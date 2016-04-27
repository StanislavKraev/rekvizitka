# -*- coding: utf-8 -*-

import bson
from django.core import mail
from rek.billing.models import Account
from rek.mango.auth import UserActivationLinks, User
from rek.tests.base import BaseTestCase

mail.outbox = []

class RekvizitkaTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'user_activation_links', 'billing_accounts', 'deferred_notifications']

    def testRegister(self):
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(self.collections['users'].count(), 1)
        user = self.collections['users'].find_one()
        self.assertIsNotNone(user['_id'])
        self.assertIsInstance(user['_id'], bson.ObjectId)
        self.assertGreater(len(unicode(user['_id'])), 10)
        self.assertFalse(user['activated'])

        self.assertEqual(UserActivationLinks.objects.count(), 1)
        link = UserActivationLinks.objects.get({})[0]
        self.assertEqual(link.user, user['_id'])

        self.assertEqual(self.collections['company_employees'].count(), 1)
        employee = self.collections['company_employees'].find_one()
        self.assertIsNotNone(employee['_id'])
        self.assertIsInstance(employee['_id'], bson.ObjectId)
        self.assertGreater(len(unicode(employee['_id'])), 10)

        self.assertIsNotNone(employee['user_id'])
        self.assertEqual(user['_id'], employee['user_id'])

        self.assertEqual(self.collections['companies'].count(), 1)
        company = self.collections['companies'].find_one()
        self.assertIsNotNone(company['_id'])
        self.assertIsInstance(company['_id'], bson.ObjectId)
        self.assertGreater(len(unicode(company['_id'])), 10)

        self.assertIsNotNone(employee['company_id'])
        self.assertEqual(company['_id'], employee['company_id'])

        company_billing_account = Account.objects.get_one({'details.subject_id' : company['_id'],
                                                           'type' : Account.TYPE_COMPANY})
        self.assertIsNotNone(company_billing_account)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'registered')

    def testRegisterIncorrectOrMissedPassword(self):
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Brand Name',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['password_error'], True)

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Brand Name',
            'password' : 'abcАБВ',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['password_error'], True)

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

    def testRegisterIncorrectOrMissedBrandName(self):
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['brand_name_error'], True)

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : '',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['brand_name_error'], True)
        self.assertEqual(response.context['page_status'], 'user_creating_error')

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

    def testActivateAccount(self):
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        user = User.collection.find_one()
        self.assertIsNotNone(user)
        self.assertFalse(user['activated'])
        self.assertEqual(self.collections['user_activation_links'].count(), 1)

        link = self.collections['user_activation_links'].find_one()

        response = self.client.get('/activate_account/' + str(link['_id']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'account_activated')
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

    def testActivateBrokenLink(self):
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

        response = self.client.get('/activate_account/' + str(bson.ObjectId()))
        self.assertEqual(response.status_code, 404)

    def testRegisterMissedEmail(self):
        response = self.client.post('/', {
            'password' : 'aaabbb',
            'brand_name' : 'Test Company',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['email_error'], True)

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

    def testRegisterIncorrectEmail(self):
        response = self.client.post('/', {
            'email' : 'test@testunavailabledom ain.ru',
            'password' : 'aaabbb',
            'brand_name' : 'Test Company',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['email_error'], True)

        self.assertEqual(self.collections['users'].count(), 0)
        self.assertEqual(self.collections['company_employees'].count(), 0)
        self.assertEqual(self.collections['companies'].count(), 0)
        self.assertEqual(self.collections['user_activation_links'].count(), 0)

    def testRegisterDuplicateEmail(self):
        response = self.client.post('/', {
            'email' : 'duplicated@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'brand_name' : 'Test Company',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('signup_form', response.context)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(self.collections['users'].count(), 1)
        self.assertEqual(self.collections['company_employees'].count(), 1)
        self.assertEqual(self.collections['companies'].count(), 1)
        self.assertEqual(self.collections['user_activation_links'].count(), 1)
        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'registered')

        response = self.client.post('/', {
            'email' : 'duplicated@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'brand_name' : 'Test Company',
            'join' : 'join'
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['signup_form']._errors), 0)

        self.assertEqual(self.collections['users'].count(), 1)
        self.assertEqual(self.collections['company_employees'].count(), 1)
        self.assertEqual(self.collections['companies'].count(), 1)
        self.assertEqual(self.collections['user_activation_links'].count(), 1)
        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_creating_error')
        self.assertEqual(response.context['email_error'], True)

    def testUnregisteredLogin(self):
        self.client.get('/')
        response = self.client.post('/', {
            'username' : 'unregistered@testunavailabledomain.ru'
        })
        self.assertEqual(response.status_code, 200)


    def testLogin(self):
        self.assertNotIn('_auth_user_id', self.client.session)
        self.client.get('/')
        self.client.post('/', {
            'email' : 'registered@testunavailabledomain.ru',
            'brand_name' : 'Brand Name',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        User.collection.update({}, {'$set' : {'activated' : True}}, multi=True)
        response = self.client.post('/', {
            'username' : 'registered@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'login' : 'login'
        })

        self.assertIn('_auth_user_id', self.client.session)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'][17:], '/CK1/')

    def testLoginNotActivated(self):
        self.assertNotIn('_auth_user_id', self.client.session)
        self.client.post('/', {
            'email' : 'registered@testunavailabledomain.ru',
            'brand_name' : 'Brand Name',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        response = self.client.post('/', {
            'username' : 'registered@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'login' : 'login'
        })

        self.assertNotIn('_auth_user_id', self.client.session)

        self.assertEqual(response.status_code, 200)
        self.assertIn('page_status', response.context)
        self.assertEqual(response.context['page_status'], 'user_not_activated')

    def testLogout(self):
        self.client.get('/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.client.post('/', {
            'email' : 'registered@testunavailabledomain.ru',
            'brand_name' : 'Brand Name',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        User.collection.update({}, {'$set' : {'activated' : True}}, multi=True)
        self.client.post('/', {
            'username' : 'registered@testunavailabledomain.ru',
            'password' : 'aaabbb',
            'login' : 'login'
        })
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post('/logout/', {
            'email' : 'registered@testunavailabledomain.ru'
        })
        self.assertNotIn('_auth_user_id', self.client.session)

    def testIndexPageNotLoggedIn(self):
        self.register()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def testIndexPageLoggedIn(self):
        self.register()
        self.login()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'][17:], '/CK1/')

    def testShowProfileNotLoggedInNotVerified(self):
        self.register(verified=False)
        response = self.client.get('/CK1/profile/')
        self.assertEqual(response.status_code, 404)

    def testShowProfileLoggedInNotVerified(self):
        self.register(verified=False)
        self.login()
        response = self.client.get('/CK1/profile/')
        self.assertEqual(response.status_code, 200)

    def testShowProfileNotLoggedInVerified(self):
        self.register()
        response = self.client.get('/CK1/profile/')
        self.assertEqual(response.status_code, 200)

    def testShowProfileLoggedInVerified(self):
        self.register()
        self.login()
        response = self.client.get('/CK1/profile/')
        self.assertEqual(response.status_code, 200)

    def testRegisterWhileLoggedIn(self):
        self.register()
        self.login()

        response = self.client.post('/', {
            'email' : 'test2@testunavailabledomain.ru',
            'brand_name' : 'Company brand name2',
            'password' : 'aaabbb',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'][17:], '/')
