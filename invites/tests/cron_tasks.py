# -*- coding: utf-8 -*-
from datetime import timedelta
from bson.objectid import ObjectId
from django.utils import timezone
from rek.invites.cron import RemoveOldRecRequestsTask
from rek.invites.models import RecommendationRequest, RecommendationStatusEnum
from rek.system_data.rek_settings import SettingsManager
from rek.tests.base import BaseTestCase

class CronTasksTestCase(BaseTestCase):
    collection_names = ['bill_items', 'billing_accounts', 'billing_transactions', 'users',
                        'companies', 'company_employees', 'sessions', 'recommendation_requests', 'deferred_notifications']

    def test_remove_old_recommendations_not_old(self):
        SettingsManager.set_property('rtimeout', 1)
        r = RecommendationRequest({'requester' : ObjectId(),
                                   'recipient' : ObjectId(),
                                   'message' : 'message',
                                   'requester_email' : 'aaa@aaabbb.ru'})
        r.save()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)
        self.assertEqual(rr.status, RecommendationStatusEnum.RECEIVED)

        task = RemoveOldRecRequestsTask()
        task.execute()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)
        self.assertEqual(rr.status, RecommendationStatusEnum.RECEIVED)

    def test_remove_old_recommendations_really_old(self):
        SettingsManager.set_property('rtimeout', 1)
        r = RecommendationRequest({'requester' : ObjectId(),
                                   'recipient' : ObjectId(),
                                   'message' : 'message',
                                   'requester_email' : 'aaa@aaabbb.ru',
                                   'send_date' : timezone.now() - timedelta(days = 1)})
        r.save()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)
        self.assertEqual(rr.status, RecommendationStatusEnum.RECEIVED)

        task = RemoveOldRecRequestsTask()
        task.execute()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNone(rr)

    def test_remove_old_recommendations_really_accepted(self):
        SettingsManager.set_property('rtimeout', 1)
        r = RecommendationRequest({'requester' : ObjectId(),
                                   'recipient' : ObjectId(),
                                   'message' : 'message',
                                   'requester_email' : 'aaa@aaabbb.ru',
                                   'status' : RecommendationStatusEnum.ACCEPTED,
                                   'send_date' : timezone.now() - timedelta(days = 1)})
        r.save()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)
        self.assertEqual(rr.status, RecommendationStatusEnum.ACCEPTED)

        task = RemoveOldRecRequestsTask()
        task.execute()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)

    def test_remove_old_recommendations_timeout(self):
        SettingsManager.set_property('rtimeout', 24 * 10)
        r = RecommendationRequest({'requester' : ObjectId(),
                                   'recipient' : ObjectId(),
                                   'message' : 'message',
                                   'requester_email' : 'aaa@aaabbb.ru',
                                   'status' : RecommendationStatusEnum.DECLINED,
                                   'send_date' : timezone.now() - timedelta(days = 1)})
        r.save()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)
        self.assertEqual(rr.status, RecommendationStatusEnum.DECLINED)

        task = RemoveOldRecRequestsTask()
        task.execute()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNotNone(rr)

        SettingsManager.set_property('rtimeout', 1)

        task.execute()

        rr = RecommendationRequest.objects.get_one({'_id' : r._id})
        self.assertIsNone(rr)
