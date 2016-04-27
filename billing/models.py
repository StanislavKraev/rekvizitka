# -*- coding: utf-8 -*-

from decimal import *
from datetime import  timedelta

from bson.objectid import ObjectId
from django.utils import timezone, simplejson

from rek.mongo.models import ObjectManager, SimpleModel

getcontext().prec = 18

class InvoiceStatusEnum(object):
    CREATED = 0
    PAID = 1
    EXPIRED = 2

    ALL_VALUES = (CREATED, PAID, EXPIRED)

    @classmethod
    def choices(cls):
        return ((cls.CREATED, cls.type_to_name(cls.CREATED)),
                (cls.PAID, cls.type_to_name(cls.PAID)),
                (cls.EXPIRED, cls.type_to_name(cls.EXPIRED)),)

    @classmethod
    def type_to_name(cls, type):
        if type == cls.CREATED:
            return u'создан'
        elif type == cls.PAID:
            return u'оплачен'
        elif type == cls.EXPIRED:
            return u'просрочен'
        return u'-'

class Invoice(SimpleModel):
    def __init__(self, kwargs=None):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')                        #    id = BigAutoField(primary_key=True)
        self.payer = kwargs.get('payer')    #    payer = models.ForeignKey(User, verbose_name='клиент')
        self.number = kwargs.get('number')                  #    number = models.CharField(max_length=255, verbose_name='номер счета')
        self.recipient = kwargs.get('recipient')            #    recipient = models.CharField(max_length=255, verbose_name='получатель')
        self.address = kwargs.get('address')                #    address = models.CharField(max_length=255, verbose_name='адрес получателя')
        self.account = kwargs.get('account')                #    account = models.CharField(max_length=20, verbose_name='счет получателя')
        self.account_name = kwargs.get('account_name')      #    account_name = models.CharField(max_length=255, verbose_name='ИНН_КПП')

        self.bank_name = kwargs.get('bank_name')            #    bank_name = models.CharField(max_length=255, verbose_name='банк получателя')
        self.bank_bik = kwargs.get('bank_bik')              #    bank_bik = models.IntegerField(verbose_name='бик банка получателя', validators=[MaxValueValidator(999999999), MinValueValidator(100000000)])
        self.bank_account = kwargs.get('bank_account')      #    bank_account = models.CharField(max_length=20, verbose_name='офис')

        self.status = kwargs.get('status', InvoiceStatusEnum.CREATED)  #    status = models.SmallIntegerField(verbose_name='статус счета', choices=BillStatusEnum.choices(), default=BillStatusEnum.CREATED, null=True, blank=True)
        self.comment = kwargs.get('comment', '')                        #    comment = models.TextField(verbose_name='комментарий', null=True, blank=True)
        self.create_date = kwargs.get('create_date', timezone.now())#    create_date = models.DateField(auto_now_add=True, verbose_name='дата создания')
        self.pay_date = kwargs.get('pay_date')                      #    pay_date = models.DateField(blank = True, null=True, verbose_name='дата оплаты')
        self.duration_days = kwargs.get('duration_days')            #    duration_days=models.IntegerField(verbose_name='срок действия (дней)')
        self.expire_date = kwargs.get('expire_date', self.create_date + timedelta(days=self.duration_days)) \
                            if self.create_date and self.duration_days \
                            else None
        self.position = kwargs.get('position')                      #    position = models.CharField(max_length=255, verbose_name='услуга', blank=True, null=True)

        self.price = kwargs.get('price', 0)                 #    price=models.IntegerField(verbose_name='стоимость (руб)', default=1)
        self.service = kwargs.get('service')

    def show_fields(self):
        fields = self._fields()
        for field in fields:
            fields[field] = unicode(fields[field])
        return fields

    def _fields(self):
        fields = {
            'payer' : self.payer,
            'number' : self.number,
            'recipient' : self.recipient,
            'address' : self.address,
            'account' : self.account,
            'account_name' : self.account_name,

            'bank_name' : self.bank_name,
            'bank_bik' : self.bank_bik,
            'bank_account' : self.bank_account,

            'status' : self.status,
            'comment' : self.comment,
            'create_date' : self.create_date,
            'pay_date' : self.pay_date,
            'duration_days' : self.duration_days,
            'expire_date' : self.expire_date,
            'position' : self.position,

            'price' : self.price,
            'service' : self.service
        }
        return fields

    def is_valid(self):
        valid = self.number is not None and len(self.number) > 0
        valid &= self.recipient is not None and len(self.recipient) > 0
        valid &= self.address is not None and len(self.address) > 0
        valid &= self.account is not None and len(self.account) > 0
        valid &= self.account_name is not None and len(self.account_name) > 0
        valid &= self.bank_name is not None and len(self.bank_name) > 0
        valid &= self.bank_bik is not None
        valid &= self.bank_account is not None and len(self.bank_account) > 0
        valid &= self.position is not None and len(self.position) > 0
        valid &= self.status is not None and self.status in InvoiceStatusEnum.ALL_VALUES
        valid &= self.duration_days is not None and self.duration_days > 0 and self.duration_days < 365 * 10
        if not self.duration_days:
            return False
        valid &= self.price and self.price > 0 and self.price < 1000000000000
        valid &= self.comment is not None
        return valid

    def save(self):
        if not self.is_valid():
            raise Exception('Incorrect bill (%s). Can not save to db.' % simplejson.dumps(self.show_fields()))
        return super(Invoice, self).save()

Invoice.objects = ObjectManager(Invoice, 'bill_items', [('payer', 1), ('number', 1), ('expire_date', -1)])

class MaxCurrencyException(Exception):
    pass

class Currency(object):
    CODE_RUSSIAN_RUBLE = 'RUB'
    CODE_US_DOLLAR = 'USD'
    CODE_EURO = 'EUR'
    CODE_HRYVNIA = 'UAH'
    CODE_BELORUSSIAN_RUBLE = 'BYR'
    CODE_POUND_STERLING = 'GBP'
    CODE_NEW_ISRAELI_SHEQEL = 'ILS'
    CODE_NO_CURRENCY = 'XXX'
    CODE_TEST_CURRENCY = 'XTS'

    BASE_CURRENCY = CODE_RUSSIAN_RUBLE

    MAX_VAL = 9999999999
    DB_MULTIPLIER = Decimal(100000000)

    def _code_get(self):
        return self._code
    code = property(_code_get)

    def _rate_get(self):
        return self._rate
    rate = property(_rate_get)

    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        if not isinstance(kwargs, dict):
            raise Exception('incorrect initial data')
        self._code = kwargs.get('code', self.CODE_NO_CURRENCY)
        self._rate = kwargs.get('rate', Decimal(1))
        if not isinstance(self._rate, Decimal):
            self._rate = Decimal(self._rate)

        self.amount = kwargs.get('amount', Decimal(0))
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount)

        if int(self._rate * self.amount) > self.MAX_VAL:
            raise MaxCurrencyException('Too big currency amount: %s' % repr(self))

    def fields(self):
        return {'code' : self._code,
                'rate' : unicode(self._rate),
                'amount' : unicode(self.amount)}

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.amount == other.amount and self._rate == other._rate and self._code == other._code

    def __unicode__(self):
        return "%s %s" % (unicode(self.amount), self.code)

    def __repr__(self):
        return "%s %s (rate: %s)" % (repr(self.amount), self.code, repr(self._rate))

    def __neg__(self):
        return Currency({'code' : self._code, 'amount' : -self.amount, 'rate' : self._rate})

    def __add__(self, other):
        return Currency.russian_roubles(self.rate * self.amount + other.rate * other.amount)

    def __sub__(self, other):
        return Currency.russian_roubles(self.rate * self.amount - other.rate * other.amount)

    @classmethod
    def russian_roubles(cls, amount):
        return cls({'code' : cls.CODE_RUSSIAN_RUBLE,
                    'amount' : amount,
                    'rate' : 1})

    @classmethod
    def us_dollars(cls, amount, rate):
        return cls({'code' : cls.CODE_US_DOLLAR,
                    'amount' : amount,
                    'rate' : rate})

    @classmethod
    def euro(cls, amount, rate):
        return cls({'code' : cls.CODE_EURO,
                    'amount' : amount,
                    'rate' : rate})

    def db_value(self):
        return int(self.amount * self.rate * self.DB_MULTIPLIER)

    @classmethod
    def from_db_value(cls, db_value):
        return cls({'code' : cls.CODE_RUSSIAN_RUBLE,
                    'rate' : 1,
                    'amount' : Decimal(db_value) / cls.DB_MULTIPLIER})

class CurrencyReduceException(Exception):
    pass

class CurrencyExchange(object):
    def __init__(self):
        self.exchange_rates = {}
        self.load_rates()

    def load_rates(self):
        self.exchange_rates.update({Currency.CODE_RUSSIAN_RUBLE : Decimal(1),
                                    Currency.CODE_US_DOLLAR : Decimal(30),
                                    Currency.CODE_NO_CURRENCY : Decimal(0),
                                    Currency.CODE_TEST_CURRENCY : Decimal(1),
                                    Currency.CODE_EURO : Decimal(45)})

    def sum(self, currency_array, to = Currency.CODE_RUSSIAN_RUBLE):
        if not currency_array:
            return self.reduce(Currency.russian_roubles(0), to)

        if len(currency_array) == 1:
            return self.reduce(currency_array[0], to)

        if to not in self.exchange_rates:
            raise CurrencyReduceException("Can't reduce currency to %s - do not know exchange rate." % to)

        if currency_array[0].code not in self.exchange_rates:
            raise CurrencyReduceException("Can't reduce currency %s - do not know exchange rate." % unicode(currency_array[0]))

        result_amount = currency_array[0].amount * self.exchange_rates[currency_array[0].code]
        for cur in currency_array[1:]:
            if cur.code not in self.exchange_rates:
                raise CurrencyReduceException("Can't reduce currency %s - do not know exchange rate." % unicode(cur))
            result_amount += cur.amount * self.exchange_rates[cur.code]
        to_rate = self.exchange_rates[to]
        return Currency({'code' : to, 'amount' : result_amount / to_rate, 'rate' : to_rate})

    def reduce(self, currency, to = Currency.CODE_RUSSIAN_RUBLE):
        if currency.code == to:
            return currency

        if currency.code not in self.exchange_rates:
            raise CurrencyReduceException("Can't reduce currency %s - do not know exchange rate." % unicode(currency))

        if to not in self.exchange_rates:
            raise CurrencyReduceException("Can't reduce currency to %s - do not know exchange rate." % to)

        result = Currency({'code' : to,
                           'amount' : self.exchange_rates[currency.code] * currency.amount / self.exchange_rates[to],
                           'rate' : self.exchange_rates[to]})
        return result

CurrencyExchangeManager = CurrencyExchange()

class Account(SimpleModel):
    TYPE_UNKNOWN = 0
    TYPE_EMPLOYEE = 1
    TYPE_COMPANY = 2
    TYPE_VIRTUAL = 3
    TYPE_BANK = 4

    FIXED_PROMO_ACCOUNT_ID = ObjectId('4fa279d9c52be42506000001')
    FIXED_BANK_ACCOUNT_ID = ObjectId('4fa279dac52be42506000002')
    FIXED_ADS_ACCOUNT_ID = ObjectId('4fa279dcc52be42506000003')

    def __init__(self, kwargs = None):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')
        self.name = kwargs.get('name', '')
        self.system_id = kwargs.get('system_id')
        self._type = kwargs.get('type', self.TYPE_UNKNOWN)
        self._balance = kwargs.get('balance', 0)
        if self._balance and isinstance(self._balance, Currency):
            self._balance = CurrencyExchangeManager.reduce(self._balance).amount

        self.details = kwargs.get('details', {})
        self.pending_transactions = kwargs.get('pending_transactions', [])

    def _balance_get(self):
        return Currency.from_db_value(self._balance)

    balance = property(_balance_get)

    def _type_get(self):
        return self._type
    type = property(_type_get)

    def _fields(self):
        fields = {
            'name' : self.name,
            'type' : self._type,
            'balance' : self._balance,
            'details' : self.details,
            'pending_transactions' : self.pending_transactions
        }
        if self.system_id:
            fields['system_id'] = self.system_id
        return fields

Account.objects = ObjectManager(Account, 'billing_accounts', [('details.subject_id', 1), ('system_id', 1)])

class Transaction(SimpleModel):
    STATE_INITIAL = 0
    STATE_PENDING = 1
    STATE_COMMITTED = 2
    STATE_DONE = 3

    def __init__(self, kwargs = None):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')
        self.source_account = kwargs.get('source')
        self.dest_account = kwargs.get('dest')
        self.amount = kwargs.get('amount')
        if self.amount and not isinstance(self.amount, Currency):
            self.amount = Currency(self.amount)
        self.state = kwargs.get('state', self.STATE_INITIAL)
        self.created = kwargs.get('created', timezone.now())
        self.started = kwargs.get('started')
        self.finished = kwargs.get('finished')
        self.comment = kwargs.get('comment')

    def apply(self):
        if not self.amount or not isinstance(self.amount, Currency):
            raise Exception('Invalid transaction amount: %s' % unicode(self.amount))

        self.state = self.STATE_PENDING
        self.started = timezone.now()
        Transaction.objects.update({'_id': self._id},
                                   {'$set': {'state': self.state, 'started' : self.started}})

        amount_rub = self.amount.db_value()

        Account.objects.update({'_id': self.source_account, 'pending_transactions': {'$ne': self._id}},
                               {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': self._id}})

        Account.objects.update({'_id': self.dest_account, 'pending_transactions': {'$ne': self._id}},
                               {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': self._id}})

        self.state = self.STATE_COMMITTED
        Transaction.objects.update({'_id': self._id}, {'$set': {'state': self.state}})

        Account.objects.update({'_id': self.source_account},
                               {'$pull': {'pending_transactions': self._id}})

        Account.objects.update({'_id': self.dest_account},
                               {'$pull': {'pending_transactions': self._id}})

        self.state = self.STATE_DONE
        self.finished = timezone.now()
        Transaction.objects.update({'_id': self._id},
                                   {'$set': {'state': self.state, 'finished' : self.finished}})

    def complete(self):
        if self.state in (self.STATE_DONE, self.STATE_INITIAL):
            return
        if self.state == self.STATE_PENDING:
            amount_rub = self.amount.db_value()

            Account.objects.update({'_id': self.source_account, 'pending_transactions': {'$ne': self._id}},
                    {'$inc': {'balance': -amount_rub}, '$push': {'pending_transactions': self._id}})

            Account.objects.update({'_id': self.dest_account, 'pending_transactions': {'$ne': self._id}},
                    {'$inc': {'balance': amount_rub}, '$push': {'pending_transactions': self._id}})

            self.state = self.STATE_COMMITTED
            Transaction.objects.update({'_id': self._id}, {'$set': {'state': self.state}})

        if self.state == self.STATE_COMMITTED:
            Account.objects.update({'_id': self.source_account},
                    {'$pull': {'pending_transactions': self._id}})

            Account.objects.update({'_id': self.dest_account},
                    {'$pull': {'pending_transactions': self._id}})

            self.state = self.STATE_DONE
            Transaction.objects.update({'_id': self._id}, {'$set': {'state': self.state}})

    def _fields(self):
        return {
            'source' : self.source_account,
            'dest' : self.dest_account,
            'amount' : self.amount.fields(),
            'state' : self.state,
            'created' : self.created,
            'started' : self.started,
            'finished' : self.finished,
            'comment' : self.comment
        }

Transaction.objects = ObjectManager(Transaction, 'billing_transactions', [('created', -1), ('finished', -1)])
