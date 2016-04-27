# -*- coding: utf-8 -*-
from django.core.management import call_command
from rek.billing.models import Account

from rek.tests.base import BaseTestCase
from rek.rekvizitka.models import Company

class AccountsTestCase(BaseTestCase):
    collection_names = ['billing_accounts', 'billing_transactions', 'users', 'companies', 'company_employees', 'sessions', 'deferred_notifications']

    def test_init_accounts_command(self):
        self.register_companies(count=3)
        companies = Company.objects.get({})
        self.assertEqual(len(companies), 3)

        for company in companies:
            account = Account.objects.get_one({'details.subject_id':company._id, 'type' : Account.TYPE_COMPANY})
            self.assertIsNone(account)

        self.assertIsNone(Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID}))
        self.assertIsNone(Account.objects.get_one({'system_id' : Account.FIXED_ADS_ACCOUNT_ID}))
        self.assertIsNone(Account.objects.get_one({'system_id' : Account.FIXED_PROMO_ACCOUNT_ID}))

        call_command("init_billing_accounts")

        for company in companies:
            account = Account.objects.get_one({'details.subject_id':company._id, 'type' : Account.TYPE_COMPANY})
            self.assertIsNotNone(account)

        self.assertIsNotNone(Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID}))
        self.assertIsNotNone(Account.objects.get_one({'system_id' : Account.FIXED_ADS_ACCOUNT_ID}))
        self.assertIsNotNone(Account.objects.get_one({'system_id' : Account.FIXED_PROMO_ACCOUNT_ID}))
