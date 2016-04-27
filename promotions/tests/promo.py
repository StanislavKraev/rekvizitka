# -*- coding: utf-8 -*-
from datetime import timedelta
from django.core import mail
from django.core.management import call_command

from django.utils import timezone
from rek.billing.models import Currency

from rek.promotions.models import Promotion, create_reg_promotion, RegistrationPromoCode
from rek.rekvizitka.models import Company
from rek.tests.base import BaseTestCase

class PromotionsTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'user_activation_links',
                        'reg_promo_codes', 'promotions']

    def test_create_registration_promotion(self):
        self.assertLessEqual(Promotion.objects.count(), 0)
        self.assertLessEqual(RegistrationPromoCode.objects.count(), 0)
        create_reg_promotion(timezone.now(), 30, "test promo", Currency.russian_roubles(1000), 20)
        self.assertEqual(Promotion.objects.count(), 1)
        self.assertEqual(RegistrationPromoCode.objects.count(), 20)

    def test_use_reg_promo(self):
        self.register()
        create_reg_promotion(timezone.now(), 30, "test promo", Currency.russian_roubles(1000), 1)
        code = RegistrationPromoCode.objects.get({})[0]
        self.assertIsNotNone(code)

        company = Company.objects.get({})[0]
        code.use(company._id)

    def test_register_with_promo(self):
        call_command("init_billing_accounts")
        promotion = Promotion({'count' : 1,
                               'start_date' : timezone.now() - timedelta(days=1),
                               'expires_date' : timezone.now() + timedelta(days=1)})
        promotion.save()
        promo_code = RegistrationPromoCode({'code' : 12345678,
                                            'promotion_id' : promotion._id,
                                            'price' : Currency.russian_roubles(100)})
        promo_code.save()
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'promo_code_part1' : unicode(promo_code.code)[:4],
            'promo_code_part2' : unicode(promo_code.code)[4:],
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        company = Company.objects.get({})[0]
        self.assertEqual(len(mail.outbox), 2)

        self.assertEqual(len(RegistrationPromoCode.objects.get({'company_id' : company._id})), 1)
        code = RegistrationPromoCode.objects.get({'company_id' : company._id})[0]
        self.assertIsNotNone(code)
        self.assertTrue(code.used)
        self.assertRaises(KeyError, response.context.__getitem__, 'promo_code_error')

    def test_register_with_missed_promo(self):
        call_command("init_billing_accounts")
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'promo_code_part1' : u'1234',
            'promo_code_part2' : u'5678',
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(Company.objects.get({})), 0)
        self.assertEqual(response.context['promo_code_error'], True)

    def test_register_with_used_promo(self):
        call_command("init_billing_accounts")
        promotion = Promotion({'count' : 1,
                               'start_date' : timezone.now() - timedelta(days=1),
                               'expires_date' : timezone.now() + timedelta(days=1)})
        promotion.save()
        promo_code = RegistrationPromoCode({'code' : 12345678,
                                            'promotion_id' : promotion._id,
                                            'price' : Currency.russian_roubles(100)})
        promo_code.save()
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'promo_code_part1' : unicode(promo_code.code)[:4],
            'promo_code_part2' : unicode(promo_code.code)[4:],
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertRaises(KeyError, response.context.__getitem__, 'promo_code_error')
        company = Company.objects.get({})[0]

        self.assertEqual(len(RegistrationPromoCode.objects.get({'company_id' : company._id})), 1)
        code = RegistrationPromoCode.objects.get({'company_id' : company._id})[0]
        self.assertIsNotNone(code)
        self.assertTrue(code.used)

        response = self.client.post('/', {
            'email' : 'test2@testunavailabledomain.ru',
            'brand_name' : 'Company brand name2',
            'password' : 'aaabbb2',
            'promo_code_part1' : unicode(promo_code.code)[:4],
            'promo_code_part2' : unicode(promo_code.code)[4:],
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(Company.objects.get({})), 1)
        self.assertEqual(response.context['promo_code_error'], True)

    def test_register_with_not_active_promo(self):
        call_command("init_billing_accounts")
        promotion = Promotion({'count' : 1,
                               'start_date' : timezone.now() - timedelta(days=1),
                               'expires_date' : timezone.now() - timedelta(days=1)})
        promotion.save()
        promo_code = RegistrationPromoCode({'code' : 12345678,
                                            'promotion_id' : promotion._id,
                                            'price' : Currency.russian_roubles(100)})
        promo_code.save()
        response = self.client.post('/', {
            'email' : 'test@testunavailabledomain.ru',
            'brand_name' : 'Company brand name',
            'password' : 'aaabbb',
            'promo_code_part1' : unicode(promo_code.code)[:4],
            'promo_code_part2' : unicode(promo_code.code)[4:],
            'join' : 'join'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('promo_code_error', response.context)
        self.assertEqual(response.context['promo_code_error'], True)
