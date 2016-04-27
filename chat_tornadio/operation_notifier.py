# -*- coding: utf-8 -*-
import logging
from rek.chat.models import ChatDialog
from rek.chat_tornadio.utils import get_cts
from rek.mongo.models import SimpleModel, ObjectManager

class OperationTypeEnum(object):
    OT_INVALID = 0
    OT_REMOVE_DIALOG = 1
    OT_NEW_MESSAGE = 2
    OT_STATUS_CHANGE = 3

    OT_MARK_READ = 5

    OT_EMAIL_SENT = 100

class Operation(SimpleModel):
    __capped__ = True
    __capped_size__ = 1024 * 1024 * 200
    __capped_max__ = 100000
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.owner = kwargs.get('owner') # employee id
        self.operation_type = kwargs.get('operation_type')
        self.data = kwargs.get('data')
        self.timestamp = kwargs.get('timestamp')
        self.listeners = kwargs.get('listeners', []) # employees ids
        self.is_service = kwargs.get('is_service', False)

    def save(self):
        self.timestamp = get_cts()
        return super(Operation, self).save()

    def _fields(self):
        fields = {
            'operation_type' : self.operation_type,
            'data' : self.data,
            'timestamp' : self.timestamp,
            'listeners' : self.listeners,
            'owner' : self.owner,
            'is_service' : self.is_service
        }
        return fields

Operation.objects = ObjectManager(Operation, 'operation', [('timestamp', 1)])

class OperationNotifier(object):
    sessions = {}
    connections = {}
    employee_dlg_connections = {} # employee -> employee list

    @classmethod
    def notify(cls, operation, cur_ts):
        operation_type = operation.operation_type

        for listener in operation.listeners:
            connection_list = cls.connections.get(listener, [])

            for connection in connection_list:
                if connection:
                    data = {'operation_type' : operation_type, 'new_cts' : cur_ts}
                    data.update(operation.data)
                    connection.emit('operation', data)

    @classmethod
    def on_employee_online(cls, employee_id):
        logging.debug('OperationNotifier::on_employee_online. employee_id: %s' % unicode(employee_id))
        logging.debug('OperationNotifier::employee_dlg_connections (start): %s' % unicode(cls.employee_dlg_connections))
        connected_employees = cls._get_dialog_connections(employee_id)
        for connected_employee in connected_employees:
            if connected_employee not in cls.employee_dlg_connections:
                cls.employee_dlg_connections[connected_employee] = set([employee_id])
            else:
                cls.employee_dlg_connections[connected_employee].add(employee_id)
        logging.debug('OperationNotifier::employee_dlg_connections (finish): %s' % unicode(cls.employee_dlg_connections))

    @classmethod
    def on_employee_offline(cls, employee_id):
        logging.debug('OperationNotifier::on_employee_offline. employee_id: %s' % unicode(employee_id))
        logging.debug('OperationNotifier::employee_dlg_connections (start): %s' % unicode(cls.employee_dlg_connections))
        connected_employees = cls._get_dialog_connections(employee_id)
        for connected_employee in connected_employees:
            if connected_employee in cls.employee_dlg_connections:
                cur_set = cls.employee_dlg_connections[connected_employee]
                cur_set.discard(employee_id)
                if len(cur_set):
                    del cls.employee_dlg_connections[connected_employee]
        logging.debug('OperationNotifier::employee_dlg_connections (finish): %s' % unicode(cls.employee_dlg_connections))

    @classmethod
    def _get_dialog_connections(cls, employee_id):
        employee_dialogs = ChatDialog.objects.get({'parties' : employee_id})
        dlg_connections = set()
        for dialog in employee_dialogs:
            dialog_parties = dialog.parties
            dlg_connections.update(dialog_parties)
        try:
            dlg_connections.remove(employee_id)
        except KeyError:
            pass
        return dlg_connections

    @classmethod
    def active_dialog_connections(cls, employee_id):
        return list(cls.employee_dlg_connections.get(employee_id, []))