# -*- coding: utf-8 -*-
from django.utils import simplejson

from rek.tests.base import BaseTestCase

class SearchTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'contractors', 'user_activation_links']

    def load_data(self, response):
        d = self.find_context_item(response.context, 'search_initials')
        data = simplejson.loads(d['search_initials'])
        return data

    def find_context_item(self, context, item):
        d = context[0].dicts
        for dict in d:
            if item in dict:
                return dict

    def testSearchRekId(self):
        self.register()
        response = self.client.get('/search/?q=CK1')
        self.assertEqual(response.status_code, 200)
        data = self.load_data(response)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['company_url'], '/CK1/')

    def testSearchBrandName(self):
        pass

    def testSearchShortName(self):
        pass

    def testSearchFullName(self):
        pass

    def testSearchDescription(self):
        pass

    def testSearchNotVerified(self):
        self.register(verified=False)
        response = self.client.get('/search/?q=CK1')
        self.assertEqual(response.status_code, 200)
        data = self.load_data(response)
        self.assertEqual(len(data['results']), 0)
