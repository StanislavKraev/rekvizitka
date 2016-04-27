# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext, Context
from django.template.loader import get_template, render_to_string
from django.views.generic.base import View
from rek.billing.models import Invoice, InvoiceStatusEnum
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.inc_form import IncFormEnum
from rek.rekvizitka.models import Company, StaffSizeEnum, get_company_admin_user, CompanyEmployee
from rek.utils.model_fields import is_valid_inn, is_valid_kpp

STATUS_COLORS = {'just_registered' : 'lightgray',
                 'verified' : 'green',
                 'semi_verified' : 'yellow'}

class SearchCompanyView(View):
    def get(self, request):
        company_list = []

        active_only = request.GET.get('active', '')
        search_query = {}
        if active_only=='true':
            search_query['is_account_activated'] = True
        elif active_only=='false':
            search_query['is_account_activated'] = False

        verified_only = request.GET.get('verified', '')
        if verified_only=='true':
            search_query['account_status'] = 'verified'
        elif verified_only=='false':
            search_query['account_status'] = 'just_registered'

        companies = Company.objects.collection.find(search_query).sort('date_creation', -1)
        total_count = companies.count()
        data = {'companies' : company_list,
                'total_count' : total_count}
        for company_data in companies:
            item = Company(company_data)
            company_list.append({'rek_id' : item.rek_id,
                              'brand_name' : item.brand_name,
                              'short_name' : item.short_name,
                              'full_name' : item.full_name,
                              'description' : item.description,
                              'logo_url' : item.get_logo_url(),
                              'inc_form_str' : IncFormEnum.type_to_abbr(item.inc_form),
                              'inn' : item.inn or "",
                              'kpp' : item.kpp or "",
                              'category_text' : item.category_text or "",
                              'date_creation' : item.date_creation,
                              'date_established' : item.date_established or "",
                              'staff_size' : StaffSizeEnum.to_string(item.staff_size),
                              'gen_director' : item.gen_director or "",
                              'chief_accountant' : item.chief_accountant or "",
                              'account_status' : item.account_status,
                              'account_status_color' : STATUS_COLORS.get(item.account_status, 'white'),
                              'is_account_activated' : item.is_account_activated})
        return render_to_response("search/companies/seach_company.html", data, context_instance=RequestContext(request))

class MakeCompanyView(View):
    def get(self, request):
        return render_to_response("search/companies/make_company.html", {}, context_instance=RequestContext(request))

class ShowCompanyView(View):
    def get(self, request, code):
        if not code or not len(code):
            return HttpResponseNotFound('Incorrect company rek id')
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            return HttpResponseNotFound('No such company: %s' % code)

        employees = CompanyEmployee.objects.get({'company_id' : company._id})
        employee_list = []
        for employee in employees:
            user = User.collection.find_one({'_id' : employee.user_id})
            employee_list.append({'id' : employee._id,
                                  'user_id' : employee.user_id,
                                  'first_name' : employee.first_name,
                                  'second_name' : employee.second_name,
                                  'middle_name' : employee.middle_name,
                                  'title' : employee.title,
                                  'phone' : employee.phone,
                                  'avatar' : employee.get_avatar_url(),
                                  'male' : employee.male,
                                  'birth_date' : employee.birth_date,
                                  'profile_status' : employee.profile_status,
                                  'deleted' : employee.deleted,
                                  'email' : user['email'] if user else u'<неизвестно>'})

        company_data = {'rek_id' : company.rek_id,
                          'brand_name' : company.brand_name,
                          'short_name' : company.short_name,
                          'full_name' : company.full_name,
                          'description' : company.description,
                          'logo_url' : company.get_logo_url(),
                          'inc_form_str' : IncFormEnum.type_to_abbr(company.inc_form),
                          'inn' : company.inn or "",
                          'kpp' : company.kpp or "",
                          'category_text' : company.category_text or "",
                          'date_creation' : company.date_creation,
                          'date_established' : company.date_established or "",
                          'staff_size' : StaffSizeEnum.to_string(company.staff_size),
                          'gen_director' : company.gen_director or "",
                          'chief_accountant' : company.chief_accountant or "",
                          'account_status' : company.account_status,
                          'account_status_color' : STATUS_COLORS.get(company.account_status, 'white'),
                          'is_account_activated' : company.is_account_activated}
        return render_to_response("search/companies/show_company.html", {'company' : company_data, 'employees' : employee_list}, context_instance=RequestContext(request))

class ManageCompanyView(View):
    def get(self, request, code):
        if not code or not len(code):
            return HttpResponseNotFound('Incorrect company rek id')
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            return HttpResponseNotFound('No such company: %s' % code)

        company_data = {'rek_id' : company.rek_id,
                          'brand_name' : company.brand_name,
                          'short_name' : company.short_name,
                          'full_name' : company.full_name,
                          'description' : company.description,
#                          'logo_url' : company.get_logo_url(),
#                          'inc_form_str' : IncFormEnum.type_to_abbr(company.inc_form),
                          'inn' : company.inn or "",
                          'kpp' : company.kpp or "",
#                          'category_text' : company.category_text or "",
#                          'date_creation' : company.date_creation,
#                          'date_established' : company.date_established or "",
#                          'staff_size' : StaffSizeEnum.to_string(company.staff_size),
#                          'gen_director' : company.gen_director or "",
#                          'chief_accountant' : company.chief_accountant or "",
                          'account_status' : company.account_status,
#                          'is_account_activated' : company.is_account_activated
        }

        return render_to_response("search/companies/manage_company.html", {'company' : company_data}, context_instance=RequestContext(request))

    def post(self, request, code):
        if not code or not len(code):
            return HttpResponseNotFound('Incorrect company rek id')
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            return HttpResponseNotFound('No such company: %s' % code)

        company_data = {'rek_id' : company.rek_id,
                          'brand_name' : company.brand_name,
                          'short_name' : company.short_name,
                          'full_name' : company.full_name,
                          'description' : company.description,
#                          'logo_url' : company.get_logo_url(),
#                          'inc_form_str' : IncFormEnum.type_to_abbr(company.inc_form),
                          'inn' : company.inn or "",
                          'kpp' : company.kpp or "",
#                          'category_text' : company.category_text or "",
#                          'date_creation' : company.date_creation,
#                          'date_established' : company.date_established or "",
#                          'staff_size' : StaffSizeEnum.to_string(company.staff_size),
#                          'gen_director' : company.gen_director or "",
#                          'chief_accountant' : company.chief_accountant or "",
                          'account_status' : company.account_status,
#                          'is_account_activated' : company.is_account_activated
        }

        errors = {}
        if request.POST.has_key('modify'):
            brand_name = request.POST.get('brand_name', '').strip()
            short_name = request.POST.get('short_name', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            description = request.POST.get('description', '').strip()
            inn = request.POST.get('inn', '').strip()
            kpp = request.POST.get('kpp', '').strip()

            if not len(brand_name):
                errors['brand_name'] = 'Поле не может быть пустым'
            if len(inn) and not is_valid_inn(inn):
                errors['inn'] = 'Некорректный ИНН'
            if len(kpp) and not is_valid_kpp(kpp):
                errors['kpp'] = 'Некорректный КПП'

            company_data['brand_name'] = brand_name
            company_data['short_name'] = short_name
            company_data['full_name'] = full_name
            company_data['description'] = description
            company_data['inn'] = inn
            company_data['kpp'] = kpp

            if not len(errors):
                company.objects.update({'_id' : company._id}, {'$set' : {
                    'brand_name' : brand_name,
                    'short_name' : short_name,
                    'full_name' : full_name,
                    'description' : description,
                    'inn' : inn,
                    'kpp' : kpp
                }})
                return HttpResponseRedirect('/search/companies/%s/' % company.rek_id)
        else:
            return HttpResponseBadRequest('Do not know what to do.')

        return render_to_response("search/companies/manage_company.html", {'company' : company_data, 'errors' : errors}, context_instance=RequestContext(request))

class VerifyCompanyInvoiceView(View):
    def get(self, request, code):
        if not code or not len(code):
            return HttpResponseNotFound('Incorrect company rek id')
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            return HttpResponseNotFound('No such company: %s' % code)

        invoice_list = []
        invoices = Invoice.objects.get({'payer' : company._id,
                                        'status' : InvoiceStatusEnum.PAID})
        for invoice in invoices:
            if not invoice.service or not len(invoice.service):
                invoice_list.append({'title' : self.make_invoice_description(invoice),
                                     'value' : invoice._id})


        company_data = {'rek_id' : company.rek_id,
                        'brand_name' : company.brand_name,
                        'account_status' : company.account_status,
                        'account_status_color' : STATUS_COLORS.get(company.account_status, 'white'),
                        'date_creation' : company.date_creation,
                        'verify' : company.account_status == CompanyAccountStatus.JUST_REGISTERED}
        return render_to_response("search/companies/verify_company_invoice.html",
            {'company' : company_data, 'invoices' : invoice_list},
            context_instance=RequestContext(request))

    def make_invoice_description(self, invoice):
        return u"Счет N%s от %s: %s" % (invoice.number, invoice.create_date.strftime('%d-%m-%Y'), invoice.position)

    def post(self, request, code):
        invoice_list = []
        error_str = ""
        if not code or not len(code):
            return HttpResponseNotFound('Incorrect company rek id')
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            return HttpResponseNotFound('No such company: %s' % code)

        company_data = {'rek_id' : company.rek_id,
                        'brand_name' : company.brand_name,
                        'account_status' : company.account_status,
                        'account_status_color' : STATUS_COLORS.get(company.account_status, 'white'),
                        'date_creation' : company.date_creation,
                        'verify' : company.account_status == CompanyAccountStatus.JUST_REGISTERED}

        if 'verify' in request.POST:
            invoices = Invoice.objects.get({'payer' : company._id,
                                            'status' : InvoiceStatusEnum.PAID})
            for invoice in invoices:
                if not invoice.service or not len(invoice.service):
                    invoice_list.append({'title' : self.make_invoice_description(invoice),
                                         'value' : invoice._id})

            invoice = None
            if company.account_status == CompanyAccountStatus.JUST_REGISTERED:
                invoice_select = request.POST.get('invoice_select', '')
                try:
                    try:
                        invoice_select_id = ObjectId(invoice_select)
                        invoice = Invoice.objects.get_one({'_id' : invoice_select_id})
                    except Exception:
                        pass
#                    if not invoice:
#                        raise Exception('Некорректный счет')

                    admin_user = get_company_admin_user(company)
                    if not admin_user:
                        raise Exception('Невозможно найти пользователя для отправки письма!')

                    email = admin_user.email
                    self.send_verification_passed_email(email, company.rek_id)

                    company.change_fsm_state(CompanyAccountStatus.VERIFIED)
                    if invoice:
                        Invoice.objects.update({'_id' : invoice._id}, {'$set' : {'service' : "verification"}})
                    return HttpResponseRedirect(request.path)
                except Exception, ex:
                    error_str = ex.message
            else:
                error_str = "Компания уже верифицирована"

        elif 'unverify' in request.POST:
            if company.account_status == CompanyAccountStatus.VERIFIED:
                try:
                    company.change_fsm_state(CompanyAccountStatus.JUST_REGISTERED)
                    return HttpResponseRedirect(request.path)
                except Exception, ex:
                    error_str = ex.message
            else:
                error_str = "Компания не верифицирована"
        else:
            return HttpResponseBadRequest("Nothing to do")

        return render_to_response("search/companies/verify_company_invoice.html",
                {'company' : company_data,
                 'error_str' : error_str,
                 'invoices' : invoice_list},
            context_instance=RequestContext(request))

    def send_verification_passed_email(self, email, company_rek_id):
        action = create_action_id(actions.INVOICE_VERIFICATION_PASSED, company_rek_id)

        plain_text = render_to_string('mails/verified_through_invoice.txt')
        html = render_to_string('mails/verified_through_invoice.html')

        notification_manager.add(action, email, 'Ваша компания успешно прошла верификацию в Реквизитке', plain_text, html, 1)
