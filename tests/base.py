# -*- coding: utf-8 -*-
from random import randint

from django.core import mail
from django.utils import unittest
from django.test.client import Client
from rek.contractors.models import Contractor
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import Company, CompanyEmployee
from rek.rekvizitka.utils import integer_to_code

from rek.tests.runner import MongoDBTestRunner

class BaseTestCase(unittest.TestCase):
    user_email = 'test@testunavailabledomain.ru'
    collection_names = []

    def setUp(self):
        self.db = MongoDBTestRunner.test_db

        self.collections = {}
        for name in self.collection_names:
            self.collections[name] = self.db[name]

        self.client = Client()
        User.set_indexes()
        Contractor.set_indexes()
        self.company = None
        self.employee = None

    def tearDown(self):
        self.client = None
        for col in self.collections.keys():
            self.db.drop_collection(col)
        mail.outbox = []

    def register(self, verified = True, email = 'registered@testunavailabledomain.ru'):
        rand_brand = 'Test Company Brand name ' + str(randint(1, 100000))
        self.client.post('/', {
            'email' : email,
            'brand_name' : rand_brand,
            'password' : 'aaabbb',
            'join' : 'join'
        })
        company = self.collections['companies'].find_one({'brand_name' : rand_brand})
        if verified:
            self.collections['companies'].update({'_id' : company['_id']},
                    {'$set' : {'account_status' : CompanyAccountStatus.VERIFIED,
                               'is_account_activated' : True,
                               'brand_name' : 'Brand name',
                               'description' : 'System testing'}})
        else:
            self.collections['companies'].update({'_id' : company['_id']},
                    {'$set' : {'is_account_activated' : True,
                               'brand_name' : 'Brand name',
                               'description' : 'System testing'}})
        self.company = Company.objects.get_one({'_id' : company['_id']})
        self.employee = CompanyEmployee.objects.get_one({'company_id' : company['_id']})
        User.collection.update({'_id' : self.employee.user_id}, {'$set' : {'activated' : True}})

    def register_companies(self, count = 10, verified = True):
        companies = []
        for a in xrange(count):
            user = User.create_user('new_registered_user%d@testdomain.xy' % a, User.make_random_password())
            if not user:
                raise Exception('failed to create test user')
            User.collection.update({'_id' : user._id}, {'$set' : {'activated' : True}})

            employee = CompanyEmployee({'user_id' : user._id,
                                        'first_name' : 'test_user_' + str(a)})
            employee.save()
            company = Company({'rek_id' : integer_to_code(a + 10000),
                'owner_employee_id' : employee._id,
                'short_name' : 'tc_' + str(a),
                'full_name' : 'OOO Test Company ' + str(a),
                'brand_name' : 'Test Company Brand ' + str(a),
                'description' : 'Test company ' + str(a),
                'category_text' : 'Testing',
                'staff_size' : (a + 1) * 3,
                'inn' : int(str(a + 1) + '0' * (12 - len(str(a)))) + a + 1,
                'kpp' : int(str(a + 1) + '1' * (9 - len(str(a)))) + a + 1,
                'is_account_activated' : True,
                'account_status' : CompanyAccountStatus.VERIFIED if verified else CompanyAccountStatus.JUST_REGISTERED
            })
            company.save()
            employee.set(company_id = company._id)
            companies.append(company)

        return companies

    def login(self, password = 'aaabbb'):
        return self.client.post('/', {
            'username' : 'registered@testunavailabledomain.ru',
            'password' : password,
            'login' : 'login'
        })

    def login_as(self, email):
        self.client.post('/', {
            'username' : email,
            'password' : 'aaabbb',
            'login' : 'login'
        })

    def logout(self):
        self.client.post('/logout/', {
            'email' : 'registered@testunavailabledomain.ru'
        })
