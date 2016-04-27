# -*- coding: utf-8 -*-
from decimal import *
from billing.models import Currency, CurrencyExchangeManager

from rek.tests.base import BaseTestCase

class CurrencyTestCase(BaseTestCase):
    def test_init(self):
        two_roubles = Currency({'code' : 'RUB', 'rate' : 1, 'amount' : 2})
        self.assertEqual(two_roubles.code, 'RUB')
        self.assertIsInstance(two_roubles.amount, Decimal)
        self.assertEqual(two_roubles.amount, Decimal(2))

        self.assertIsInstance(two_roubles.rate, Decimal)
        self.assertEqual(two_roubles.rate, Decimal(1))

    def test_roubles(self):
        one_rouble = Currency.russian_roubles(1)

        self.assertEqual(one_rouble.code, 'RUB')
        self.assertIsInstance(one_rouble.amount, Decimal)
        self.assertEqual(one_rouble.amount, Decimal(1))

        self.assertIsInstance(one_rouble.rate, Decimal)
        self.assertEqual(one_rouble.rate, Decimal(1))

    def test_usd(self):
        five_dollars = Currency.us_dollars(5, Decimal("1.5"))

        self.assertEqual(five_dollars.code, 'USD')
        self.assertIsInstance(five_dollars.amount, Decimal)
        self.assertEqual(five_dollars.amount, Decimal(5))

        self.assertIsInstance(five_dollars.rate, Decimal)
        self.assertEqual(five_dollars.rate, Decimal("1.5"))

    def test_neg(self):
        five_dollars = Currency.us_dollars(5, Decimal("1.5"))
        self.assertEqual(five_dollars.amount, Decimal(5))
        self.assertEqual((-five_dollars).amount, Decimal(-5))

    def test_calculate_sum_same_currency(self):
        two_dollars = Currency.us_dollars(2, 3)
        seven_dollars = Currency.us_dollars(7, 4)

        self.assertEqual(two_dollars + seven_dollars, Currency.russian_roubles(34))

    def test_calculate_sum_diff_currency(self):
        two_dollars = Currency.us_dollars(2, 3)
        five_roubles = Currency.russian_roubles(5)

        self.assertEqual(two_dollars + five_roubles, Currency.russian_roubles(11))

    def test_calculate_diff_same_currency(self):
        two_dollars = Currency.us_dollars(2, 3)
        seven_dollars = Currency.us_dollars(7, 4)

        self.assertEqual(seven_dollars - two_dollars, Currency.russian_roubles(22))

    def test_calculate_diff_diff_currency(self):
        two_dollars = Currency.us_dollars(2, 3)
        five_roubles = Currency.russian_roubles(5)

        self.assertEqual(two_dollars - five_roubles, Currency.russian_roubles(1))

    def test_currency_exchange_reduce(self):
        two_dollars = Currency.us_dollars(2, 3)
        self.assertEqual(CurrencyExchangeManager.reduce(two_dollars), Currency.russian_roubles(60))
        self.assertNotEqual(CurrencyExchangeManager.reduce(two_dollars, 'USD'), Currency.russian_roubles(60))
        self.assertNotEqual(CurrencyExchangeManager.reduce(two_dollars, 'USD'), Currency.us_dollars(2, CurrencyExchangeManager.exchange_rates['USD']))
        self.assertEqual(CurrencyExchangeManager.reduce(two_dollars, 'USD'), Currency.us_dollars(2, 3))

    def test_currency_exchange_sum_one(self):
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3)]), Currency.russian_roubles(60))
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3)], 'USD'), Currency.us_dollars(2, 3))

    def test_currency_exchange_sum_two(self):
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3),
                                                      Currency.us_dollars(3, 5)]), Currency.russian_roubles(150))
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3),
                                                      Currency.us_dollars(3, 5)], 'USD'), Currency.us_dollars(5,
                         CurrencyExchangeManager.exchange_rates['USD']))

    def test_currency_exchange_sum_list(self):
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3),
                                                      Currency.us_dollars(3, 5),
                                                      Currency.russian_roubles(60)], 'USD'), Currency.us_dollars(7,
            CurrencyExchangeManager.exchange_rates['USD']))
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3),
                                                      Currency.us_dollars(3, 5),
                                                      Currency.russian_roubles(60)]), Currency.russian_roubles(210))
        self.assertEqual(CurrencyExchangeManager.sum([Currency.us_dollars(2, 3),
                                                      Currency.us_dollars(3, 5),
                                                      Currency.russian_roubles(60),
                                                      Currency.euro(4, 90)], 'EUR'), Currency.euro(Decimal('8.66666666666666667'),
                                                                                                   CurrencyExchangeManager.exchange_rates['EUR']))
