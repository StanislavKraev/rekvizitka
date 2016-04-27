# -*- coding: utf-8 -*-
from datetime import datetime
import sys, os

os.environ['DJANGO_SETTINGS_MODULE'] = 'rek.settings'
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../third_party/'))

import tornadio2
from tornadio2 import proto
from bson.objectid import ObjectId
from tornadio2.conn import event
from tornado import ioloop
from tornado.web import Application as WebApplication
import memcache
import logging

from rek.utils import tornado_auth
from rek.chat.models import ChatDialog, DialogMessage
from rek.chat_tornadio.utils import get_cts
from rek.chat_tornadio.operation_notifier import OperationNotifier, OperationTypeEnum, Operation

#from pydev import pydevd
#pydevd.settrace('127.0.0.1', port=33321, stdoutToServer=True, stderrToServer=True, suspend=False)

mem_cache = memcache.Client(['127.0.0.1:11211'])

class FakeRequest(object):
    def __init__(self, request, cookies, path):
        self.request = request
        self.cookies = cookies
        self.method = 'GET'
        self.path = path

class ChatConnection(tornadio2.SocketConnection):
    def notify_online(self, employee):
        self.notify_status_change(employee, online = True)
        mem_cache.set('on-%s' % str(employee._id), 1, 0)

    def notify_offline(self, employee):
        self.notify_status_change(employee, online = False)
        mem_cache.delete('on-%s' % str(employee._id))

    def notify_status_change(self, employee, online = False):
        operation = Operation({'owner' : employee._id,
                               'operation_type' : OperationTypeEnum.OT_STATUS_CHANGE,
                               'data' : {'employee' : unicode(employee._id),
                                         'online' : online},
                               'listeners' : OperationNotifier.active_dialog_connections(employee._id)})

        operation.save()

        server_cts = get_cts()
        self.client_cts = server_cts
        OperationNotifier.notify(operation, self.client_cts)

    def on_open(self, request):
        if self.session.session_id not in OperationNotifier.sessions:
            return False
        logging.debug('ChatConnection::on_open. session_id: %s' % unicode(self.session.session_id))
        user, company, employee, client_cts = OperationNotifier.sessions[self.session.session_id]
        if employee._id not in OperationNotifier.connections:
            OperationNotifier.connections[employee._id] = [self]
            OperationNotifier.on_employee_online(employee._id)
            self.notify_online(employee)
        else:
            OperationNotifier.connections[employee._id].append(self)
        mem_cache.set('on-%s' % str(employee._id), 1, 0)
        self.company = company
        self.employee = employee
        self.user = user
        self.client_cts = client_cts
        self.connection_date = datetime.now()

        self.tailable_cursor = Operation.objects.collection.find({'listeners' : employee._id,
                                                                  'is_service' : False,
                                                                  'timestamp' : {'$gt' : self.client_cts}}, tailable=True)

        op_list = self.get_missed_ops(self.client_cts)
        if len(op_list):
            server_cts = get_cts()
            self.client_cts = server_cts
            self.emit('operations', {'ops' : op_list,
                                     'new_cts' : server_cts})

    @event('check_dialog_viewed')
    def on_check_dialog_viewed(self, **data):
        my_employee = self.employee
        try:
            dialog_id = data.get('dialog_id')
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'parties' : my_employee._id})
            if not dialog:
                raise Exception('No such dialog')
        except Exception:
            self.emit('check_as_viewed', {'error' : True})
            return
        ChatDialog.objects.collection.update({'_id' : dialog._id},
                                             {'$pull' : {'not_viewed_by_parties' : my_employee._id}})

        operation = Operation({'owner' : my_employee._id,
                               'operation_type' : OperationTypeEnum.OT_MARK_READ,
                               'data' : {'dialog' : dialog_id},
                               'listeners' : [my_employee._id]})
        operation.save()
        server_cts = get_cts()
        self.client_cts = server_cts
        OperationNotifier.notify(operation, self.client_cts)

    @event('add_dlg_msg')
    def on_add_dlg_msg(self, **data):
        my_employee = self.employee
        try:
            text = data.get('text').strip()
            dialog_id = data.get('dialog_id')
            if not len(text):
                raise Exception('Missing required parameter "text"')
                # todo: asyncmongo
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'parties' : my_employee._id})
            if not dialog:
                raise Exception('No such dialog')
        except Exception:
            self.emit('error', {'msg' : u'Не удалось отправить сообщение'})
            return

        new_message = DialogMessage({'dialog' : dialog._id,
                                     'text' : text,
                                     'creator' : my_employee._id})
        new_message.save()
        employee_tz = my_employee.get_tz()
        ChatDialog.objects.collection.update({'_id' : dialog._id}, {'$set' : {
            'last_message_date' : new_message.date,
            'last_message_text' : new_message.text[:200],
            'last_message_party' : self.employee._id,
            'last_message_id' : new_message._id,
            'hidden_by_parties' : [],
            'not_viewed_by_parties' : dialog.parties
        }})

        operation = Operation({'owner' : my_employee._id,
                               'operation_type' : OperationTypeEnum.OT_NEW_MESSAGE,
                               'data' : {'dialog' : dialog_id,
                                         'text' : new_message.text,
                                         'date' : new_message.date.astimezone(employee_tz).isoformat(),
                                         'author' : unicode(my_employee._id),
                                         'message_id' : unicode(new_message._id)},
                               'listeners' : dialog.parties})
        operation.save()
        server_cts = get_cts()
        self.client_cts = server_cts
        OperationNotifier.notify(operation, self.client_cts)

    def on_close(self):
        logging.debug('ChatConnection::on_close. session_id: %s' % unicode(self.session.session_id))
        logging.debug('OperationNotifier::connections (start): %s' % unicode(OperationNotifier.connections))
        self.tailable_cursor = None
        conn_list = OperationNotifier.connections.get(self.employee._id, [])
        try:
            conn_list.remove(self)
            if not len(conn_list):
                del OperationNotifier.connections[self.employee._id]
                self.notify_offline(self.employee)
                OperationNotifier.on_employee_offline(self.employee._id)
        except Exception, ex:
            logging.warning('exception: %s' % unicode(ex.message))
        logging.debug('OperationNotifier::connections (finish): %s' % unicode(OperationNotifier.connections))

    def get_missed_ops(self, last_ts):
        data_list = []
        while self.tailable_cursor.alive:
            try:
                operation = self.tailable_cursor.next()
                if operation['timestamp'] <= last_ts:
                    continue
                data = {'operation_type' : operation['operation_type']}
                data.update(operation['data'])
                data_list.append(data)
            except StopIteration:
                break

        return data_list

    def on_refresh_connection(self, endpoint_name):
        logging.debug('* * * Refresh connection')
        data_list = self.get_missed_ops(self.client_cts)

        if len(data_list):
            logging.debug('* * * %i new operations:' % len(data_list))
            for op in data_list:
                logging.debug(repr(op))
            # dirty hack
            server_cts = get_cts()
            self.client_cts = server_cts
            msg = proto.event(endpoint_name, 'operations', None, {'ops' : data_list, 'new_cts' : server_cts})
            self.session.send_queue.append(msg)
            return True

        cur_date = datetime.now()
        dt = cur_date - self.connection_date
        if dt.seconds / 3600.0 > 2:
            return False

        return True

class MyConnection(tornadio2.SocketConnection):
    __endpoints__ = {'/dchat' : ChatConnection}

    def on_open(self, request):
        logging.debug('MyConnection::on_open. session_id: %s' % unicode(self.session.session_id))
        session_cookie = request.get_cookie('sessionid')
        csrf_cookie = request.get_cookie('csrftoken')
        if not session_cookie or not csrf_cookie:
            return False
        session_id = session_cookie.value
        csrf_key = csrf_cookie.value
        fake_request = FakeRequest(request, request.cookies, '/dchat/1/')

        # todo: asyncmongo
        user, company, employee = tornado_auth.get_authorized_parameters(csrf_key, session_id, fake_request)

        if not user or not employee:
            return False

        try:
            client_cts_str = request.cookies['cts'].value
            client_cts = int(client_cts_str)
            logging.debug('client_cts : %s' % str(client_cts))
        except Exception:
            client_cts = 0
            logging.debug('client_cts : %s' % str(client_cts))

        OperationNotifier.sessions[self.session.session_id] = (user, company, employee, client_cts)

    def on_close(self):
        logging.debug('MyConnection::on_close. session_id: %s' % unicode(self.session.session_id))
        if self.session.session_id in OperationNotifier.sessions:
            del OperationNotifier.sessions[self.session.session_id]

MyRouter = tornadio2.TornadioRouter(MyConnection, namespace='dchat',
    user_settings={'enabled_protocols': [
#        'websocket',
        'xhr-polling',
        'flashsocket',
        'xhr-multipart',
], 'xhr_polling_timeout' : 30,
'heartbeat_interval': 25}
)

application = WebApplication(
    MyRouter.urls,
    socket_io_port = 8086)

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    tornadio2.server.SocketServer(application, auto_start=False)
    ioloop.IOLoop.instance().start()

