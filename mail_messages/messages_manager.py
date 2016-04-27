# -*- coding: utf-8 -*-
import bson
import pymongo
from rek.mongo.mongo_utils import mongodb_datetime_now
from rek.mongo.conn_manager import mongodb_connection_manager
import rek.mail_messages.messages_exceptions

class MailMessage(object):
    FOLDER_INBOX = bson.ObjectId('4f168258e6cdaf1620000000')
    FOLDER_SENT = bson.ObjectId('4f16826ce6cdaf1620000001')
    FOLDER_SPAM = bson.ObjectId('4f16826ce6cdaf1620000002')
    FOLDER_DRAFT = bson.ObjectId('4f16826ce6cdaf1620000003')
    #Warning! This-deleted folder is not folder! Only for client side
    FOLDER_DELETED = bson.ObjectId('4f16826ce6cdaf1620000004')


    def __init__(self, owner, text, company_rek='', subject='Без темы', folder=FOLDER_DRAFT, headers=None, attaches=None,
                 input_number=0, output_number=0, send_date=mongodb_datetime_now(), is_important=False, is_official=False,
                 is_auto_answer=False, is_read=False, is_deleted=False):

        attaches = attaches or list() #Attache name, attache_id, attache size ...

        headers = headers or [{'FROM': owner,'TO': '','DATE': send_date}] #FROM: TO:

        self._id = None
        self.owner = owner
        # FROM USER COMPANY if user has many companies - REK
        self.company_rek = company_rek
        self.text = text
        self.subject = subject
        self.folder = folder
        self.headers = headers
        self.attaches = attaches
        self.input_number = input_number
        self.output_number = output_number
        self.send_date = send_date
        self.is_important = is_important
        self.is_official = is_official
        self.is_auto_answer = is_auto_answer
        self.is_read = is_read
        self.is_deleted = is_deleted


    def __eq__(self, other):
        if not isinstance(other, MailMessage):
            return False
        return self.owner == other.owner and self.company_rek == other.company_rek and self.text == other.text and self.folder == other.folder \
            and self._id == other._id and  self.headers == other.headers and self.attaches == other.attaches \
            and self.input_number == other.output_number and self.send_date == other.send_date and self.is_important == other.is_important \
            and self.is_official == other.is_official and self.is_auto_answer == other.is_auto_answer and self.is_read == other.is_read and self.is_deleted == other.is_deleted

    def save(self):
        if self._id:
            if messages_manager.update_message(self._id, self):
                result = self._id
            else:
                raise rek.mail_messages.messages_exceptions.CantSaveMessage('Can not save message')
        else:
            result = messages_manager.save_message(self)
        return result

    def clone(self):
        return messages_manager.save_message(self)

    def drop(self):
        messages_manager.del_message(self._id, self.owner)

    def _get_last_recipient(self):
        if len(self.headers):
            return self.headers[-1][u'TO']
        else:
            return ''

    to = property(_get_last_recipient)

    def _get_last_sender(self): #sender
        if len(self.headers):
            header_item = self.headers[-1]
            return header_item['FROM']
        else:
            return self.owner

    sender = property(_get_last_sender)

    def set_sender_and_recipient(self, sender, to, send_date=None):
        if (self.to == to or self.to == '') and self.sender == sender: #edit last header
            self.update_or_add_last_header(to)
        else:#add_new_header
            self.add_new_header(sender, to, send_date)

    def add_new_header(self, sender = None, to='', send_date=mongodb_datetime_now()):
        # when new message saved as draft massage have not from or to header data
        sender = sender or self.owner
        return self.headers.append({
            u'FROM': sender,
            u'TO': to,
            u'DATE': send_date
        })

    def update_or_add_last_header(self, to, sender = None):
        sender = sender or self.owner
        if len(self.headers):
            last_header = self.headers[-1]
            last_header[u'TO'] = to
            last_header[u'FROM'] = sender
            return True
        else:
            return self.add_new_header(self, to)

class MessagesManager(object):
    def __init__(self):
        dbh = mongodb_connection_manager.database
        self.collection = dbh['messages']

    def del_message(self, id, owner):
        result = self.collection.remove({'_id':id, 'owner': owner}, safe=True)
        if 'err' and 'n' in result:
            if result['err'] is None and result['n']==1:
                return True
            else:
                return False
        else:
            raise rek.mail_messages.messages_exceptions.CantDeleteOneMessage('Can not delete one message')

    def save_message(self, mail_message):
        result = self.collection.insert({
            'owner': mail_message.owner,
            'company_rek': mail_message.company_rek,
            'text': mail_message.text,
            'subject': mail_message.subject,
            'folder': mail_message.folder,
            'headers': mail_message.headers,
            'attaches': mail_message.attaches,
            'input_number': mail_message.input_number,
            'output_number': mail_message.output_number,
            'send_date': mail_message.send_date,
            'is_important': mail_message.is_important,
            'is_official': mail_message.is_official,
            'is_auto_answer': mail_message.is_auto_answer,
            'is_read': mail_message.is_read,
            'is_deleted': mail_message.is_deleted
        })
        if isinstance(result, bson.ObjectId):
            mail_message._id = result
            return result
        else:
            raise rek.mail_messages.messages_exceptions.CantAddOneMessage('Can not add one message')

    def update_message(self, id, mail_message):
        result = self.collection.update(
            { # Where
                '_id':id,
                'owner': mail_message.owner
            },
            { # What
                'company_rek': mail_message.company_rek,
                'owner': mail_message.owner,
                'text': mail_message.text,
                'subject':mail_message.subject,
                'folder': mail_message.folder,
                'headers': mail_message.headers,
                'attaches': mail_message.attaches,
                'input_number': mail_message.input_number,
                'output_number': mail_message.output_number,
                'send_date': mail_message.send_date,
                'is_important': mail_message.is_important,
                'is_official': mail_message.is_official,
                'is_auto_answer': mail_message.is_auto_answer,
                'is_read': mail_message.is_read,
                'is_deleted': mail_message.is_deleted
            },
            safe = True
        )

        if 'err' and 'n' in result:
            if result['err'] is None and result['n']==1:
                return True
            else:
                return False
        else:
            raise rek.mail_messages.messages_exceptions.CantUpdateOneMessage('Can not update one message')

    def _set_object(self, db_entry):
        mail_message = MailMessage(db_entry.get('owner'),  db_entry.get('text'), db_entry.get('company_rek'),
                                   db_entry.get('subject'),db_entry.get('folder'),db_entry.get('headers'),
                                   db_entry.get('attaches'),db_entry.get('input_number'), db_entry.get('output_number'),
                                   db_entry.get('send_date'),db_entry.get('is_important'),db_entry.get('is_official'),
                                   db_entry.get('is_auto_answer'),db_entry.get('is_read'), db_entry.get('is_deleted'))

        mail_message._id = db_entry.get('_id')
        return mail_message

    def get_one_message(self, id, owner):
        db_entry = self.collection.find_one({'_id':id, 'owner':owner})
        if db_entry:
            return self._set_object(db_entry)
        else:
            raise rek.mail_messages.messages_exceptions.CantFindOneMessage('Can not find one message')

    def get_messages(self, owner, limit = None, skip = 0, folder=MailMessage.FOLDER_INBOX, is_official=None, is_important=None, sort='send_date', sort_order='DESC'): #skip == mongodb offset
        sort_type = pymongo.DESCENDING if sort_order == 'DESC' else pymongo.ASCENDING
        filter = {'owner':owner}

        if is_important is not None:
            filter['is_important'] = is_important

        if is_official is not None:
            filter['is_official'] = is_official

        if folder == MailMessage.FOLDER_DELETED:
            filter['is_deleted'] = True
        else:
            filter['folder'] = folder

        message_cursor = self.collection.find(filter).sort(sort, sort_type)
        if limit:
            message_cursor = message_cursor.limit(limit)
        if skip:
            message_cursor = message_cursor.skip(skip)

        for message in message_cursor:
            yield self._set_object(message)

    def get_message_count(self, owner, folder, is_official=None, is_important=None):

        filter = {'owner':owner}
        if is_important is not None: filter['is_important'] = is_important
        if is_official is not None: filter['is_official'] = is_official
        if folder == MailMessage.FOLDER_DELETED:
            filter['is_deleted'] = True
        else: 
            filter['folder'] = folder

        message_count = self.collection.find(filter).count()

        return message_count

    def send_message(self, add_message, to):

        send_date = mongodb_datetime_now()
        add_message.folder = MailMessage.FOLDER_SENT
        add_message.send_date = send_date
        add_message.set_sender_and_recipient(add_message.owner, to, send_date)
        add_message.save() #self make add or update if is in Object _id
        add_message.folder = MailMessage.FOLDER_INBOX
        add_message.owner = to
        add_message.clone()

        return True

messages_manager = MessagesManager()
  