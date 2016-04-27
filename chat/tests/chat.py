# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
import time
from rek.chat.cron import UnreadDialogNotificationTask
from rek.chat_tornadio.operation_notifier import Operation, OperationTypeEnum
from rek.chat_tornadio.utils import get_cts
from rek.mongo.conn_manager import mongodb_connection_manager

from rek.tests.base import BaseTestCase

DELAY = 0.01

class ChatTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions',
                        'user_activation_links', 'dialog_message', 'chat_dialog', 'operation', 'chat_dialog_mr_udn',
                        'chat_dialog_mr_udn2']

    def setUp(self):
        super(ChatTestCase, self).setUp()
        self.e1 = ObjectId()
        self.e2 = ObjectId()
        self.e3 = ObjectId()

    def test_first_mr(self):
        om1 = Operation({'owner' : self.e2,
                         'operation_type' : OperationTypeEnum.OT_NEW_MESSAGE,
                         'data' : {'dialog' : ObjectId(),
                                   'text' : 'first',
                                   'email' : 'email1'},
                         'listeners' : [self.e1, self.e2]})
        om1.save()

        oo1 = Operation({'owner' : self.e1,
                         'operation_type' : OperationTypeEnum.OT_STATUS_CHANGE,
                         'data' : {'online' : True},
                         'listeners' : [self.e2, self.e3]})
        oo1.save()

        task = UnreadDialogNotificationTask()
        task.make_employee_op_collection(get_cts() + 100000, 0)

        all_eo_items = mongodb_connection_manager.database['chat_dialog_mr_udn'].find().sort([('value.ts', 1)])
        items = [item for item in all_eo_items]
        self.assertEqual(all_eo_items.count(), 2)

        test_m1 = items[0]
        test_o1 = items[1]

        self.assertIn('_id', test_m1)
        self.assertIn('_id', test_o1)

        self.assertIn('value', test_m1)
        self.assertIn('value', test_o1)

        m1_key = test_m1['_id']
        o1_key = test_o1['_id']

        self.assertIn('owner', m1_key)
        self.assertIn('owner', o1_key)

        self.assertEqual(m1_key['owner'], self.e1)
        self.assertEqual(o1_key['owner'], self.e1)

        self.assertIn('op', m1_key)
        self.assertIn('op', o1_key)

        self.assertEqual(m1_key['op'], 2)
        self.assertEqual(o1_key['op'], 3)

        m1_value = test_m1['value']
        o1_value = test_o1['value']

        self.assertIn('ts', m1_value)
        self.assertIn('ts', o1_value)

    def send_message(self, sender, receiver):
        om1 = Operation({'owner' : sender,
                         'operation_type' : OperationTypeEnum.OT_NEW_MESSAGE,
                         'data' : {'dialog' : ObjectId(),
                                   'text' : 'first'},
                         'listeners' : [receiver, sender]})
        om1.save()
        time.sleep(DELAY)
        return om1

    def send_online(self, e1, listeners):
        o = Operation({'owner' : e1,
                   'operation_type' : OperationTypeEnum.OT_STATUS_CHANGE,
                   'data' : {'online' : True},
                   'listeners' : listeners})
        o.save()
        time.sleep(DELAY)
        return o

    def send_email(self, e1):
        oe = Operation({'owner' : e1,
                        'operation_type' : OperationTypeEnum.OT_EMAIL_SENT,
                        'data' : {},
                        'listeners' : [e1],
                        'is_service' : True})
        oe.save()
        time.sleep(DELAY)
        return oe

    def test_first_mr_many(self):
        self.send_online(self.e1, [self.e2, self.e3])
        self.send_message(self.e1, self.e2)

        self.send_online(self.e2, [self.e1, self.e3])
        self.send_message(self.e2, self.e1)
        self.send_message(self.e2, self.e1)
        self.send_message(self.e1, self.e2)
        self.send_message(self.e1, self.e3)
        self.send_online(self.e3, [self.e1, self.e2])
        self.send_message(self.e3, self.e1)

        task = UnreadDialogNotificationTask()
        task.make_employee_op_collection(get_cts() + 100000, 0)

        all_eo_items = mongodb_connection_manager.database['chat_dialog_mr_udn'].find().sort([('value.ts', 1)])
        self.assertEqual(all_eo_items.count(), 6)

    def test_first_mr_after_ts(self):
        self.send_online(self.e1, [self.e2, self.e3])
        self.send_message(self.e1, self.e2)

        self.send_online(self.e2, [self.e1, self.e3])
        self.send_message(self.e2, self.e1)
        ts = self.send_message(self.e2, self.e1).timestamp
        self.send_message(self.e1, self.e2)
        self.send_message(self.e1, self.e3)
        self.send_online(self.e3, [self.e1, self.e2])
        self.send_message(self.e3, self.e1)

        task = UnreadDialogNotificationTask()
        task.make_employee_op_collection(get_cts() + 100000, ts)

        all_eo_items = mongodb_connection_manager.database['chat_dialog_mr_udn'].find().sort([('value.ts', 1)])
        self.assertEqual(all_eo_items.count(), 4)

    def test_first_mr_must_send(self):
        self.send_online(self.e1, [self.e2, self.e3]) # A       3
        self.send_message(self.e1, self.e2)           # -

        self.send_online(self.e2, [self.e1, self.e3]) # B       3
        self.send_message(self.e2, self.e1)           # -
        self.send_message(self.e2, self.e1)           # C       2
        op = self.send_message(self.e1, self.e2)      # D       2
        ts = op.timestamp                             # ts = D.ts

        self.send_message(self.e1, self.e3)           # -
        self.send_online(self.e3, [self.e1, self.e2]) # E
        self.send_message(self.e3, self.e1)           # -

        task = UnreadDialogNotificationTask()
        task.make_employee_op_collection(ts, 0)

        all_eo_items = mongodb_connection_manager.database['chat_dialog_mr_udn'].find().sort([('value.ts', 1)])
        self.assertEqual(all_eo_items.count(), 5)
        items = [item for item in all_eo_items]

        self.assertEqual(items[0]['_id']['op'], 3)
        self.assertEqual(items[0]['_id']['owner'], self.e1)

        self.assertEqual(items[1]['_id']['op'], 3)
        self.assertEqual(items[1]['_id']['owner'], self.e2)

        self.assertEqual(items[2]['_id']['op'], 2)
        self.assertEqual(items[2]['_id']['owner'], self.e1)

        self.assertEqual(items[3]['_id']['op'], 2)
        self.assertEqual(items[3]['_id']['owner'], self.e2)

        self.assertEqual(items[4]['_id']['op'], 3)
        self.assertEqual(items[4]['_id']['owner'], self.e3)

    def test_first_mr_email_sent(self):
        self.send_online(self.e1, [self.e2, self.e3]) # A       3
        self.send_message(self.e1, self.e2)           # -

        self.send_online(self.e2, [self.e1, self.e3]) # B       3
        self.send_message(self.e2, self.e1)           # -
        self.send_message(self.e2, self.e1)           # C       2
        op = self.send_message(self.e1, self.e2)      # D       2
        ts = op.timestamp                             # ts = D.ts

        self.send_message(self.e1, self.e3)           # -
        self.send_online(self.e3, [self.e1, self.e2]) # E
        self.send_email(self.e3)                      # F
        self.send_message(self.e3, self.e1)           # -

        task = UnreadDialogNotificationTask()
        task.make_employee_op_collection(ts, 0)

        all_eo_items = mongodb_connection_manager.database['chat_dialog_mr_udn'].find().sort([('value.ts', 1)])
        self.assertEqual(all_eo_items.count(), 6)
        items = [item for item in all_eo_items]

        self.assertEqual(items[0]['_id']['op'], 3)
        self.assertEqual(items[0]['_id']['owner'], self.e1)

        self.assertEqual(items[1]['_id']['op'], 3)
        self.assertEqual(items[1]['_id']['owner'], self.e2)

        self.assertEqual(items[2]['_id']['op'], 2)
        self.assertEqual(items[2]['_id']['owner'], self.e1)

        self.assertEqual(items[3]['_id']['op'], 2)
        self.assertEqual(items[3]['_id']['owner'], self.e2)

        self.assertEqual(items[4]['_id']['op'], 3)
        self.assertEqual(items[4]['_id']['owner'], self.e3)

        self.assertEqual(items[5]['_id']['op'], 100)
        self.assertEqual(items[5]['_id']['owner'], self.e3)

    def udn_received_message(self, e1, ts):
        col = mongodb_connection_manager.database['chat_dialog_mr_udn']
        col.insert({'_id' : {'owner' : e1, 'op' : 2}, 'value' : {'ts' : ts, 'email' : 'some_email'}})

    def udn_gone_online(self, e1, ts):
        col = mongodb_connection_manager.database['chat_dialog_mr_udn']
        col.insert({'_id' : {'owner' : e1, 'op' : 3}, 'value' : {'ts' : ts, 'email' : ''}})

    def udn_service_msg(self, e1, ts):
        col = mongodb_connection_manager.database['chat_dialog_mr_udn']
        col.insert({'_id' : {'owner' : e1, 'op' : 100}, 'value' : {'ts' : ts, 'email' : ''}})

    def test_second_mr_collect_1_2_3(self):
        self.udn_gone_online(self.e1, 5)

        self.udn_gone_online(self.e2, 10)
        self.udn_received_message(self.e2, 20)

        self.udn_gone_online(self.e3, 15)
        self.udn_received_message(self.e3, 25)
        self.udn_service_msg(self.e3, 40)

        task = UnreadDialogNotificationTask()
        task.make_employee_last_ops()

        all_list_items = mongodb_connection_manager.database['chat_dialog_mr_udn2'].find()
        self.assertEqual(all_list_items.count(), 3)
        items = [item for item in all_list_items]

        item1 = items[0]
        item2 = items[1]
        item3 = items[2]

        self.assertEqual(item1['_id'], self.e1)
        self.assertEqual(item2['_id'], self.e2)
        self.assertEqual(item3['_id'], self.e3)

        self.assertIn('list', item1['value'])
        self.assertIn('list', item2['value'])
        self.assertIn('list', item3['value'])

        list1 = item1['value']['list']
        list2 = item2['value']['list']
        list3 = item3['value']['list']

        self.assertEqual(len(list1), 1)
        self.assertEqual(len(list2), 2)
        self.assertEqual(len(list3), 3)

    def test_query_no_items(self):
        self.udn_gone_online(self.e1, 5)

        self.udn_received_message(self.e2, 10)
        self.udn_gone_online(self.e2, 20)

        self.udn_gone_online(self.e3, 15)
        self.udn_received_message(self.e3, 25)
        self.udn_service_msg(self.e3, 40)

        task = UnreadDialogNotificationTask()
        task.make_employee_last_ops()
        unsent = task.find_unsent_messages()
        self.assertEqual(unsent.count(), 0)

    def test_query_1_item(self):
        self.udn_gone_online(self.e1, 5)

        self.udn_gone_online(self.e2, 10)
        self.udn_received_message(self.e2, 20)

        self.udn_gone_online(self.e3, 15)
        self.udn_received_message(self.e3, 25)
        self.udn_service_msg(self.e3, 40)

        task = UnreadDialogNotificationTask()
        task.make_employee_last_ops()
        unsent = task.find_unsent_messages()
        self.assertEqual(unsent.count(), 1)

    def test_query_2_items(self):
        self.udn_gone_online(self.e1, 5)

        self.udn_gone_online(self.e2, 10)
        self.udn_received_message(self.e2, 20)

        self.udn_gone_online(self.e3, 15)
        self.udn_service_msg(self.e3, 21)
        self.udn_received_message(self.e3, 25)

        task = UnreadDialogNotificationTask()
        task.make_employee_last_ops()
        unsent = task.find_unsent_messages()
        self.assertEqual(unsent.count(), 2)
