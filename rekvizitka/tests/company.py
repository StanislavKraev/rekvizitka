# -*- coding: utf-8 -*-
from rek.mongo.fsm import StateChangeException
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import Company

from rek.tests.base import BaseTestCase

class CompanyTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'user_activation_links']

    def testVerifyRaw(self):
        company = Company({'brand_name' : 'Test Company Brand name'})
        company.save()
        company.change_fsm_state(CompanyAccountStatus.VERIFIED, brand_name='brand name', description='description')

        company = Company.objects.get_one({'brand_name' : 'brand name', 'description' : 'description'})
        self.assertIsNotNone(company)
        self.assertEqual(company.account_status, CompanyAccountStatus.VERIFIED)

    def testIncorrectTransition(self):
        company = Company({'brand_name' : 'Test Company Brand name'})
        company.save()
        self.assertRaises(StateChangeException, company.change_fsm_state, CompanyAccountStatus.SEMI_VERIFIED)