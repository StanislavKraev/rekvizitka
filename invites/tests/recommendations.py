# -*- coding: utf-8 -*-
from django.core import mail
from django.utils import simplejson
from rek.invites.models import RecommendationRequest, RecommendationStatusEnum
from rek.rekvizitka.models import Company
from rek.system_data.rek_settings import SettingsManager
from rek.tests.base import BaseTestCase

mail.outbox = []

class InvitesRecsTestCase(BaseTestCase):
    collection_names = ['bill_items', 'billing_accounts', 'billing_transactions', 'users',
                        'companies', 'company_employees', 'sessions',
                        'recommendation_requests', 'invites', 'deferred_notifications']

    def setUp(self):
        super(InvitesRecsTestCase, self).setUp()
        SettingsManager.set_property('verifylettercount', 0)

    def test_give_recommendation(self):
        self.register()
        self.login()
        companies = self.register_companies(1)
        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        self.assertEqual(rec.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(rec.requester, companies[0]._id)
        self.assertEqual(rec.recipient, self.company._id)

    def test_give_recommendation_not_auth(self):
        self.register()
        companies = self.register_companies(1)
        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 302)

    def test_give_cross_recommendation(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.RECEIVED})
        cur_rec.save()

        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        self.assertEqual(rec.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(rec.requester, companies[0]._id)
        self.assertEqual(rec.recipient, self.company._id)

    def test_give_cross_recommendation_not_verified(self):
        self.register()
        self.login()
        companies = self.register_companies(1, verified=False)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.RECEIVED})
        cur_rec.save()

        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        self.assertEqual(rec.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(rec.requester, companies[0]._id)
        self.assertEqual(rec.recipient, self.company._id)

        company_upd = Company.objects.get_one({'_id' : companies[0]._id})
        self.assertEqual(company_upd.account_status, 'verified')

    def test_give_rec_declined(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.DECLINED})
        cur_rec.save()

        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        self.assertEqual(rec.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(rec.requester, companies[0]._id)
        self.assertEqual(rec.recipient, self.company._id)

    def test_give_rec_duplicate(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.ACCEPTED})
        cur_rec.save()


        response = self.client.post('/recommendations/give/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        self.assertEqual(rec.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(rec.requester, companies[0]._id)
        self.assertEqual(rec.recipient, self.company._id)

    def test_take_recommendation(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.ACCEPTED})
        cur_rec.save()

        response = self.client.post('/recommendations/take-away/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 0)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

    def test_take_rec_not_found(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        response = self.client.post('/recommendations/take-away/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 0)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def test_take_rec_declined(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.DECLINED})
        cur_rec.save()

        response = self.client.post('/recommendations/take-away/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def test_take_rec_received(self):
        self.register()
        self.login()
        companies = self.register_companies(1)

        cur_rec = RecommendationRequest({'recipient' : self.company._id,
                                         'requester' : companies[0]._id,
                                         'status' : RecommendationStatusEnum.RECEIVED})
        cur_rec.save()

        response = self.client.post('/recommendations/take-away/%s/' % companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        recs = RecommendationRequest.objects.get({})
        self.assertEqual(len(recs), 1)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)
