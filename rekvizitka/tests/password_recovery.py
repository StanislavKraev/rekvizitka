# -*- coding: utf-8 -*-
from bson.objectid import ObjectId

from django.contrib.auth import authenticate as auth_authenticate
from django.core import mail
from rek.deferred_notification.models import Notification
from rek.mango.auth import User
from rek.rekvizitka.models import PasswordRecoveryLink
from rek.tests.base import BaseTestCase

mail.outbox = []

class PasswordRecoveryTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions',
                        'user_activation_links', 'billing_accounts', 'deferred_notifications',
                        'password_recovery_links']

    def test_recovery_url(self):
        self.register()
        response = self.client.get('/password-recovery/')
        self.assertEqual(response.status_code, 200)

    def test_request_password_link(self):
        self.register()
        self.assertEqual(len(mail.outbox), 1)
        notification_count = Notification.objects.count()

        response = self.client.post('/password-recovery/', {'email' : 'registered@testunavailabledomain.ru'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('link_id', response.context)
        link_id = ObjectId(response.context['link_id'])

        link = PasswordRecoveryLink.objects.get_one({'_id' : link_id})
        self.assertIsNotNone(link)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Notification.objects.count(), notification_count + 1)

    def test_request_no_email(self):
        self.register()
        response = self.client.post('/password-recovery/')
        self.assertEqual(response.status_code, 404)

    def test_request_no_such_email(self):
        self.register()
        response = self.client.post('/password-recovery/', {'email' : 'wrong@testunavailabledomain.ru'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_not_found', response.context)
        self.assertTrue(response.context['user_not_found'])

    def test_set_new_password_url(self):
        self.register()
        user = User.collection.find_one({'email' : 'registered@testunavailabledomain.ru'})
        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        response = self.client.get('/new-password/' + unicode(link._id) + '/')
        self.assertEqual(response.status_code, 200)

    def test_set_new_password_invalid_url(self):
        self.register()
        user = User.collection.find_one({'email' : 'registered@testunavailabledomain.ru'})
        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        response = self.client.get('/new-password/' + 'abc' + '/')
        self.assertEqual(response.status_code, 404)

    def test_set_new_password_missed_link(self):
        self.register()
        user = User.collection.find_one({'email' : 'registered@testunavailabledomain.ru'})
        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        response = self.client.get('/new-password/' + unicode(ObjectId) + '/')
        self.assertEqual(response.status_code, 404)

    def test_set_new_password_post(self):
        self.register()
        user = User.collection.find_one({'email' : 'registered@testunavailabledomain.ru'})
        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        response = self.client.post('/new-password/' + unicode(link._id) + '/', {'new_password' : 'new_password',
                                                                                 'new_password_repeat' : 'new_password'})
        self.assertEqual(response.status_code, 200)

        self.assertIn('password_set', response.context)
        self.assertTrue(response.context['password_set'])

        link = PasswordRecoveryLink.objects.get_one({'user':user['_id']})
        self.assertIsNone(link)
        auth_user = auth_authenticate(username='registered@testunavailabledomain.ru', password='new_password')
        self.assertIsNotNone(auth_user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_set_new_password_post_incorrect_link(self):
        self.register()
        user = User.collection.find_one({'email' : 'registered@testunavailabledomain.ru'})
        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        response = self.client.post('/new-password/' + 'abc' + '/', {'new_password' : 'new_password'})
        self.assertEqual(response.status_code, 404)
        link = PasswordRecoveryLink({'user':user['_id']})
        self.assertIsNotNone(link)
        auth_user = auth_authenticate(username='registered@testunavailabledomain.ru', password='new_password')
        self.assertIsNone(auth_user)
