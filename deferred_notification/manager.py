# -*- coding: utf-8 -*-

from datetime import timedelta
from django.utils import timezone
from rek.deferred_notification.models import Notification

class NotificationManager(object):
    def add(self, action, email, subject, message_text, message_html=u'', delay_minutes=0):

        date_now = timezone.now()
        difference = timedelta(minutes=delay_minutes)
        send_date = date_now + difference
        
        new_notification = Notification({
            'action' : action,
            'subject' : subject,
            'message_text' : message_text,
            'message_html' : message_html,
            'email' : email,
            'send_date' : send_date
        })
        try:
            new_notification.save()
        except Exception:
            return False

        return True

    def remove(self, action):
        Notification.objects.collection.remove({'action':action})
        return True

notification_manager = NotificationManager()
