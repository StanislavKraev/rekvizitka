# -*- coding: utf-8 -*-
from datetime import timedelta
import bson
from bson.objectid import ObjectId
from django.utils import timezone
from django.core.management import call_command
from rek.billing import invoice_manager
from rek.billing.cron import RotInvoicesTask

from rek.billing.models import Invoice, InvoiceStatusEnum, Account, Transaction, Currency
from rek.tests.base import BaseTestCase

class InvoiceModelTestCase(BaseTestCase):
    collection_names = ['bill_items', 'billing_accounts', 'billing_transactions', 'users',
                        'companies', 'company_employees', 'sessions', 'deferred_notifications']

    def testCreateEmpty(self):
        invoice = Invoice()
        self.assertEquals(invoice._id, None)
        self.assertEqual(invoice.payer, None)
        self.assertFalse(invoice.is_valid())

    def testCreateFilled(self):
        invoice = Invoice({
            'number' : u'КЦ-111',
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',

            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            'position' : u'Верификация в информационной системе',
            'status' : 1,
            'duration_days':30,
            'price' : 1111
        })
        self.assertTrue(invoice.is_valid())

    def testFindByPayer(self):
        payer_id = bson.ObjectId()
        invoice = Invoice({
            'payer' : payer_id,
            'number' : u'КЦ-111',
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',

            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            'position' : u'Верификация в информационной системе',
            'status' : 1,
            'duration_days':30,
            'price' : 1111
        })
        invoice.save()
        one = self.collections['bill_items'].find_one({'payer' : payer_id})
        self.assertIsNotNone(one)
        two = invoice.objects.get_one_partial({'payer' : payer_id}, {'_id' : 1})
        self.assertIsNotNone(two)

    def test_pay_invoice(self):
        call_command("init_billing_accounts")
        self.register(verified=False)
        invoice = Invoice({
            'payer' : self.company._id,
            'number' : u'КЦ-123',
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',

            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            'position' : u'Верификация в информационной системе',
            'status' : InvoiceStatusEnum.CREATED,
            'duration_days':30,
            'price' : 1111
        })
        invoice.save()

        payment_order = {
            'n' : '19191',
            'date' : timezone.now(),
            'comment' : u"Верификация в информационной системе"
        }

        invoice_manager.set_paid(invoice, payment_order['n'], payment_order['date'], payment_order['comment'])

        company_account = Account.objects.get_one({'type' : Account.TYPE_COMPANY, 'details.subject_id' : self.company._id})
        self.assertIsNotNone(company_account)

        bank_account = Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID})
        tr = Transaction.objects.get_one({'source' : bank_account._id,
                                          'dest' : company_account._id})
        self.assertIsNotNone(tr)
        self.assertEqual(tr.amount, Currency.russian_roubles(invoice.price))

        invoice = Invoice.objects.get_one({'_id' : invoice._id})
        self.assertEqual(invoice.status, InvoiceStatusEnum.PAID)

    def test_rot(self):
        self.register(verified=False)
        invoice = Invoice({
            'payer' : self.company._id,
            'number' : u'КЦ-123',
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',

            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            'position' : u'Верификация в информационной системе',
            'status' : InvoiceStatusEnum.CREATED,
            'duration_days':30,
            'price' : 1111
        })
        invoice.save()

        invoice = Invoice.objects.get_one({'_id' : invoice._id})

        self.assertEqual(invoice.status, InvoiceStatusEnum.CREATED)
        invoice.expire_date = timezone.now() - timedelta(days=2)
        invoice.save()

        task = RotInvoicesTask()
        task.execute()

        invoice = Invoice.objects.get_one({'_id' : invoice._id})
        self.assertEqual(invoice.status, InvoiceStatusEnum.EXPIRED)
