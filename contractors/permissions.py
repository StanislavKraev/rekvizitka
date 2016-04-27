# -*- coding: utf-8 -*-

from rek.contractors.models import ContractorPrivacy, Contractor
from rek.rekvizitka.models import Company

class ContractorPermission(object):
    def __init__(self, my_company, target_company):
        self.my_company = my_company
        self.target_company = target_company
        self.own = False if not my_company else my_company._id == target_company._id
        self.are_we_contractors = False if not my_company or self.own else self.check_in_contractors(my_company, target_company.contractors)
        self.target_company_verified = True # todo
        self.is_admin = True # todo

    def check_in_contractors(self, my_company, target_company_contractors):
        for contractor in target_company_contractors:
            if my_company._id == contractor['company_id']:
                return True
        return False

    def can_view_contractor(self, contractor_data):
        if not self.target_company_verified:
            return False

        if self.own and self.is_admin:
            return True

        # not own, verified

        privacy = contractor_data['privacy']
        if privacy == ContractorPrivacy.VISIBLE_EVERYONE:
            return True

        if privacy == ContractorPrivacy.VISIBLE_OUR_EMPLOYEES:
            return False

        if privacy == ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS:
            return self.are_we_contractors

        if privacy == ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS:
            if not self.my_company:
                return False

            if self.are_we_contractors:
                return True

            target_company_part = Company.objects.collection.find_one({'rek_id' : self.target_company.rek_id},
                                                                           fields=['contractors'])
            if not target_company_part:
                return False

            contractor_list = [item['company_id'] for item in target_company_part['contractors']]
            found_contractor = Contractor.objects.collection.find_one({'$or' : [{'company_1' : self.my_company._id,
                                                                                 'company_2' : {'$in' : contractor_list}},
                                                                                {'company_2' : self.my_company._id,
                                                                                 'company_1' : {'$in' : contractor_list}}]})
            if found_contractor:
                return True

        return False
