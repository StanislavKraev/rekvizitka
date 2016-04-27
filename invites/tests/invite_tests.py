# -*- coding: utf-8 -*-
from django.test.client import Client
from django.utils import simplejson
from rek.billing.models import Transaction, Account
from rek.deferred_notification.models import Notification
from rek.invites.models import Invite, RecommendationRequest
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import Company, get_user_company
from rek.system_data.rek_settings import SettingsManager
from rek.tests.base import BaseTestCase

class InvitesTestCase(BaseTestCase):
    collection_names = ['bill_items', 'billing_accounts', 'billing_transactions', 'users',
                        'companies', 'company_employees', 'sessions',
                        'recommendation_requests', 'invites', 'deferred_notifications']

    def setUp(self):
        super(InvitesTestCase, self).setUp()
        SettingsManager.set_property('verifylettercount', 0)

    def test_send_invite_not_verified(self):
        self.register(verified=False)
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 302)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 0)

    def test_send_invite(self):
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 1)

    def test_send_invalid_invite(self):
        self.register()
        self.login()

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        data = {}
        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertFalse(data['success'])

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

    def test_send_invite_existing_email(self):
        self.register()
        self.login()

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'registered@testunavailabledomain.ru'}
        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('email_exists', data)
        self.assertTrue(data['email_exists'])

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

    def test_invite_cookie(self):
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        self.logout()
        response = self.client.get(u'/invites/join/%s/' % invite.cookie_code)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.client.cookies.has_key('invite'))

    def test_invite_cookie_invalid_url(self):
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        self.logout()
        response = self.client.get(u'/invites/join/qwerty/')
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self.client.cookies.has_key('invite'))

    def test_register_after_invite(self):
        SettingsManager.set_property('rnes', 3)
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        self.logout()
        response = self.client.get(u'/invites/join/%s/' % invite.cookie_code)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.client.cookies.has_key('invite'))

        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(RecommendationRequest.objects.count(), 0)
        self.register(email="someemail@somedomain.zz", verified=False)
        self.login()
        self.assertEqual(Company.objects.count(), 2)

        invite = Invite.objects.get_one({})
        self.assertEqual(RecommendationRequest.objects.count(), 1)
        self.assertEqual(invite.rec_request, RecommendationRequest.objects.get_one({})._id)

        user = User(User.collection.find_one({'email' : "someemail@somedomain.zz"}))
        company = get_user_company(user)
        self.assertEqual(company.account_status, CompanyAccountStatus.JUST_REGISTERED)

    def test_twice_register_after_invite(self):
        SettingsManager.set_property('rnes', 3)
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        self.logout()
        response = self.client.get(u'/invites/join/%s/' % invite.cookie_code)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.client.cookies.has_key('invite'))

        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(RecommendationRequest.objects.count(), 0)
        self.register(email="someemail@somedomain.zz", verified=False)
        self.login()
        self.assertEqual(Company.objects.count(), 2)

        invite = Invite.objects.get_one({})
        self.assertEqual(RecommendationRequest.objects.count(), 1)
        self.assertEqual(invite.rec_request, RecommendationRequest.objects.get_one({})._id)

        user = User(User.collection.find_one({'email' : "someemail@somedomain.zz"}))
        company = get_user_company(user)
        self.assertEqual(company.account_status, CompanyAccountStatus.JUST_REGISTERED)

        self.logout()
        self.client = Client()
        response = self.client.get(u'/invites/join/%s/' % invite.cookie_code)
        self.assertEquals(response.status_code, 302)
        self.assertFalse(self.client.cookies.has_key('invite'))

        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(RecommendationRequest.objects.count(), 1)
        self.register(email="someemail2@somedomain.zz", verified=False)
        self.login()
        self.assertEqual(Company.objects.count(), 3)

        self.assertEqual(RecommendationRequest.objects.count(), 1)

        trans = Transaction.objects.get_one({})
        self.assertIsNone(trans)

    def test_register_after_invite_and_verify(self):
        account = Account({"system_id" : Account.FIXED_PROMO_ACCOUNT_ID,
                           "name" : "Счет промо-акцийг",
                           "type" : Account.TYPE_VIRTUAL})
        account.save()

        SettingsManager.set_property('rnes', 1)
        self.register()
        self.login()

        data = {'msg' : 'Come on! Join us now!',
                'email' : 'pupkin@pipkin.zz'}

        notifications = Notification.objects.get({})
        self.assertEqual(len(notifications), 0)

        response = self.client.post('/invites/send/', data)
        self.assertEquals(response.status_code, 200)

        invites = Invite.objects.get({})
        self.assertEqual(len(invites), 1)
        invite = invites[0]
        self.assertEqual(invite.message, 'Come on! Join us now!')
        self.assertEqual(invite.email, 'pupkin@pipkin.zz')

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        self.logout()
        response = self.client.get(u'/invites/join/%s/' % invite.cookie_code)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.client.cookies.has_key('invite'))

        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(RecommendationRequest.objects.count(), 0)
        self.register(email="someemail@somedomain.zz", verified=False)
        self.login()
        self.assertEqual(Company.objects.count(), 2)

        invite = Invite.objects.get_one({})
        self.assertEqual(RecommendationRequest.objects.count(), 1)
        self.assertEqual(invite.rec_request, RecommendationRequest.objects.get_one({})._id)

        user = User(User.collection.find_one({'email' : "someemail@somedomain.zz"}))
        company = get_user_company(user)
        self.assertEqual(company.account_status, CompanyAccountStatus.VERIFIED)

        trans = Transaction.objects.get_one({})
        self.assertIsNotNone(trans)
        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(trans.amount.amount, SettingsManager.get_property('invite_bonus'))
        self.assertEqual(trans.source_account, account._id)
        dest_account = Account.objects.get_one({'type' : Account.TYPE_COMPANY,
                                                'details.subject_id' : invite.sender})
        self.assertEqual(trans.dest_account, dest_account._id)

