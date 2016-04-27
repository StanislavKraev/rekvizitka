# -*- coding: utf-8 -*-

from django import template
from rek.rekvizitka.models import AddressTypeEnum, Account, CompanyEmployeeStatus, get_user_employee
from rek.rekvizitka.permissions import CompanyPermission, PermissionCriteriaMask, EmployeePermission
from rek.utils.model_fields import get_field_ref

register = template.Library()

def view_reason(criteria_mask, company):
    if criteria_mask & PermissionCriteriaMask.REGISTERED:
        return u'<a href="/?next=/%s/">Только для зарегистрированных пользователей</a>' % company.code_view
    if criteria_mask & PermissionCriteriaMask.COMPANY_VERIFIED:
        return u'<a href="/">Только для верифицированных компаний</a>'
    if criteria_mask & PermissionCriteriaMask.CONTRACTOR:
        return u"Только для контрагентов"
    return ""

@register.inclusion_tag("tags/rek_address_widget.html")
def rek_address_widget(user, company, can_modify):
    company_check = CompanyPermission(user)

    can_view_address = company_check.can_view_address(company)
    can_view_criteria = company_check.get_view_address_criteria(company) if not can_view_address else 0
    can_view_restriction_reason = view_reason(can_view_criteria, company)

    addresses_list = [{'address_type' : AddressTypeEnum.type_to_name(address.address_type_val),
                       'address_view' : address.address_view,
                       'emails' : address.addressemail_set.all(),
                       'phones' : address.addressphone_set.all(),
                       'address' : unicode(address)}
                      for address in company.companyaddress_set.all()]
    website_list = [unicode(site) for site in company.companywebsite_set.all()]
    return {'can_view_address' : can_view_address,
            'can_view_restriction_reason' : can_view_restriction_reason,
            'can_modify' : can_modify,
            'company_addresses': addresses_list,
            'websites' : website_list,
            'company' : company
            }

@register.inclusion_tag("tags/rek_general_profile.html")
def rek_general_profile(company, can_modify):
    return {'company' : company, 'can_modify' : can_modify}

@register.inclusion_tag("tags/rek_accounts_widget.html")
def rek_accounts_widget(user, company, can_modify):
    company_check = CompanyPermission(user)
    accounts = Account.objects.filter(company=company)
    visible_accounts = []
    for account in accounts:
        can_view_account = company_check.can_view_account(company, account)
        if can_view_account:
            visible_accounts.append(account)

    can_view_criteria = company_check.get_view_accounts_criteria(company) if not len(visible_accounts) else 0
    can_view_restriction_reason = view_reason(can_view_criteria, company)

    return {'can_modify' : can_modify,
            'can_view_restriction_reason' : can_view_restriction_reason,
            'visible_accounts' : visible_accounts}

def get_employee_data(employee, my_employee):
    return {
        'full_name' : employee.full_name,
        'title' : employee.title,
        'avatar' : employee.get_avatar(),
        'email' : employee.user.email if employee.user else '',
        'profile_status' : CompanyEmployeeStatus.toString(employee.profile_status).capitalize(),
        'visible_in_profile' : employee.visible_in_profile,
        'phone' : employee.phone or '',
        'is_me' : employee.id == my_employee.id
    }

@register.inclusion_tag("tags/rek_staff_widget.html")
def rek_staff_widget(user, company, can_modify):
    employees = company.companyemployee_set.all()

    my_employee = get_user_employee(user)
    if my_employee:
        employee_check = EmployeePermission(user)
        visible_employees = []
        for employee in employees:
            can_view_employee = employee_check.can_view(employee)
            if can_view_employee:
                visible_employees.append(get_employee_data(employee, my_employee))
        return {'can_modify' : can_modify,
                'employees' : visible_employees}
    else:
        return {}

@register.inclusion_tag("tags/rek_additional_widget.html")
def rek_additional_widget(user, company, can_modify, profile_extra_data):
    return {'company' : company,
            'can_modify' : can_modify,
            'profile_extra_data' : profile_extra_data}

@register.inclusion_tag("tags/rek_general_widget.html")
def rek_general_widget(user, company, can_modify):
    opf_field = get_field_ref(company, 'inc_form')
    opf_field_value = company.inc_form
    can_modified_unverified_data = CompanyPermission(user).can_modify_unverified_data()

    return {'company' : company,
            'can_modify' : can_modify,
            'opf_field' : opf_field,
            'opf_field_value' : opf_field_value,
            'can_modified_unverified_data' : can_modified_unverified_data}
