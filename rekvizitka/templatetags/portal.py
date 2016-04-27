# -*- coding: utf-8 -*-
import codecs

from django import template
from django.conf import settings
from django.middleware.csrf import get_token
from django.utils import simplejson
from rek.chat.models import ChatDialog
from rek.contractors.models import Contractor, ContractorStatusEnum
from rek.invites.models import RecommendationRequest
from rek.rekvizitka.models import Company, CompanyEmployee
from rek.rekvizitka.account_statuses import CompanyAccountStatus

register = template.Library()

def get_contractors(company):
    if not (company and hasattr(company, 'contractors') and company.contractors and len(company.contractors)):
        return []

    return [{'rek_id' : contractor_data['rek_id'],
             'brand_name' : contractor_data['brand_name'],
             'comment_logo' : Company.get_micro_logo_url(contractor_data['rek_id'],
                                                         contractor_data['micro_logo'])} for contractor_data in company.contractors]

def get_unread_dialog_count(employee_ie):
    return ChatDialog.objects.collection.find({'parties' : employee_ie,
                                               'not_viewed_by_parties' : employee_ie,
                                               'hidden_by_parties' : {'$ne' : employee_ie}}).count()


def get_unviewed_contractors_count(target_company):
    # todo: cache count in company object (denorm)
    return Contractor.objects.collection.find({'viewed' : False,
                                               'company_2' : target_company._id,
                                               'status' : ContractorStatusEnum.RECEIVED}).count()

def get_common_data_for_company(request, target_company):
    common_data = {}
    if not target_company:
        return {'common_data' : common_data}

    company = None
    authorized = not request.user.is_anonymous() and hasattr(request, "company") and request.company is not None

    # <temporary> // until employees are implemented
    employee_id = ''
    # </temporary>

    own = False
    if authorized:
        company = target_company
        own = request.company._id == target_company._id
        # <temporary> // until employees are implemented
        employee = CompanyEmployee.objects.get_one({'company_id' : company._id})
        employee_id = unicode(employee._id) if employee else ''
        # </temporary>
        common_data.update({'verified' : CompanyAccountStatus.is_active_account(request.company.account_status)})
        common_data.update({'they_verified' : CompanyAccountStatus.is_active_account(target_company.account_status)})

    common_data.update({'contractors' : [],
                        'companyRekId' : target_company.rek_id,
                        'company_logo_url' : target_company.get_logo_url(),
                        'brandName' : target_company.brand_name,
                        # <temporary> // until employees are implemented
                        'employee_id' : employee_id
                        # </temporary>
    })

    common_data.update({
        'own_company' : own,
        'authorized' : authorized
    })

    if authorized:
        common_data.update({'companyRekId' : company.rek_id,
                            'company_logo_url' : company.get_logo_url(),
                            'brandName' : company.brand_name,
                            'ownBrandName' : request.company.brand_name,
                            'ownCompanyRekId' : request.company.rek_id})
        if own:
            common_data['unviewed_contractors'] = get_unviewed_contractors_count(request.company)
        else:
            my_rec_request_status = -1
            their_rec_request_status = -1
            recs = RecommendationRequest.objects.get({'$or' : [{'requester' : company._id,
                                                                'recipient' : request.company._id},
                                                               {'recipient' : company._id,
                                                                'requester' : request.company._id}]})
            for rec in recs:
                if rec.recipient == request.company._id:
                    their_rec_request_status = rec.status
                else:
                    my_rec_request_status = rec.status
                if my_rec_request_status != -1 and their_rec_request_status != -1:
                    break
            if my_rec_request_status != -1:
                common_data['my_rec_request_status'] = my_rec_request_status
            if their_rec_request_status != -1:
                common_data['their_rec_request_status'] = their_rec_request_status

            we_are_contractors = ""
            contractor = Contractor.objects.get_one({'$or' : [{'company_1' : target_company._id,
                                                               'company_2' : request.company._id},
                                                              {'company_2' : target_company._id,
                                                               'company_1' : request.company._id}]})
            if contractor:
                if contractor.status == ContractorStatusEnum.ACCEPTED:
                    we_are_contractors = 'yes'
                elif contractor.status == ContractorStatusEnum.RECEIVED:
                    if contractor.company_1 == request.company._id:
                        we_are_contractors = 'we_asked'
                    else:
                        we_are_contractors = 'they_asked'
                elif contractor.status == ContractorStatusEnum.DECLINED:
                    if contractor.company_1 == request.company._id:
                        we_are_contractors = 'they_declined'
                    else:
                        we_are_contractors = 'we_declined'
            else:
                we_are_contractors = 'no'

            common_data['we_are_contractors'] = we_are_contractors

        if common_data['verified']:
            common_data.update({'notifications' : {'unread_dialogs' : get_unread_dialog_count(request.employee._id)}})

    return {'common_data' : common_data}

def get_common_data_for_employee(request, target_employee):
    result_data = {}
    if not request:
        return {'common_data' : result_data}

    authorized = not request.user.is_anonymous() and hasattr(request, "company") and request.company is not None

    if not target_employee:
        return {'common_data' : result_data}

    own = False

    result_data.update({
        'own_company' : own,
        'authorized' : authorized
    })

    if authorized:
        result_data.update({'ownBrandName' : request.company.brand_name,
                            'ownCompanyRekId' : request.company.rek_id})

        if result_data['verified']:
            result_data.update({'notifications' :
                                        {'unread_dialogs' : get_unread_dialog_count(request.employee._id)}
            })

    return {'common_data' : result_data}

def get_common_data_for_search(request, show_options):
    result_data = {}
    if not request:
        return {'common_data' : result_data}

    company = None
    authorized = not request.user.is_anonymous() and hasattr(request, "company") and request.company is not None
    own = False
    if authorized:
        own = True
        company = request.company
        result_data.update({'show_mode' : show_options.get('show_mode', 'companies'),
                            'verified' : CompanyAccountStatus.is_active_account(company.account_status),
                            'companyRekId' : company.rek_id,
                            'brandName' : company.brand_name})

    result_data.update({
        'own_company' : own,
        'authorized' : authorized
    })

    if authorized:
        result_data.update({'companyRekId' : company.rek_id,
                            'company_logo_url' : company.get_logo_url(),
                            'brandName' : company.brand_name,
                            'ownBrandName' : company.brand_name,
                            'ownCompanyRekId' : company.rek_id})

        if result_data['verified']:
            result_data.update({'notifications' :
                                        {'unread_dialogs' : get_unread_dialog_count(request.employee._id)}
            })

    return {'common_data' : result_data}

def get_common_data_for_feedback(request):
    result_data = {}
    if not request:
        return {'common_data' : result_data}

    company = None
    authorized = not request.user.is_anonymous() and hasattr(request, "company") and request.company is not None

    own = False
    if authorized:
        own = True
        company = request.company
        result_data.update({'verified' : CompanyAccountStatus.is_active_account(company.account_status)})

    result_data.update({
        'own_company' : own,
        'authorized' : authorized
    })

    if authorized:
        result_data.update({'companyRekId' : company.rek_id,
                            'company_logo_url' : company.get_logo_url(),
                            'brandName' : company.brand_name,
                            'ownBrandName' : request.company.brand_name,
                            'ownCompanyRekId' : request.company.rek_id})

        if result_data['verified']:
            result_data.update({'notifications' :
                                        {'unread_dialogs' : get_unread_dialog_count(request.employee._id)}
            })

    return {'common_data' : result_data}

@register.simple_tag
def portal_initials(request, mode, sidebar_initial_data):
    result_data = {'csrf_token' : get_token(request),
                   'sidebar_mode' : mode or ""}
    if not request:
        return simplejson.dumps(result_data)

    if mode == "some_company":
        result_data.update(get_common_data_for_company(request, sidebar_initial_data)['common_data'])
        return simplejson.dumps(result_data)
    elif mode == "some_employee":
        result_data.update(get_common_data_for_employee(request, sidebar_initial_data)['common_data'])
        return simplejson.dumps(result_data)
    elif mode == "search":
        result_data.update(get_common_data_for_search(request, sidebar_initial_data)['common_data'])
        return simplejson.dumps(result_data)

    result_data.update(get_common_data_for_feedback(request)['common_data'])
    return simplejson.dumps(result_data)

try:
    with codecs.open(settings.CLIENT_SIDE_MODULES_DATA_FILE, 'r', 'utf-8') as _f:
        _modules_data = simplejson.loads(_f.read())
        _modules_info = {}
        for mod in _modules_data:
            if mod.find('/') == -1:
                _modules_info[mod] = mod
            else:
                mod_name, ver = mod.split('/')
                _modules_info[mod_name] = mod
except Exception:
    _modules_info = {}

try:
    with codecs.open(settings.CLIENT_SIDE_APPS_DATA_FILE, 'r', 'utf-8') as _f:
        _apps_data = simplejson.loads(_f.read())
except Exception:
    _apps_data = {}

@register.simple_tag
def client_mod_ver(name):
    return _modules_info.get(name, '<unknown_module>')

@register.simple_tag
def client_app_ver(name, lang):
    app_name = _apps_data.get(name, '<unknown_app>')
    return "%(path)s%(name)s_%(lang)s.js" % {'name' : app_name, 'lang' : lang, 'path' : settings.CLIENT_SIDE_APPS_PATH}

@register.simple_tag
def client_app_css_ver(name, lang):
    app_name = _apps_data.get(name, '<unknown_app>')
    return "%(path)s%(name)s_%(lang)s.css" % {'name' : app_name, 'lang' : lang, 'path' : settings.CLIENT_SIDE_APPS_PATH}