# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from rek.billing.models import Account
from rek.rekvizitka.models import Company

class Command(BaseCommand):
    help = u'Initialize billing accounts\n'

    def handle(self, *args, **options):
        print('Initializing billing accounts...')

        for company in Company.objects.get({}):
            if not Account.objects.count({'details.subject_id':company._id, 'type' : Account.TYPE_COMPANY}):
                account = Account({"name" : "Счет компании",
                                   "type" : Account.TYPE_COMPANY,
                                   "details" : {'subject_id' : company._id}})
                account.save()

        if not Account.objects.get_one({'system_id' : Account.FIXED_ADS_ACCOUNT_ID}):
            account = Account({"system_id" : Account.FIXED_ADS_ACCOUNT_ID,
                               "name" : "Счет рекламных услуг",
                               "type" : Account.TYPE_VIRTUAL})
            account.save()

        if not Account.objects.get_one({'system_id' : Account.FIXED_PROMO_ACCOUNT_ID}):
            account = Account({"system_id" : Account.FIXED_PROMO_ACCOUNT_ID,
                               "name" : "Счет промо-акцийг",
                               "type" : Account.TYPE_VIRTUAL})
            account.save()

        if not Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID}):
            account = Account({"system_id" : Account.FIXED_BANK_ACCOUNT_ID,
                               "name" : "Банковский счет",
                               "type" : Account.TYPE_VIRTUAL})
            account.save()

        print('Done!')