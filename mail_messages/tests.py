# -*- coding: utf-8 -*-
from unittest import TestCase
import bson
from rek.mail_messages.contacts_manager import Contact, EmployeeContact, contacts_manager
from rek.mail_messages.messages_exceptions import CantAddMessageSettings
from rek.mail_messages.messages_manager import MailMessage, messages_manager
from rek.mail_messages.settings_manager import messages_user_settings_manager, MessagesUserSettings
from rek.mongo.mongo_utils import mongodb_datetime_now
from rek.mongo.conn_manager import mongodb_connection_manager

FIRST_CONTACT_ID = bson.ObjectId()
FIRST_MESSAGE_ID = bson.ObjectId()
SECOND_MESSAGE_ID = bson.ObjectId()
FIRST_SETTINGS_ID = bson.ObjectId()

MESSAGE_DATE = mongodb_datetime_now()


class MongoTestCase(TestCase):
    def setUp(self):
        self.contacts_collection = mongodb_connection_manager.database['test_contacts']
        self.contacts_collection.insert({'_id' : FIRST_CONTACT_ID,
            'owner': 1,
            'type': Contact.TYPE_EMPLOYEE,
            'contact_data': {
                'user_name' : 'user_name',
                'user_photo' : 'user_photo',
                'company_name' : 'company_name',
                'company_code' : 'company_code',
                'position' : 'position'
            }
        })

        self.contacts_collection.insert({'_id' : bson.ObjectId(),
            'owner': 2,
            'type': Contact.TYPE_EMPLOYEE,
            'contact_data': {
                'user_name' : 'user_name',
                'user_photo' : 'user_photo',
                'company_name' : 'company_name',
                'company_code' : 'company_code',
                'position' : 'position'
            }
        })

        self.contacts_collection.insert({'_id' : bson.ObjectId(),
            'owner': 1,
            'type': Contact.TYPE_EMPLOYEE,
            'contact_data': {
                'user_name' : 'user_name',
                'user_photo' : 'user_photo',
                'company_name' : 'company_name',
                'company_code' : 'company_code',
                'position' : 'position'
            }
        })

        self.message_collection = mongodb_connection_manager.database['test_messages']

        self.message_collection.insert({'_id' : FIRST_MESSAGE_ID,
            'owner': 1,
            'text': 'test text 1',
            'company_rek':10,
            'subject': 'test subject 1',
            'folder': MailMessage.FOLDER_DRAFT,
            'headers': [{'FROM':1, 'TO':2, 'DATE':MESSAGE_DATE}],
            'attaches': [],
            'input_number': 0,
            'output_number': 0,
            'send_date': MESSAGE_DATE,
            'is_important': False,
            'is_official': False,
            'is_auto_answer': False,
            'is_read': False,
            'is_deleted': False
        })

        self.message_collection.insert({'_id' : SECOND_MESSAGE_ID,
            'owner': 333,
            'text': 'test text',
            'company_rek':11,
            'subject': 'test subject',
            'folder': MailMessage.FOLDER_DRAFT,
            'headers': [{'FROM':1, 'TO':2, 'DATE':mongodb_datetime_now()}],
            'attaches': [],
            'input_number': 0,
            'output_number': 0,
            'send_date': mongodb_datetime_now(),
            'is_important': False,
            'is_official': False,
            'is_auto_answer': False,
            'is_read': False,
            'is_deleted': False
        })

        self.message_collection.insert({'_id' : bson.ObjectId(),
            'owner': 1,
            'text': 'test text',
            'company_rek':10,
            'subject': 'test subject',
            'folder': MailMessage.FOLDER_DRAFT,
            'headers': [{'FROM':1, 'TO':2, 'DATE':mongodb_datetime_now()}],
            'attaches': [],
            'input_number': 0,
            'output_number': 0,
            'send_date': mongodb_datetime_now(),
            'is_important': False,
            'is_official': False,
            'is_auto_answer': False,
            'is_read': False,
            'is_deleted': False
        })

        self.message_settings_collection = mongodb_connection_manager.database['test_messages_settings']

        self.message_settings_collection.insert({'_id' : FIRST_SETTINGS_ID,
            'user_id': 1,
            'messages_on_page': 25,
            'contacts_on_page': 50,
            'only_from_contact_list': False,
            'is_on_auto_answer': False,
            'text_auto_answer': 'Меня нет в интернет, отвечу как появлюсь. Чаооооо!',
            'text_signature': 'С уважением, инженер Алексей В. Синявский'
        })

        self.message_settings_collection.insert({'_id' : bson.ObjectId(),
            'user_id': 2,
            'messages_on_page': 25,
            'contacts_on_page': 50,
            'only_from_contact_list': False,
            'is_on_auto_answer': False,
            'text_auto_answer': 'До 31 января не появлюсь в интернет',
            'text_signature': 'С уважением, директор Иванов Иван Иванович'
        })
                
    def tearDown(self):
        self.contacts_collection.drop()
        self.message_collection.drop()
        self.message_settings_collection.drop()

    def testSingleFind(self):
        contacts_manager.collection = mongodb_connection_manager.database['test_contacts']
        contact = contacts_manager.get_one_contact(FIRST_CONTACT_ID, 1)
        self.assertNotEqual(contact, None)

        test_contact = EmployeeContact(1, contact_data = {
            'user_name' : 'user_name',
            'user_photo' : 'user_photo',
            'company_name' : 'company_name',
            'company_code' : 'company_code',
            'position' : 'position'},

        )
        test_contact._id = FIRST_CONTACT_ID
        
        self.assertEqual(contact, test_contact)

    def testFindAll(self):
        contacts_manager.collection = mongodb_connection_manager.database['test_contacts']
        contact_list = contacts_manager.get_all_contacts(1, 10000, 0)
        self.assertNotEqual(contact_list, None)
        self.assertEqual(len([c for c in contact_list]), 2)

    def testDeleteOne(self):
        contacts_manager.collection = mongodb_connection_manager.database['test_contacts']
        contact = contacts_manager.del_contact(FIRST_CONTACT_ID, 1)
        self.assertEqual(contact, True)
        contact = contacts_manager.del_contact(FIRST_CONTACT_ID, 1)
        self.assertNotEqual(contact, True)

    def testAddOne(self):
        contact = EmployeeContact(1, contact_data = {
            'user_name' : 'user_name',
            'user_photo' : 'user_photo',
            'company_name' : 'company_name',
            'company_code' : 'company_code',
            'position' : 'position'}
        )
        contacts_manager.collection = mongodb_connection_manager.database['test_contacts']
        result = contacts_manager.add_contact(contact)
        self.assertEqual(isinstance(result, bson.ObjectId), True)

    def testUpdateOne(self):
        contact = EmployeeContact(1, contact_data = {
            'user_name' : 'user_name',
            'user_photo' : 'user_photo',
            'company_name' : 'company_name',
            'company_code' : 'company_code',
            'position' : 'position'}
        )
        contacts_manager.collection = mongodb_connection_manager.database['test_contacts']
        id_add = contacts_manager.add_contact(contact)
        if id_add:
            contact.contact_data['company_name'] = 'company_name_update'
            result = contacts_manager.update_contact(id_add, contact)
            self.assertEqual(result, True)

        contact_find = contacts_manager.get_one_contact(id_add, 1)
        self.assertEqual(contact_find.contact_data['company_name'], 'company_name_update')

    def testFindOneMessage(self):
        messages_manager.collection = mongodb_connection_manager.database['test_messages']
        message = messages_manager.get_one_message(FIRST_MESSAGE_ID, 1)
        self.assertNotEqual(message, None)
        
        test_message = MailMessage(1, 'test text 1', company_rek = 10, subject='test subject 1', send_date=MESSAGE_DATE, headers=[{'FROM':1, 'TO':2, 'DATE':MESSAGE_DATE}] ) #owner to text
        test_message._id = FIRST_MESSAGE_ID

        self.assertEqual(message, test_message)

    def testFindAllMessages(self):
        messages_manager.collection = mongodb_connection_manager.database['test_messages']
        messages_list = messages_manager.get_messages(1, 1000, 0, folder=MailMessage.FOLDER_DRAFT)
        self.assertNotEqual(messages_list, None)
        self.assertEqual(len([c for c in messages_list]), 2)

    def testAddDraftMessage(self):
        #without headers
        draft_message = MailMessage(666, 'Draft message', subject='New draft message', send_date=mongodb_datetime_now(),)
        messages_manager.collection = mongodb_connection_manager.database['test_messages']
        result = messages_manager.save_message(draft_message)
        self.assertEqual(result is not False, True)

    def testSendMessage(self):
        messages_manager.collection = mongodb_connection_manager.database['test_messages']
        draft_message = messages_manager.get_one_message(SECOND_MESSAGE_ID, 333)
        self.assertNotEqual(draft_message, None)

        draft_message.text = 'blah blah blah'
        messages_manager.send_message(draft_message, 555)

    def testAddUserSettings(self):
        user_settings = MessagesUserSettings(3)
        messages_user_settings_manager.collection = mongodb_connection_manager.database['test_messages_settings']
        result = messages_user_settings_manager.add_user_settings(user_settings)

        self.assertEqual(isinstance(result, bson.ObjectId), True)
        user_settings = MessagesUserSettings(1)
        try:
            messages_user_settings_manager.add_user_settings(user_settings)
        except CantAddMessageSettings:
            pass

    def testUpdateSettings(self):
        messages_user_settings_manager.collection = mongodb_connection_manager.database['test_messages_settings']
        user_mail_settings = messages_user_settings_manager.get_user_settings(1)
        self.assertEqual(user_mail_settings._id, FIRST_SETTINGS_ID)

        user_mail_settings.text_auto_answer='Фак ю Спилберг'
        result = user_mail_settings.save()
        self.assertEqual(isinstance(result, bson.ObjectId), True)
    