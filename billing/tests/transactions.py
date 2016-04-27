# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
from billing.models import Currency, Transaction, Account, MaxCurrencyException
from cron.cron_tasks_manager import cron_tasks_manager
from rek.billing.cron import RepairTransactionsTask

from rek.tests.base import BaseTestCase

class TransactionsTestCase(BaseTestCase):
    collection_names = ['billing_accounts', 'billing_transactions', 'deferred_notifications']
    def setUp(self):
        super(TransactionsTestCase, self).setUp()
        self.user1_account = self.create_account('user1_account')
        self.user2_account = self.create_account('user2_account')

    def create_account(self, name):
        account = Account({'name' : name,
                           'type' : Account.TYPE_EMPLOYEE,
                           'details' : {'subject_id' : ObjectId()}})
        account.save()
        return account

    def test_money_transfer(self):
        value = Currency.russian_roubles("123.43")
        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()
        transaction.apply()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})

        self.assertEqual(account1.balance, -value)
        self.assertEqual(account2.balance, value)

    def test_currency_ranges(self):
        Currency.russian_roubles("9999999999.99123459")
        self.assertRaises(MaxCurrencyException, Currency.russian_roubles, "19999999999.99123459")

        self.assertEqual(Currency.russian_roubles("9999999999.99123459").db_value(), 999999999999123459)
        self.assertEqual(Currency.russian_roubles("9999999999.99123459123").db_value(), 999999999999123459)

        self.assertEqual(Currency.euro("999999999.991234591", 10).db_value(), 999999999991234591)
        self.assertEqual(Currency.us_dollars("9111111.991234591", 1058).db_value(), 963955648672619728)
        self.assertEqual(Currency.us_dollars("9111111.991234591123123123", 1058).db_value(), 963955648672619741)

        self.assertEqual(Currency.euro("0.000000000001", 120).db_value(), 0)
        self.assertEqual(Currency.euro("0.0000000001", 100).db_value(), 1)

    def test_floats(self):
        value = Currency.russian_roubles("9999999999.99123459")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()
        transaction.apply()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})

        self.assertEqual(account1.balance, -value)
        self.assertEqual(account2.balance, value)

        new_value = Currency.russian_roubles("-10.99122459")
        value += new_value

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : new_value})
        transaction.save()
        transaction.apply()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})

        self.assertEqual(account1.balance, -value)
        self.assertEqual(account2.balance, value)

    def test_floats_usd(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()
        transaction.apply()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})

        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

        new_value = Currency.russian_roubles("-10.99122459")
        value += new_value

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : new_value})
        transaction.save()
        transaction.apply()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})

        self.assertEqual(account1.balance, -value)
        self.assertEqual(account2.balance, value)

    def test_complete_after_pending1(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to pending
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_complete_after_pending2(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to pending
        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                               {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})
        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_complete_after_pending3(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to pending
        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Account.objects.update({'_id': account2._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': transaction._id}})
        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_complete_after_committed1(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to committed
        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Account.objects.update({'_id': account2._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_COMMITTED}})

        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_complete_after_committed2(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to committed
        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Account.objects.update({'_id': account2._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_COMMITTED}})
        Account.objects.update({'_id': account1._id},
                {'$pull': {'pending_transactions': transaction._id}})

        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_complete_after_committed3(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        # partial transaction.apply() - up to committed
        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Account.objects.update({'_id': account2._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': transaction._id}})
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_COMMITTED}})
        Account.objects.update({'_id': account1._id},
                {'$pull': {'pending_transactions': transaction._id}})
        Account.objects.update({'_id': account2._id},
                {'$pull': {'pending_transactions': transaction._id}})

        transaction = Transaction.objects.get_one({'_id' : transaction._id})

        transaction.complete()

        account1 = Account.objects.get_one({'_id' : account1._id})
        account2 = Account.objects.get_one({'_id' : account2._id})
        trans = Transaction.objects.get_one({'_id' : transaction._id})

        self.assertEqual(trans.state, Transaction.STATE_DONE)
        self.assertEqual(account1.balance.amount, -value.amount * value.rate)
        self.assertEqual(account2.balance.amount, value.amount * value.rate)

    def test_cron_transaction_repair(self):
        value = Currency.us_dollars("99999999.99123459", "30.12342")

        account1 = self.user1_account
        account2 = self.user2_account

        transaction = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : value})
        transaction.save()

        amount_rub = transaction.amount.db_value()
        Transaction.objects.update({'_id': transaction._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction._id}},
                {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': transaction._id}})

        transaction2 = Transaction({'source' : account1._id, 'dest' : account2._id, 'amount' : -value})
        transaction2.save()

        amount_rub2 = transaction2.amount.db_value()
        Transaction.objects.update({'_id': transaction2._id}, {'$set': {'state': Transaction.STATE_PENDING}})
        Account.objects.update({'_id': account1._id, 'pending_transactions': {'$ne': transaction2._id}},
                {'$inc': {'balance': -amount_rub2}, '$push': {'pending_transactions': transaction2._id}})

        bad_transactions = Transaction.objects.get({'state' : {'$nin' : [Transaction.STATE_INITIAL, Transaction.STATE_DONE]}})
        self.assertTrue(len(bad_transactions) > 0)

        task = RepairTransactionsTask()
        task.execute()

        bad_transactions = Transaction.objects.get({'state' : {'$nin' : [Transaction.STATE_INITIAL, Transaction.STATE_DONE]}})
        self.assertEquals(len(bad_transactions), 0)
