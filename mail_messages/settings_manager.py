# -*- coding: utf-8 -*-
import bson
from rek.mongo.conn_manager import mongodb_connection_manager
import rek.mail_messages.messages_exceptions

class MessagesUserSettings(object):
    def __init__(self, user_id = None, messages_on_page = 25, contacts_on_page = 50,
                 only_from_contact_list = False, is_on_auto_answer = False, text_auto_answer = '', text_signature=''):

        self._id = None
        self.user_id = user_id
        self.messages_on_page = messages_on_page
        self.contacts_on_page = contacts_on_page
        self.only_from_contact_list = only_from_contact_list
        self.is_on_auto_answer = is_on_auto_answer
        self.text_auto_answer = text_auto_answer
        self.text_signature = text_signature

    def __unicode__(self):
        return self.user_id

    def save(self):
        if self._id:
            if messages_user_settings_manager.update_user_settings(self._id, self):
                result = self._id
            else:
                raise rek.mail_messages.messages_exceptions.CantSaveSettings('Can not save settings')
        else:
            result = messages_user_settings_manager.add_user_settings(self)
        return result

    def __eq__(self, other):
        if not isinstance(other, MessagesUserSettings):
            return False
        return self.user_id == other.user_id and self.messages_on_page == other.messages_on_page and \
               self._id == other._id and self.contacts_on_page == other.contacts_on_page and \
               self.only_from_contact_list == other.only_from_contact_list and self.is_on_auto_answer == other.is_on_auto_answer and \
               self.text_auto_answer == other.text_auto_answer and self.text_signature == other.text_signature


class MessagesUserSettingsManager(object):
    def __init__(self):
        dbh = mongodb_connection_manager.database
        self.collection = dbh['messages_settings']

    def user_settings_exists(self, user_id):
        return self.collection.find({'user_id':user_id}).count()


    def add_user_settings(self, user_settings):
        # Test if not allright exists user_settings
        if self.user_settings_exists(user_settings.user_id):
            raise rek.mail_messages.messages_exceptions.CantAddMessageSettings('Can add user settings. User settings already exist.')

        result = self.collection.insert({
            'user_id': user_settings.user_id,
            'messages_on_page': user_settings.messages_on_page,
            'contacts_on_page': user_settings.contacts_on_page,
            'only_from_contact_list': user_settings.only_from_contact_list,
            'is_on_auto_answer': user_settings.is_on_auto_answer,
            'text_auto_answer': user_settings.text_auto_answer,
            'text_signature': user_settings.text_signature
        })

        if isinstance(result, bson.ObjectId):
            user_settings._id = result
            return result
        else:
            raise rek.mail_messages.messages_exceptions.CantAddUserSettings('Can not add to user mail settings')

    def update_user_settings(self, id, user_settings):
        result = self.collection.update(
            { # Where
                '_id':id,
                'user_id': user_settings.user_id,
            },
            { # What
                'user_id': user_settings.user_id,
                'messages_on_page': user_settings.messages_on_page,
                'contacts_on_page': user_settings.contacts_on_page,
                'only_from_contact_list': user_settings.only_from_contact_list,
                'is_on_auto_answer': user_settings.is_on_auto_answer,
                'text_auto_answer': user_settings.text_auto_answer,
                'text_signature': user_settings.text_signature
            },
            safe = True
        )

        if 'err' and 'n' in result:
            if result['err'] is None and result['n']==1:
                return True
            else:
                return False
        else:
            raise rek.mail_messages.messages_exceptions.CantUpdateMessageSettings('Can not update message user settings')

    def _set_object(self, db_entry):
        user_settings = MessagesUserSettings(db_entry.get('user_id'), db_entry.get('messages_on_page'),
                                   db_entry.get('contacts_on_page'),db_entry.get('only_from_contact_list'),
                                   db_entry.get('is_on_auto_answer'),db_entry.get('text_auto_answer'),
                                   db_entry.get('text_signature'))

        user_settings._id = db_entry.get('_id')
        return user_settings

    def get_user_settings(self, user_id):
        db_entry = self.collection.find_one({'user_id':user_id})
        if db_entry is not None:
            return self._set_object(db_entry)
        else:
            user_settings = MessagesUserSettings(user_id = user_id)
            self.add_user_settings(user_settings)
            return self.get_user_settings(user_id)

messages_user_settings_manager = MessagesUserSettingsManager()
  