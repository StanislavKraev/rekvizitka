# -*- coding: utf-8 -*-

from rek.invites.models import RecommendationRequest
from rek.permissions import Permission
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import get_user_company
from rek.system_data.rek_settings import SettingsManager

class PermissionCriteriaMask:
    REGISTERED                  = 1 << 0
    CONTRACTOR                  = 1 << 1
    CONTRACTOR_OF_CONTRACTOR    = 1 << 2
    NOT_BLACKLISTED             = 1 << 3
    COMPANY_VERIFIED            = 1 << 4

class CompanyPermission(Permission):
    def can_view_address(self, company):
        #noinspection PyUnusedLocal
        unused = company

        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        own = user_company == company
        if not own and (not user_company or not CompanyAccountStatus.is_active_account(user_company.account_status)):
            return False

        return True

    def get_view_address_criteria(self, company):
        #noinspection PyUnusedLocal
        unused = company

        pcm = 0

        if not self.user.is_authenticated():
            pcm |= PermissionCriteriaMask.REGISTERED
        else:
            user_company = get_user_company(self.user)
            own = user_company == company
            if not own and (not user_company or not CompanyAccountStatus.is_active_account(user_company.account_status)):
                pcm |= PermissionCriteriaMask.COMPANY_VERIFIED

        return pcm

    def can_view_account(self, company, account):
        #noinspection PyUnusedLocal
        unused = company

        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        own = user_company == company
        if not own and (not user_company or not CompanyAccountStatus.is_active_account(user_company.account_status)):
            return False

        if not own and account.hidden:
            return False

        return True

    def get_view_accounts_criteria(self, company):
        #noinspection PyUnusedLocal
        unused = company

        pcm = 0

        if not self.user.is_authenticated():
            pcm |= PermissionCriteriaMask.REGISTERED
        else:
            user_company = get_user_company(self.user)
            own = user_company == company
            if not own and (not user_company or not CompanyAccountStatus.is_active_account(user_company.account_status)):
                pcm |= PermissionCriteriaMask.COMPANY_VERIFIED

        return pcm

    def can_modify(self, company):
        if not self.user.is_authenticated():
            return False

        user_company = self.company
        if not user_company:
            return False

        return company == user_company

    def can_modify_unverified_data(self):
        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or user_company.account_status == CompanyAccountStatus.VERIFIED:
            return False

        return False

    def can_modify_settings(self):
        if not self.user.is_authenticated():
            return False

        user_company = self.company
        if not user_company:
            return False

        return True

    def can_ask_recommendation(self, company_to_ask, result_dict = None):
        result_dict = result_dict or {}

        if not self.user.is_authenticated():
            result_dict['unauthorized'] = True
            return False

        user_company = self.company
        if not user_company or not self.employee:
            result_dict['not_verified'] = True
            return False

        recommendations_count = RecommendationRequest.objects.count({'requester' : user_company._id})
        if not self.company.is_verified() and recommendations_count >= SettingsManager.get_property('rmax'):
            result_dict['max_reached'] = True
            return False

        return True

class EmployeePermission(Permission):
    def can_view(self, employee):
        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or not CompanyAccountStatus.is_active_account(user_company.account_status):
            return False

        if not employee.visible_in_profile:
            return (employee.company == user_company and self.user.groups.filter(name="companyadmin").count() > 0) or \
                    employee == self.user.get_profile()

        return True

    def can_delete(self, employee):
        if not employee.can_delete():
            return False

        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or not user_company.is_active():
            return False

        if not self.user.groups.filter(name="companyadmin").count():
            return False

        return employee.company == user_company

    def can_create(self):
        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or not user_company.is_active():
            return False

        return self.user.groups.filter(name="companyadmin").count() > 0

    def can_modify_any(self, company):
        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or not user_company.is_active():
            return False

        if not self.user.groups.filter(name="companyadmin").count():
            return False

        return company == user_company

class ContractorsPermission(Permission):
    def can_add(self, company):
        if not self.user.is_authenticated():
            return False

        user_company = get_user_company(self.user)
        if not user_company or not user_company.is_active():
            return False

        if company == user_company:
            return False

#        if not self.user.groups.filter(name="companyadmin").count(): # todo
#            return False

        # todo:
#        my_contractor_request = Contractors.objects.filter(
#            (
#                Q(company_1=user_company ) &
#                Q(company_2=company)
#            ) | (
#                Q(company_2=user_company ) &
#                Q(company_1=company )
#            )
#        ).count()

        # todo:
#        if my_contractor_request:
#            return False

        return True

