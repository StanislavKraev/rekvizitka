# -*- coding: utf-8 -*-
from django.utils import simplejson

from rek.tests.base import BaseTestCase

class PasswordTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'user_activation_links', 'billing_accounts', 'deferred_notifications']

    def testChangePasswordOk(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbb', 'new' : 'bbbccc', 'new2' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)
        self.logout()
        response = self.login('bbbccc')
        self.assertEqual(response.status_code, 302)
        self.assertIn('location', response._headers)
        self.assertEqual(response._headers['location'], ('Location', 'http://testserver/CK1/'))

    def testChangePasswordNoOld(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'new' : 'bbbccc', 'new2' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordBadOld(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : '\ффф', 'new' : 'bbbccc', 'new2' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordWrongOld(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbc', 'new' : 'bbbccc', 'new2' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordNoNew(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbb', 'new2' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordNoNew2(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbb', 'new' : 'bbbccc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordBadNew(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbb', 'new2' : 'aa', 'new' : 'aa'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)

    def testChangePasswordDoNotMatch(self):
        self.register()
        self.login()
        response = self.client.post('/profile/change_pwd/', {'old' : 'aaabbb', 'new' : '123456', 'new2' : '123457'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)