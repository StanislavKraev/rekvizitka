# -*- coding: utf-8 -*-

from rek.mongo.models import ObjectManager, SimpleModel

class ContractorStatusEnum(object):
    RECEIVED = 0 #when contractor send to contracor(first time view this request)
    DECLINED = 1
    ACCEPTED = 2

    @classmethod
    def choices(cls):
        return ((cls.DECLINED, cls.type_to_name(cls.DECLINED)),
                (cls.ACCEPTED, cls.type_to_name(cls.ACCEPTED)),
                (cls.RECEIVED, cls.type_to_name(cls.RECEIVED)))

    @classmethod
    def type_to_name(cls, type):
        if type == cls.DECLINED:
            return u'отклонена'
        elif type == cls.ACCEPTED:
            return u'подтверждена'
        elif type == cls.RECEIVED:
            return u'получена'
        return u'-'

class ContractorPrivacy(object):
    VISIBLE_EVERYONE = 'everyone'
    VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS = 'empl_contr_their_contr'
    VISIBLE_OUR_EMPLOYEES_CONTRACTORS = 'empl_contr'
    VISIBLE_OUR_EMPLOYEES = 'employees'
    VISIBLE_OUR_ADMINS = 'our_admins'

    ALL = (VISIBLE_EVERYONE,
           VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS,
           VISIBLE_OUR_EMPLOYEES_CONTRACTORS,
           VISIBLE_OUR_EMPLOYEES,
           VISIBLE_OUR_ADMINS)

    @classmethod
    def to_string(cls, val):
        if val == cls.VISIBLE_EVERYONE:
            return u'всем'
        elif type == cls.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS:
            return u'только нашим сотрудникам, контрагентам и их контрагентам'
        elif type == cls.VISIBLE_OUR_EMPLOYEES_CONTRACTORS:
            return u'только нашим сотрудникам и контрагентам'
        elif type == cls.VISIBLE_OUR_EMPLOYEES:
            return u'только нашим сотрудникам'
        elif type == cls.VISIBLE_OUR_ADMINS:
            return u'только администраторам компании'
        return u'неизвестно'

class Contractor(SimpleModel):
    def __init__(self, kwargs):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.company_1 = kwargs.get('company_1')
        self.company_2 = kwargs.get('company_2')
        self.company_1_data = kwargs.get('company_1_data', {})
        self.company_2_data = kwargs.get('company_2_data', {})
        self.status = kwargs.get('status', ContractorStatusEnum.RECEIVED)
        self.viewed = kwargs.get('viewed', False)

    def _fields(self):
        fields = {
            'company_1' : self.company_1,
            'company_2' : self.company_2,
            'viewed' : self.viewed,
            'status' : self.status,
            'company_1_data' : self.company_1_data,
            'company_2_data' : self.company_2_data
        }

        return fields

    @classmethod
    def set_indexes(cls):
        cls.objects.collection.ensure_index([('company_1', 1), ('company_2', 1)], unique=True)

Contractor.objects = ObjectManager(Contractor, 'contractors')
Contractor.set_indexes()
