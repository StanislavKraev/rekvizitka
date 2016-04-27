# -*- coding: utf-8 -*-
import sys
import time

from django.utils import timezone
from django.core.mail.message import EmailMultiAlternatives
from rek import settings
from rek.deferred_notification.models import Notification

from rek.cron.cron_task import CronTaskBase

SECONDS_LIMIT = 20

class DeferredNotificationsTask(CronTaskBase):
    def execute(self):
        print >> sys.stdout, 'Executing DeferredNotificationsTask'

        start = time.time()
        notifications = Notification.objects.collection.find({'is_sent': False,
                                                            'send_date': {'$lte': timezone.now()}
                                                             }).sort('send_date', -1)
        for notification in notifications:
            msg = EmailMultiAlternatives(notification['subject'],
                                         notification['message_text'],
                                         settings.EMAIL_HOST_USER,
                                         [notification['email'], ], [])

            if len(notification['message_html']):
                msg.attach_alternative(notification['message_html'], "text/html")

#           mustdo: implement attaches
#            attaches = NotificationAttaches.objects.filter(nid=notification)
#            sys.stdout.write(u'    Find %d attache files\n' % attaches.count())
#
#            if attaches.count():
#                for attache in attaches:
#                    sys.stdout.write(u'    Attache file: %s\n' % attache.file)
#                    msg.attach_file(attache.file)

            msg.send()

            Notification.objects.update({'_id' : notification['_id']}, {'$set' : {'is_sent' : True}})

            finish = time.time()
            run_time = finish - start
            if run_time > SECONDS_LIMIT:
                return
