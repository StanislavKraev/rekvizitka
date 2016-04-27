# -*- coding: utf-8 -*-
from datetime import timedelta
from bson.objectid import ObjectId
import random

from django.utils import timezone

from rek.billing.models import Currency
from rek.mongo.models import SimpleModel, ObjectManager

class Promotion(SimpleModel):
    STATE_ACTIVE = 0
    STATE_DISABLED = 1

    def __init__(self, kwargs):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')
        self.creation_date = kwargs.get('creation_date', timezone.now())
        self.start_date = kwargs.get('start_date', timezone.now())
        self.expires_date = kwargs.get('expires_date', timezone.now())
        self.state = kwargs.get('state', self.STATE_ACTIVE)
        self.comment = kwargs.get('comment', '')
        self.type = kwargs.get('type')

    def _is_active(self):
        if self.state != self.STATE_ACTIVE:
            return False
        if timezone.now() >= self.expires_date or timezone.now() < self.start_date:
            return False
        return True
    active = property(_is_active)

    def _fields(self):
        return {
            'creation_date' : self.creation_date,
            'start_date' : self.start_date,
            'expires_date' : self.expires_date,
            'state' : self.state,
            'comment' : self.comment,
            'type' : self.type
        }

Promotion.objects = ObjectManager(Promotion, 'promotions', [('expires_date', -1)])

class RegistrationPromoCode(SimpleModel):
    INVALID_CODE_VALUE = 0
    MIN_CODE_VALUE = 11111111
    MAX_CODE_VALUE = 99999999

    def __init__(self, kwargs):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')
        self.code = kwargs.get('code', self.INVALID_CODE_VALUE)
        self.promotion_id = kwargs.get('promotion_id')
        self.company_id = kwargs.get('company_id')
        self.used_date = kwargs.get('used_date')
        self.price = kwargs.get('price', Currency.russian_roubles(0))
        if self.price and not isinstance(self.price, Currency):
            self.price = Currency(self.price)

    def _is_used(self):
        if self.used_date and self.company_id:
            return True
        else:
            return False
    used = property(_is_used)

    def _is_active(self):
        if self.used:
            return False

        promo = Promotion.objects.get_one({'_id' : self.promotion_id})
        return promo is not None and promo.active

    active = property(_is_active)

    def use(self, company_id):
        if self.code < self.MIN_CODE_VALUE or self.code > self.MAX_CODE_VALUE:
            raise Exception('Invalid code id: %s. Can not use.' % unicode(self.code))

        if not isinstance(company_id, ObjectId):
            raise Exception('Invalid company id: %s' % unicode(company_id))

        if self.used:
            raise Exception('Promo code %s already used by company %s on %s.' %
                            (unicode(self.code),
                             unicode(self.company_id),
                             unicode(self.used_date)))

        self.used_date = timezone.now()
        self.company_id = company_id
        if not self._id:
            self.save()
        else:
            self.objects.update({'_id' : self._id}, {'$set' : {'used_date' : self.used_date,
                                                               'company_id' : self.company_id}})

    def _fields(self):
        return {
            'code' : self.code,
            'promotion_id' : self.promotion_id,
            'company_id' : self.company_id,
            'used_date' : self.used_date,
            'price' : self.price.fields()
        }

    @classmethod
    def generate_unique_code(cls):
        while True:
            promo_code = random.randrange(10000000,99999999)
            if not cls.objects.get_one({'code' : promo_code}):
                return promo_code

RegistrationPromoCode.objects = ObjectManager(RegistrationPromoCode, 'reg_promo_codes',
    [('promotion_id', 1),
        ('company_id', 1),
        ('used_date', -1)], [('code', 1)])

def create_reg_promotion(start_date, duration_days, comment, price, count):
    promotion = Promotion({'comment' : comment,
                           'start_date' : start_date,
                           'expires_date' : start_date + timedelta(days=duration_days),
                           'type' : 'registration'})
    promotion.save()

    try:
        for i in xrange(count):
            code_val = RegistrationPromoCode.generate_unique_code()
            promo_code = RegistrationPromoCode({'code' : code_val,
                                                'promotion_id' : promotion._id,
                                                'price' : price})
            promo_code.save()
    except Exception, ex:
        RegistrationPromoCode.objects.collection.remove({'promotion_id' : promotion._id})
        Promotion.objects.collection.remove({'_id' : promotion._id})
        raise ex
