# -*- coding: utf-8 -*-
import bson
import pymongo
from rek.mongo.conn_manager import mongodb_connection_manager
import rek.mail_messages.messages_exceptions

class Contact(object):
    TYPE_UNKNOWN = bson.ObjectId('4f2bd7ca272ca6e8ada3ab46')
    TYPE_EMPLOYEE = bson.ObjectId('4f2bd805d7ab438ddeedbe47')
    TYPE_COMPANY = bson.ObjectId('4f2bd805d7ab438ddeedbe48')
    TYPE_EMAIL = bson.ObjectId('4f2bd805d7ab438ddeedbe49')

    def __init__(self, owner = 0):
        self._id = None
        self.owner = owner
        self.contact_data = {}

    def __unicode__(self):
        return self.owner

    def save(self):
        if self._id:
            if contacts_manager.update_contact(self._id, self):
                result = self._id
            else:
                raise rek.mail_messages.messages_exceptions.CantSaveContact('Can not save contact')
        else:
            result = contacts_manager.add_contact(self)
        return result

    def drop(self):
        return contacts_manager.del_contact(self._id, self.owner)

class EmployeeContact(Contact):
    def _get_type(self):
        return Contact.TYPE_EMPLOYEE
    type = property(_get_type)

    def __init__(self, owner, contact_data):
        super(EmployeeContact, self).__init__(owner)
        if self.contact_data is not None:
            self.contact_data = dict.copy(contact_data)

    def __eq__(self, other):
        if not isinstance(other, EmployeeContact):
            return False
        return self.owner == other.owner and self.contact_data == other.contact_data and self._id == other._id

class CompanyContact(Contact):
    def _get_type(self):
        return Contact.TYPE_COMPANY
    type = property(_get_type)

    def __init__(self, owner, contact_data):
        super(CompanyContact, self).__init__(owner)
        self.contact_data = dict.copy(contact_data)

    def __eq__(self, other):
        if not isinstance(other, CompanyContact):
            return False
        return self.owner == other.owner and self.contact_data == other.contact_data and self._id == other._id

class EmailContact(Contact):
    def _get_type(self):
        return Contact.TYPE_EMAIL
    type = property(_get_type)

    def __init__(self, owner, contact_data):
        super(EmailContact, self).__init__(owner)
        self.contact_data['email'] = contact_data['email']

    def __eq__(self, other):
        if not isinstance(other, EmailContact):
            return False
        return self.owner == other.owner and self.contact_data == other.contact_data and self._id == other._id


class ContactsManager(object):
    def __init__(self):
        dbh = mongodb_connection_manager.database
        self.collection = dbh['contacts']

    def del_contact(self, _id, owner):
        result = self.collection.remove({'_id':_id, 'owner':owner}, safe=True)
        if 'err' and 'n' in result:
            if result['err'] is None and result['n']==1:
                return True
            else:
                return False
        else:
            raise rek.mail_messages.messages_exceptions.CantDeleteOneContact('Can not delete one contact')

    def add_contact(self, mail_contact):
        result = self.collection.insert({
            'owner': mail_contact.owner,
            'type': mail_contact.type,
            'contact_data': mail_contact.contact_data
        })
        if isinstance(result, bson.ObjectId):
            mail_contact._id = result
            return result
        else:
            raise rek.mail_messages.messages_exceptions.CantAddOneContact('Can add new contact')

    def update_contact(self, id, mail_contact):

        result = self.collection.update(
            { # Where
                '_id': id,
                'owner':mail_contact.owner
            },
            { # What
                'owner': mail_contact.owner,
                'type': mail_contact.type,
                'contact_data': mail_contact.contact_data
            },
            safe=True
        )

        if 'err' and 'n' in result:
            if result['err'] is None and result['n']==1:
                return True
            else:
                return False
        else:
            raise rek.mail_messages.messages_exceptions.CantUpdateOneContact('Can not update one contact')

    def _set_object(self, db_entry):
        type = db_entry.get('type')

        if type == Contact.TYPE_EMPLOYEE:
            mail_contact = EmployeeContact(db_entry.get('owner'),db_entry.get('contact_data'))
        elif type == Contact.TYPE_COMPANY:
            mail_contact = CompanyContact(db_entry.get('owner'),db_entry.get('contact_data'))
        elif type == Contact.TYPE_EMAIL:
            mail_contact = EmailContact(db_entry.get('owner'),db_entry.get('contact_data'))
        else:
            raise rek.mail_messages.messages_exceptions.ContactTypeDoesNotExistException("Don't return contact with this type %s" % str(type))

        mail_contact._id = db_entry.get('_id')
        return mail_contact

    def get_one_contact(self, _id, owner):
        db_entry = self.collection.find_one({'_id':_id,'owner':owner})
        if db_entry is not None:
            return self._set_object(db_entry)
        else:
            raise rek.mail_messages.messages_exceptions.CantFindOneContact('Can not find one contact')

    def get_all_contacts(self, owner, limit, skip, sort = 'contact_data["name"]', sort_order = 'ASC'): #skip == mongodb offset
        #return cursor
        sort_type = pymongo.ASCENDING if sort_order == 'ASC' else pymongo.DESCENDING
        contact_cursor = self.collection.find({'owner':owner}).sort(sort, sort_type).limit(limit).skip(skip)
        
        for contact in contact_cursor:
            yield self._set_object(contact)

contacts_manager = ContactsManager()