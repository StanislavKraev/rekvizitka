# -*- coding: utf-8 -*-
from django.utils import timezone
from rek.mongo.models import SimpleModel, ObjectManager

class ChatDialog(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')

        self.creator = kwargs.get('creator')                                            # employee id
        self.parties = kwargs.get('parties', [])                                        # employee ids
        self.not_viewed_by_parties = kwargs.get('not_viewed_by_parties', [])            # employee ids
        self.hidden_by_parties = kwargs.get('hidden_by_parties', [])                        # employee ids

        self.last_message_date = kwargs.get('last_message_date')
        self.last_message_text = kwargs.get('last_message_text', '')
        self.last_message_party = kwargs.get('last_message_party')
        self.last_message_id = kwargs.get('last_message_id')

    def _fields(self):
        fields = {
            'creator' : self.creator,
            'parties' : self.parties,
            'not_viewed_by_parties' : self.not_viewed_by_parties,
            'hidden_by_parties' : self.hidden_by_parties,

            'last_message_date' : self.last_message_date,
            'last_message_text' : self.last_message_text,
            'last_message_party' : self.last_message_party,
            'last_message_id' : self.last_message_id
            }
        return fields

ChatDialog.objects = ObjectManager(ChatDialog, 'chat_dialog',
    [('creator', 1), ('parties', 1), ('last_message_date', -1)])

class DialogMessage(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.dialog = kwargs.get('dialog')
        self.text = kwargs.get('text', '')
        self.date = kwargs.get('date', timezone.now())
        self.creator = kwargs.get('creator')

    def _fields(self):
        fields = {
            'dialog' : self.dialog,
            'text' : self.text,
            'date' : self.date,
            'creator' : self.creator
        }
        return fields

DialogMessage.objects = ObjectManager(DialogMessage, 'dialog_message',
    [('dialog', 1), ('date', -1), ('creator', 1)])
