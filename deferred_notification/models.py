# -*- coding: utf-8 -*-
from django.utils import timezone

from rek.mongo.models import SimpleModel, ObjectManager
from rek.rekvizitka.utils import validateEmail

class Notification(SimpleModel):
    required_fields = ['action', 'message_text', 'email', 'task_date', 'subject', 'is_sent']

    def __init__(self,kwargs):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.action = kwargs.get('action')                  #models.CharField(max_length=255, unique=True, verbose_name=u'notification action', blank=False)
        self.subject = kwargs.get('subject', '')            #models.CharField(max_length=255, verbose_name=u'тема сообщения', default=u'Извещение от Rekvizitka.ru')
        self.message_text = kwargs.get('message_text')      #models.TextField(verbose_name=u'сообщение текст')
        self.message_html = kwargs.get('message_html')      #models.TextField(verbose_name=u'сообщение HTML', blank=True)
        self.email = kwargs.get('email', '')                #models.EmailField(verbose_name=u'email назначение')
        self.task_date = kwargs.get('task_date', timezone.now())            #models.DateTimeField(auto_now_add=True, verbose_name=u'дата добавления')
        self.send_date = kwargs.get('send_date')            #models.DateTimeField(verbose_name=u'дата отправки')
        self.is_sent = kwargs.get('is_sent', False)         #models.BooleanField(verbose_name=u'статус отправки', default=False, choices=((False, 'неотправлено'),(True, 'отправлено'),))
        self.attaches = kwargs.get('attaches', [])

    def _fields(self):
        fields = {
            'action' : self.action,
            'message_text' : self.message_text,
            'email' : self.email,
            'task_date' : self.task_date,
            'subject' : self.subject,
            'is_sent' : self.is_sent,
            'message_html' : self.message_html,
            'send_date' : self.send_date,
            'attaches' : self.attaches
        }

        return fields

    def save(self):
        if not self.is_valid():
            raise Exception("Failed to save notification. Notification data is invalid.")

        return super(Notification, self).save()

    def is_valid(self):
        data = self._fields()
        for field_name in Notification.required_fields:
            if field_name not in data:
                return False
        if not validateEmail(data['email']):
            return False
        return True

Notification.objects = ObjectManager(Notification, 'deferred_notifications', [('action', 1),
                                     ('task_date', -1), ('send_date', -1)])