# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

class CompanyAccountStatus(object):
    JUST_REGISTERED = 'just_registered'
    VERIFIED = 'verified'
    SEMI_VERIFIED = 'semi_verified'

    ACTIVE_ACCOUNT_STATUSES = (VERIFIED, SEMI_VERIFIED)
    ALL = (JUST_REGISTERED, VERIFIED, SEMI_VERIFIED)

    @classmethod
    def is_active_account(cls, status):
        return status in cls.ACTIVE_ACCOUNT_STATUSES

    @classmethod
    def to_string(cls, status):
        if status == cls.JUST_REGISTERED:
            return _(u'Не проверен (не активен)')
        elif status == cls.VERIFIED:
            return _(u'Проверен')
        elif status == cls.SEMI_VERIFIED:
            return _(u'Серая компания')
        return _(u"Неизвестно")

    @classmethod
    def choices(cls):
        return [(status, cls.to_string(status)) for status in cls.ALL]