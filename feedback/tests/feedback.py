# -*- coding: utf-8 -*-
from django.utils import simplejson
from rek.tests.base import BaseTestCase

class FeedbackTestCase(BaseTestCase):
    collection_names = ['billing_accounts', 'users', 'companies',
                        'company_employees', 'sessions', 'user_activation_links',
                        'deferred_notifications']

    def test_initials(self):
        response = self.client.get('/feedback/')
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('email', data)
        self.assertEqual(data['email'], '')

    def test_send_feedback_notification(self):
        data = {}
        self.client.post('/feedback/', data)

    def test_bot_send_feedback_notification(self):
        data = {'extra_field' : '123'}
        self.client.post('/feedback/', data)

    def test_send_incorrect_feedback_no_email(self):
        data = {'email' : '',
                'msg' : '123123123123'}
        response = self.client.post('/feedback/', data)
        self.assertEqual(response.status_code, 400)

    def test_send_incorrect_feedback_no_message(self):
        data = {'email' : 'aaa@bbb.ccc',
                'msg' : ''}
        response = self.client.post('/feedback/', data)
        self.assertEqual(response.status_code, 400)

    def test_initials_when_logged_in(self):
        self.register()
        self.login()
        response = self.client.get('/feedback/')
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('email', data)
        self.assertEqual(data['email'], 'registered@testunavailabledomain.ru')