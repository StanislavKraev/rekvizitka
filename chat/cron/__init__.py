# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import memcache

import sys
from bson.code import Code
from django.template.loader import render_to_string

from rek import settings
from rek.chat_tornadio.operation_notifier import OperationTypeEnum, Operation
from rek.chat_tornadio.utils import get_cts, cts_from_timedelta

from rek.cron.cron_task import CronTaskBase
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.mango.auth import User
from rek.rekvizitka.models import CompanyEmployee
from rek.rekvizitka.utils import is_valid_email

# todo: run this task every 10-30 minutes, not every minute
from rek.mongo.conn_manager import mongodb_connection_manager

mem_cache = memcache.Client(['127.0.0.1:11211'])

filter_func = Code("function (opList) {                                                         "
                   "  var hasMessage = false;                                                   "
                   "  if (!opList.length) { return false; }                                     "
                   "  if (opList.length === 1) {                                                "
                   "    return opList[0].op === 2;                                              "
                   "  }                                                                         "
                   "  opList.sort(function(opA, opB) {                                          "
                   "    hasMessage |= (opA.op === 2) || (opB.op === 2);                         "
                   "    return opA.ts - opB.ts;                                                 "
                   "  });                                                                       "
                   "  if (!hasMessage) { return false;}                                         "
                   "  return opList[opList.length - 1].op === 2;                                "
                   "}")

mongodb_connection_manager.database.system_js.check_unsent = filter_func

class UnreadDialogNotificationTask(CronTaskBase):
    map =   unicode("function () {"
                    "  var that = this;"
                    "  if (this.operation_type === 3) {                                                 "
                    "    if (this.owner) {                                                              " # online
                    "      emit({owner:this.owner, op:that.operation_type}, {ts : that.timestamp});     "
                    "    }                                                                              "
                    "    return;                                                                        "
                    "  }                                                                                "
                    "  this.listeners.forEach(function(listener) {                                      "
                    "    if ((that.operation_type === 2)) {                                             " # new message
                    "      if (that.timestamp > %(ts)d) { return; }                                     "
                    "      if (listener.equals(that.owner)) { return; }                                 "
                    "    }                                                                              "
                    "    emit({owner:listener, op:that.operation_type},                                 "
                    "         {ts: that.timestamp});                                                    "
                    "  });                                                                              "
                    "}")
    reduce   = Code("function (key, values) {                                                       "
                    "    var result = 0;                                                            "
                    "    values.forEach(function (value) {if (value.ts > result) {                  "
                    "        result = value.ts;                                                     "
                    "    }});                                                                       "
                    "    return {ts : result};                                                      "
                    "}")

    map2 =  Code("function () {                                                                     "
                 "  emit(this._id.owner, {list:[{op:this._id.op, ts:this.value.ts}]});              "
                 "}")
    reduce2 = Code("function (key, values) {                                                        "
                   "  var result = {list:[]};                                                       "
                   "  values.forEach(function(value) {                                              "
                   "    result.list = result.list.concat(value.list);                               "
                   "  });                                                                           "
                   "  return result;                                                                "
                   "}")

    def make_employee_op_collection(self, ts, ts_min):
        map =  Code(self.map % {'ts' : ts})

        result = Operation.objects.collection.map_reduce(map, self.reduce, "chat_dialog_mr_udn",
            query={"operation_type": {"$in": [OperationTypeEnum.OT_NEW_MESSAGE,
                                              OperationTypeEnum.OT_STATUS_CHANGE,
                                              OperationTypeEnum.OT_EMAIL_SENT]},
                   "timestamp" : {"$gt" : ts_min}}, full_response = True)
        return result

    def make_employee_last_ops(self):
        return mongodb_connection_manager.database['chat_dialog_mr_udn'].map_reduce(self.map2, self.reduce2, "chat_dialog_mr_udn2", full_response = True)

    def find_unsent_messages(self):
        return mongodb_connection_manager.database['chat_dialog_mr_udn2'].find({'$where': 'check_unsent(this.value.list)'})

    def get_employee_email(self, employee_id):
        employee = CompanyEmployee.objects.get_one(employee_id)
        if not employee:
            return None

        user = User.collection.find_one(employee.user_id)
        return user['email'] if user else None

    def execute(self):
        print >> sys.stdout, '%s Executing UnreadDialogNotificationTask' % unicode(datetime.now())

        search_ts = get_cts() - cts_from_timedelta(timedelta(hours = 3))
        ts_min = search_ts - cts_from_timedelta(timedelta(days = 3))
        result = self.make_employee_op_collection(search_ts, ts_min)
        if result['ok'] != 1:
            print >> sys.stderr, u'Failed to perform map_reduce during checking unread messages: %s' % repr(result)
            return

        result = self.make_employee_last_ops()
        if result['ok'] != 1:
            print >> sys.stderr, u'Failed to perform map_reduce step 2 during checking unread messages: %s' % repr(result)
            return

        unread_dialogs_cursor = self.find_unsent_messages()

        for unread_data in unread_dialogs_cursor:
            try:
                employee = unread_data['_id']
                if self.is_online(employee):
                    mark_as_sent = Operation({'owner' : employee,
                                              'operation_type' : OperationTypeEnum.OT_EMAIL_SENT,
                                              'data' : {'fake' : True},
                                              'listeners' : [employee],
                                              'is_service' : True})
                    mark_as_sent.save()
                    continue
                email = self.get_employee_email(employee)

                if not email or not is_valid_email(email):
                    continue

                action = create_action_id(actions.UNREAD_DIALOGS, employee)
                subj = u'Непрочитанные сообщения в Реквизитке'

                data = {'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}
                text = render_to_string('mail/chat/unread_dialogs.txt', data)
                html = render_to_string('mail/chat/unread_dialogs.html', data)

                notification_manager.remove(action)
                notification_manager.add(action, email, subj, text, html, settings.UNREAD_MESSAGE_EMAIL_NOTIFY_TIMEOUT)
                mark_as_sent = Operation({'owner' : employee,
                                          'operation_type' : OperationTypeEnum.OT_EMAIL_SENT,
                                          'data' : {},
                                          'listeners' : [employee],
                                          'is_service' : True})
                mark_as_sent.save()
            except Exception:
                pass

    def is_online(self, employee):
        return mem_cache.get('on-%s' % str(employee)) == 1
