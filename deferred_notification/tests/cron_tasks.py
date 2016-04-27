from django.utils import timezone
from django.core import mail

from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.cron import DeferredNotificationsTask
from rek.deferred_notification.manager import notification_manager
from rek.deferred_notification.models import Notification
from rek.tests.base import BaseTestCase

class CronTasksTestCase(BaseTestCase):
    collection_names = ['bill_items', 'billing_accounts', 'billing_transactions', 'users',
                        'companies', 'company_employees', 'sessions', 'recommendation_requests', 'deferred_notifications']

    def test_deferred_notifications_task_send_one(self):
        action = create_action_id(actions.CONFIRM_NEW_EMPLOYEE, 123)
        notification_manager.add(action, 'somebody@somedomain.com', 'subj', 'text', 'html', 0)

        notifications = Notification.objects.get({'is_sent': False, 'send_date': {'$lte': timezone.now()}})
        self.assertEqual(len(notifications), 1)

        mail.outbox = []

        task = DeferredNotificationsTask()
        task.execute()

        notifications = Notification.objects.get({'is_sent': False, 'send_date': {'$lte': timezone.now()}})
        self.assertEqual(len(notifications), 0)
        self.assertEqual(len(mail.outbox), 1)


    def test_deferred_notifications_task_send_two(self):
        action = create_action_id(actions.CONFIRM_NEW_EMPLOYEE, 123)
        notification_manager.add(action, 'somebody@somedomain.com', 'subj', 'text', 'html', 0)
        notification_manager.add(action, 'somebody1@somedomain.com', 'subj2', 'text', 'html', 0)

        notifications = Notification.objects.get({'is_sent': False, 'send_date': {'$lte': timezone.now()}})
        self.assertEqual(len(notifications), 2)

        mail.outbox = []

        task = DeferredNotificationsTask()
        task.execute()

        notifications = Notification.objects.get({'is_sent': False, 'send_date': {'$lte': timezone.now()}})
        self.assertEqual(len(notifications), 0)
        self.assertEqual(len(mail.outbox), 2)
        notifications = Notification.objects.get({'is_sent': True})
        self.assertEqual(len(notifications), 2)

    def test_deferred_notifications_task_send_timeout(self):
        action = create_action_id(actions.CONFIRM_NEW_EMPLOYEE, 123)
        notification_manager.add(action, 'somebody@somedomain.com', 'subj', 'text', 'html', 10)
        notification_manager.add(action, 'somebody1@somedomain.com', 'subj2', 'text', 'html', 10)

        notifications = Notification.objects.get({'is_sent': False})
        self.assertEqual(len(notifications), 2)

        mail.outbox = []

        task = DeferredNotificationsTask()
        task.execute()

        notifications = Notification.objects.get({'is_sent': False})
        self.assertEqual(len(notifications), 2)
        self.assertEqual(len(mail.outbox), 0)
        notifications = Notification.objects.get({'is_sent': True})
        self.assertEqual(len(notifications), 0)
