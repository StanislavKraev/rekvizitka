# -*- coding: utf-8 -*-

from django.core.cache import cache

from rek.mongo.models import ObjectManager

# todo: create system-wide singleton. So only 1 process who can change settings is available.

class RekSettings(object):
    objects = None

    DEFAULTS = [('company_auto_index', 1000),
        ('bill_auto_index', 1000),
        ('verify_bill_price', 1000),
        ('registration_promo_action_amount', 1000),
        ('rekvizitka_bank_account', {
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',
            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
        }),
        ('rnes', 1),
        ('rmax', 5),
        ('rtimeout', 24 * 7),
        ('verifylettercount', 4),
        ('verifyletterdelaydays', 7),
        ('invite_bonus', 500),
    ]

    def __init__(self):
        for item in self.DEFAULTS:
            obj = self.objects.collection.find_one({'name' : item[0]})
            if not obj:
                self.objects.collection.insert({'name' : item[0], 'value' : item[1]})

        items_cursor = self.objects.collection.find()
        for item in items_cursor:
            cache.set(item['name'], item['value'])

    def get_property(self, name):
        value = cache.get(name)
        if not value:
            object = self.objects.collection.find_one({'name' : name})
            if object:
                cache.set(name, object['value'])
            return object['value']
        return value

    def set_property(self, name, value):
        self.objects.collection.update({'name' : name}, {'$set' : {'value' : value}})
        cache.set(name, value)

    def inc_and_return_property(self, name, inc_value = 1):
        new_property_val = self.objects.collection.find_and_modify({'name' : name}, {'$inc' : {'value' : inc_value}})
        value = new_property_val['value']
        try:
            mem_val = cache.incr(name, inc_value)
            if mem_val != value:
                raise ValueError('Data divergence')
        except ValueError:
            cache.set(name, value)
        return value

RekSettings.objects = ObjectManager(RekSettings, 'rek_settings', [], [('name', 1)])
SettingsManager = RekSettings()
