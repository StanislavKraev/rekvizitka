# -*- coding: utf-8 -*-

import cStringIO as StringIO
import logging
import bson
import datetime
from bson.objectid import ObjectId

from django.conf import settings
from django.template.context import RequestContext
from django.contrib.auth import login, authenticate as auth_authenticate, logout as auth_logout
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.views.generic.base import  View
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django import http
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.utils import simplejson

import ho.pisa as pisa
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.invites.models import RecommendationRequest, RecommendationStatusEnum
from rek.mango.auth import UserActivationLinks, User, get_password_error
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import Company, create_new_account, CompanyEmployee, StaffSizeEnum, get_categories_list, PasswordRecoveryLink
from rek.rekvizitka.forms import SignupForm, SigninForm, SubscribeForm
from rek.rekvizitka.permissions import CompanyPermission
from rek.rekvizitka.templatetags import portal
from rek.rekvizitka.utils import code_to_integer
from rek.system_data.rek_settings import SettingsManager
from rek.utils import timezones
from rek.utils.timezones import known_timezones, make_tz_name, full_tz_info

COMPANY_ON_PAGE_LIMIT = 10

logger = logging.getLogger('rekvizitka_main')
logger.setLevel(logging.WARNING)

if settings.PRODUCTION:
    fh = logging.FileHandler('/tmp/rekvizitka_main.log')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

class ProfileModuleInitialsView(View):
    @classmethod
    def generate_data_obj(cls, company, my_company):
        if not my_company:
            own = False
        else:
            own = company == my_company

        # <temporary> // until employees are implemented
        company_employee = CompanyEmployee.objects.get_one({'company_id' : company._id})
        employee_id = "" if not company_employee else unicode(company_employee._id)
        # </temporary>

        data = {
            'authorized' : my_company is not None,
            'company_logo' : company.get_logo_url(),
            'rek_id' : company.rek_id,
            'own_company' : own,
            'verified' : CompanyAccountStatus.is_active_account(company.account_status),
            # <temporary> // until employees are implemented
            'employee_id' : employee_id,
            # </temporary>,
            'profile' : {
                'descr' : company.description,
                'information' : {
                    'brandName' : company.brand_name,
                    'shortName' : company.short_name,
                    'fullName' : company.full_name,
                    'inn' : company.inn,
                    'kpp' : company.kpp,
                    'categoryText' : company.category_text or u'',
                    'estYear' : company.date_established.year if company.date_established else None,
                    'staffSize' : company.staff_size,
                    'genDir' : company.gen_director,
                    'genAcc' : company.chief_accountant,
                    'categories' : get_categories_list(company)
                },
            },
            'contacts' : {
                'site' : '',
                'phone' : '',
                'email' : ''
            },
            'staff_size_select' : StaffSizeEnum.choices()
        }
        if company.bank_accounts and len(company.bank_accounts):
            account = company.bank_accounts[0]
            data['profile']['essential_elements'] = {
                'bank' : account['bank'],
                'bank_address' : account['bank_address'],
                'bik' : account['bik'],
                'correspondent_account' : account['correspondent_account'],
                'settlement_account' : account['settlement_account'],
                'recipient' : account['recipient']
            }
        else:
            data['profile']['essential_elements'] = {
                'bank' : "",
                'bank_address' : "",
                'bik' : "",
                'correspondent_account' : "",
                'settlement_account' : "",
                'recipient' : ""
            }

        if len(company.web_sites):
            data['contacts']['site'] = company.web_sites[0]

        if len(company.phones):
            data['contacts']['phone'] = company.phones[0]

        if len(company.emails):
            data['contacts']['email'] = company.emails[0]

        if len(company.offices):
            office_list = []
            data['contacts']['offices'] = office_list
            for office in company.offices:
                office_data = {'city' : office.city,
                               'information' : office.information,
                               'imgID' : office.get_map_img_id(),
                               'img_src' : office.get_map_url(company.rek_id),
                               'img_width' : office.get_map_dimensions()[0],
                               'img_height' : office.get_map_dimensions()[1]}
                office_list.append(office_data)

        #        'company_logo' : company.get_logo_url(),    -> company_logo_url
        #        'rek_id' : company.rek_id,                  -> companyRekId

        return data


    def get(self, request, company_rek_id):
        my_company = request.company if hasattr(request, 'company') else None
        if my_company and my_company.rek_id == company_rek_id:
            company = my_company
        else:
            company = Company.get_active_company_by_rek_id(company_rek_id)
        if not company:
            raise Http404()

        data = self.generate_data_obj(company, my_company)
        data.update(portal.get_common_data_for_company(request, company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class ProfileSettingsInitialsView(View):
    @classmethod
    def generate_data_obj(cls, company, employee):
        tz_id, tz_name = full_tz_info(employee.timezone, settings.LANGUAGE_CODE)
        data = {
            "categoryText" : company.category_text or '',
            "current_tz_name" : tz_name,
            "current_tz_id" : tz_id,
        }

        return data

    def get(self, request):
        company = request.company
        data = self.generate_data_obj(company, request.employee)
        data.update(portal.get_common_data_for_company(request, company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class TimeZonesListView(View):
    def get(self, request):
        if request.user.is_anonymous():
            return HttpResponseForbidden()

        loc_time = datetime.datetime.now()
        zones = [(zone, make_tz_name(zone, loc_time, settings.LANGUAGE_CODE)) for zone in known_timezones]
        result_json = simplejson.dumps(zones)
        return HttpResponse(mark_safe(result_json), mimetype="application/x-javascript")

class IndexView(View):
    def get(self, request):
        if request.user and not request.user.is_anonymous():
            user_company = request.company
            if not user_company:
                raise Exception('Can not get user company')

            return HttpResponseRedirect(reverse('showCompany',args=(user_company.rek_id,)))

        top_signin_form = SigninForm()
        signup_form = SignupForm()
        subscribe_form = SubscribeForm()
        next = self.get_next(request, request.path)

        result_dict = {'top_signin_form' : top_signin_form,
                       'signup_form' : signup_form,
                       'subscribe_form' : subscribe_form,
                       'next' : next,
                       'user' : request.user}
        return render_to_response('base.html', result_dict, context_instance=RequestContext(request))

    def post(self, request):
        signup_form = SignupForm()
        top_signin_form = SigninForm()
        subscribe_form = SubscribeForm()
        login_error = False
        login_disabled = False
        email_error = False
        user = request.user
        page_status = "registered"
        brand_name = ""
        brand_name_error = False
        password_error = False
        promo_code_part1 = ""
        promo_code_part2 = ""
        promo_code_error = False
        email_error_str = ""
        password_error_str = ""
        brandname_error_str = ""
        promo_code_error_str = ""

        if 'login' in request.POST:
            top_signin_form = SigninForm(request.POST)
            if top_signin_form.is_valid():
                username = top_signin_form.cleaned_data['username'].lower()
                password = top_signin_form.cleaned_data['password']
                end_session_on_browser_close = top_signin_form.cleaned_data['publicpc']
                auth_user = auth_authenticate(username=username, password=password)

                if auth_user:
                    if not auth_user.activated:
                        page_status = "user_not_activated"
                    elif auth_user.is_active:
                        try:
                            return self.login_user(request, auth_user, end_session_on_browser_close)
                        except Exception:
                            pass
                    else:
                        page_status = "user_blocked"

                    login_disabled = True
                else:
                    page_status = "wrong_password"
                    login_error = True
            else:
                page_status = "wrong_email"
                login_error = True
        elif 'join' in request.POST:
            if not user.is_anonymous():
                return HttpResponseRedirect(reverse('index_view'))

            signup_form = SignupForm(request.POST)

            if signup_form.is_valid():
                email = signup_form.cleaned_data['email'].lower()
                brand_name = signup_form.cleaned_data['brand_name']
                password = signup_form.cleaned_data['password']

                promo_code = signup_form.cleaned_data['promo_code']

                try:
                    #with transaction.commit_on_success(): # mustdo: return transaction!
                    invite_cookie = request.COOKIES.get('invite')
                    created_user, password, new_company, activation_link = create_new_account(email, password, brand_name, promo_code, invite_cookie)
                    self.send_success_registration_email(email, password, activation_link)
                    if not CompanyAccountStatus.is_active_account(new_company.account_status):
                        self.generate_verification_letters(email, new_company._id)

                    if promo_code:
                        self.send_reg_promo_email(email)
                    auth_authenticate(username=email, password=password)

                    return render_to_response('base.html',
                                              {'email': email,
                                               'page_status': page_status},
                                              context_instance=RequestContext(request))
                except Exception:
                    page_status = "unknown_error"

            elif 'email' in signup_form.errors:
                page_status = "user_creating_error"
                email_error_str = getattr(signup_form, 'email_error_str', signup_form._errors['email'][0])
                email_error = True
            elif 'password' in signup_form.errors:
                page_status = "user_creating_error"
                password_error_str = getattr(signup_form, 'password_error_str', signup_form._errors['password'][0])
                password_error = True
            elif 'brand_name' in signup_form.errors:
                page_status = "user_creating_error"
                brandname_error_str = getattr(signup_form, 'brand_name_error_str', signup_form._errors['brand_name'][0])
                brand_name_error = True
            elif 'promo_code' in signup_form.errors:
                page_status = "user_creating_error"
                promo_code_error_str = getattr(signup_form, 'promo_code_error_str', signup_form._errors['promo_code'][0])
                promo_code_error = True
                promo_code_part1 = request.POST.get('promo_code_part1', '')
                promo_code_part2 = request.POST.get('promo_code_part2', '')
            elif '__all__' in signup_form.errors:
                page_status = "user_creating_error"
                promo_code_error_str = getattr(signup_form, 'promo_code_error_str', signup_form._errors['__all__'][0])
                promo_code_error = True
                promo_code_part1 = request.POST.get('promo_code_part1', '')
                promo_code_part2 = request.POST.get('promo_code_part2', '')
            else:
                page_status = "user_creating_error"

            if settings.PRODUCTION:
                valid_metas = {}
                for key in request.META:
                    val = request.META[key]
                    if isinstance(val, basestring) or isinstance(val, dict) or isinstance(val, list) or isinstance(val, tuple):
                        valid_metas[key] = val

                logger.warning(u'Reg error: page_status=%(page_status)s\nGET: %(get)s\nPOST: %(post)s\nMETA: %(meta)s' % {
                    'page_status' : page_status or '',
                    'get' : simplejson.dumps(request.GET),
                    'post' : simplejson.dumps(request.POST),
                    'meta' : simplejson.dumps(valid_metas)
                })

        next = self.get_next(request, request.path)

        result_dict = {'page_status': page_status,
                       'top_signin_form' : top_signin_form,
                       'signup_form' : signup_form,
                       'subscribe_form' : subscribe_form,
                       'next' : next,
                       'login_error' : login_error,
                       'login_disabled' : login_disabled,
                       'email_error' : email_error,
                       'user' : user,
                       'brand_name' : brand_name,
                       'brand_name_error' : brand_name_error,
                       'password_error' : password_error,
                       'email_error_str' : email_error_str,
                       'password_error_str' : password_error_str,
                       'brandname_error_str' : brandname_error_str,
                       'promo_code_error' : promo_code_error,
                       'promo_code_error_str' : promo_code_error_str,
                       'promo_code_part1' : promo_code_part1,
                       'promo_code_part2' : promo_code_part2}

        if 'email' in request.POST:
            email = request.POST['email']
            result_dict['email'] = email.strip().lower()

        if 'username' in request.POST:
            username = request.POST['username']
            result_dict['username'] = username.strip()

        if 'brand_name' in request.POST:
            brand_name = request.POST['brand_name']
            result_dict['brand_name'] = brand_name.strip()

        return render_to_response('base.html', result_dict, context_instance=RequestContext(request))

    def generate_verification_letters(self, email, company_id):
        letters_count = SettingsManager.get_property('verifylettercount')
        interval_days = SettingsManager.get_property('verifyletterdelaydays')
        subject = u"Пройдите верификацию вашей компании в Реквизитке"

        mail_context = {'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}

        text = render_to_string('mails/periodic_verify_letter.txt', dictionary=mail_context)
        html = render_to_string('mails/periodic_verify_letter.html', dictionary=mail_context)

        action_id = create_action_id(actions.VERIFICATION_PERIODIC, unicode(company_id))
        for day in xrange(letters_count):
            delay = interval_days * (day + 1) * 60 * 24
            notification_manager.add(action_id, email, subject, text, html, delay)

    def get_next(self, request, default=None):
        if 'next' in request.GET:
            return request.GET['next']
        if 'next' in request.POST:
            return request.POST['next']
        if 'HTTP_REFERER' in request.META:
            referrer = request.META['HTTP_REFERER']

            if 'activate_account' not in referrer and 'password-recovery' not in referrer:
                if '/?next=' in request.META['HTTP_REFERER']:
                    referrer = referrer[referrer.find('/?next=') + 7:]
                return referrer
        return default

    def login_user(self, request, user, end_session_on_browser_close = False):
        login(request, user)
        if end_session_on_browser_close:
            request.session.set_expiry(0)
        employee = CompanyEmployee.objects.get_one({'user_id' : user._id})
        if not employee:
            raise Exception('User without employee') # todo: log?

        next_url = self.get_next(request)
        if next_url:
            return HttpResponseRedirect(next_url)

        company = Company.objects.get_one({'_id' : employee.company_id})
        if not company:
            auth_logout(request)
            return HttpResponseRedirect(reverse('index_view'))

        return HttpResponseRedirect(reverse('showCompany',args=(company.rek_id,)))

    def send_success_registration_email(self, email, password, activation_link):
        mail_context = {'password': password,
                        'email': email,
                        'activation_url' : reverse('activation_view', kwargs={'link_id' : str(activation_link._id)}),
                        'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}

        plain_text_template = get_template('mails/signup.txt')
        html_template = get_template('mails/signup.html')

        plain_text = plain_text_template.render(Context(mail_context))
        html = html_template.render(Context(mail_context))

        subject, from_email, to,  bcc = 'Регистрация в Реквизитке', settings.EMAIL_HOST_USER, [email,], []
        msg = EmailMultiAlternatives(subject, plain_text, from_email, to, bcc)
        msg.attach_alternative(html, "text/html")

        msg.send()

    def send_reg_promo_email(self, email):
        mail_context = {'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}

        plain_text_template = get_template('mails/reg_promo.txt')
        html_template = get_template('mails/reg_promo.html')

        plain_text = plain_text_template.render(Context(mail_context))
        html = html_template.render(Context(mail_context))

        subject, from_email, to,  bcc = 'Начисление средств по акции', settings.EMAIL_HOST_USER, [email,], []
        msg = EmailMultiAlternatives(subject, plain_text, from_email, to, bcc)
        msg.attach_alternative(html, "text/html")

        msg.send()

def logout(request):
    """
    Handle user logout
    """
    auth_logout(request)
    return HttpResponseRedirect(reverse('index_view'))

class ShowCompanyRek(View):
    template = 'apps/profile/main_page/templates/main_page.html'
    def get(self, request, code):
        my_company = request.company if hasattr(request, 'company') else None
        if my_company and my_company.rek_id == code:
            company = my_company
        else:
            active_company = {'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}}
            query = {'rek_id' : code,
                     'is_account_activated' : {'$ne' : False},
                     '$or' : [active_company]}

            if my_company:
                not_verified_but_asked_for_our_recommendation = {'$and' : [{'account_status' : CompanyAccountStatus.JUST_REGISTERED},
                                                                           {'_id' : {'$in' : my_company.rec_requesters}}]}
                query['$or'].append(not_verified_but_asked_for_our_recommendation)

            company = Company.objects.get_one(query)

        if not company:
            raise Http404()

        data = ProfileModuleInitialsView.generate_data_obj(company, my_company)
        data.update(portal.get_common_data_for_company(request, company))
        response_content = mark_safe(simplejson.dumps(data))
        return render_to_response(self.template,
            {
                'profile_module_init' : response_content,
                'sidebar_mode' : 'some_company',
                'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))

class ShowCompanyRekAbout(ShowCompanyRek):
    template = 'apps/profile/main_page/templates/main_page.html'

class ShowCompanyRekContacts(ShowCompanyRek):
    template = 'apps/profile/contacts_page/templates/contacts_page.html'

class ShowCompanySettings(View):
    def get(self, request):
        data = ProfileSettingsInitialsView.generate_data_obj(request.company, request.employee)
        data.update(portal.get_common_data_for_company(request, request.company))
        response_content = mark_safe(simplejson.dumps(data))
        return render_to_response('apps/settings/templates/template.html', {
            'profile_settings_init' : response_content,
        }, context_instance = RequestContext(request))

class SaveSettingsView(View):
    def post(self, request):
        company = request.company
        employee = request.employee

#       todo: permissions for employee
#        check = CompanyPermission(request.user, request.employee, company)
#        if not check.can_modify_settings(company):
#            return HttpResponseForbidden()

        if not request.is_ajax():
            return HttpResponseForbidden()

        if 'act' not in request.POST or 'data' not in request.POST:
            raise Http404

        action = request.POST['act']
        data_str = request.POST['data']

        try:
            data = simplejson.loads(data_str)
            if not data:
                raise Exception()
        except Exception:
            raise Http404

        if action == 'gi':
            return self.process_general_info(company, employee, data)

        raise Http404()

    def process_general_info(self, company, employee, data):
        timezone_str = data.get('timezone_id', -1)
        try:
            timezone_id = int(timezone_str)
        except ValueError:
            return HttpResponse(simplejson.dumps({'error' : True}), mimetype='application/javascript')

        if timezone_id < 1:
            return HttpResponse(simplejson.dumps({'error' : True}), mimetype='application/javascript')

        locale_str = settings.LANGUAGE_CODE.lower()
        if locale_str not in timezones.locale_indexes or timezone_id not in timezones.known_timezones:
            return HttpResponse(simplejson.dumps({'error' : True}), mimetype='application/javascript')

        timezone_val = timezones.known_timezones[timezone_id][0]
        CompanyEmployee.objects.update({'_id' : employee._id}, {'$set' : {'timezone' : timezone_val}})
        id, name = timezones.full_tz_info(timezone_val, locale_str)
        return HttpResponse(simplejson.dumps({"current_tz_name" : name,
                                              "current_tz_id" : id,}), mimetype='application/javascript')

def generate_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result)
    if not pdf.err:
        res = result.getvalue()
        result.close()
        return res
    return None

def write_pdf(template_src, context_dict):
    result = generate_pdf(template_src, context_dict)
    if result:
        return http.HttpResponse(result, mimetype='application/pdf')
    return HttpResponseServerError("Couldn't generate pdf")

class JSONResponse(HttpResponse):
    def __init__(self, data):
        super(JSONResponse, self).__init__(
                simplejson.dumps(data), mimetype='application/json')

class CompanyFillData(View):
    def get(self, request):
        company = request.company
        if company.is_required_data_filled():
            return HttpResponseRedirect(reverse('index_view'))
        template_name = "fill_required_reg_data.html"
        return render_to_response(template_name, context_instance=RequestContext(request))

class VerifyCollectionView(View):
    def get(self, request, page):
        try:
            page = int(page)
            if page < 1 or page > 12345:
                page = 1
            term = request.GET['q'].strip()
        except Exception:
            term = ''

        page -= 1

        company_on_page_offset = COMPANY_ON_PAGE_LIMIT * int(page)

        regex = '.*%s.*' % term
        condition = {'$regex' : regex, '$options' : 'i' }
        condition_list = [
                {'short_name' : condition},
                {'full_name' : condition},
                {'brand_name' : condition},
        ]
        rek_id = code_to_integer(term)
        if rek_id:
            condition_list.append({'rek_id' : term})
        try:
            i_term = int(term)
            can_be_inn = len(term) == 12 or len(term) == 10
            can_be_kpp = len(term) == 9
        except Exception:
            can_be_inn = False
            can_be_kpp = False
            i_term = 0

        if can_be_inn:
            condition_list.append({'inn' : i_term})
        elif can_be_kpp:
            condition_list.append({'kpp' : i_term})

        full_conditions = {'$and' : [
            {'$or' : condition_list},
            {'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}},
            {'is_account_activated' : {'$ne' : False}}
        ]}

        company_count = Company.objects.count(full_conditions)

        pages = company_count / COMPANY_ON_PAGE_LIMIT + (1 if company_count % COMPANY_ON_PAGE_LIMIT else 0)

        if page > pages - 1:
            result = {
                'companies' : [],
                'page' : page + 1,
                'pages' : pages,
                'can_send': False
            }
            return HttpResponse(simplejson.dumps(result), mimetype='application/javascript')

        # todo: optimize query. do not use skip like this
        companies = Company.objects.get(full_conditions, COMPANY_ON_PAGE_LIMIT, company_on_page_offset)

        employee = request.employee
        recommendations = RecommendationRequest.objects.get({'requester' : request.company._id})

        this_company = request.company
        check = CompanyPermission(request.user, employee, request.company)
        can_ask_recommendation = check.can_ask_recommendation(this_company)

        companies_list = []
        result={
            'companies' : companies_list,
            'page' : page + 1,
            'pages' : pages,
            'can_send': can_ask_recommendation
        }

        for company in companies:
            already_sent = False
            for item in recommendations:
                if item.recipient == company._id and item.status != RecommendationStatusEnum.DECLINED:
                    already_sent = True
                    break

            result_data = {
                'code' : company.rek_id,
                'name' : company.brand_name,
                'kind_of_activity': company.category_text,
                'logo': company.get_some_logo_url(kind='post_logo'),
                'send_status': already_sent,
            }
            companies_list.append(result_data)

        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

class AccountActivationView(View):
    def get(self, request, link_id):
        try:
            link = UserActivationLinks.objects.get_one({'_id' : bson.ObjectId(link_id)})
            if not link:
                raise Exception()
        except Exception:
            raise Http404()

        user_id = link.user

        User.collection.update({'_id' : user_id}, {'$set' : {'activated' : True}})
        employee = CompanyEmployee.objects.get_one_partial({'user_id' : user_id}, {'company_id' : 1})

        if employee and employee.company_id:
            Company.objects.update({'_id' : employee.company_id}, {'$set' : {'is_account_activated' : True}})
        UserActivationLinks.objects.collection.remove({'_id' : link._id})

        user = User.get({'_id' : user_id})
        user.backend = "rek.mango.auth.Backend"
        if user:
            login(request, user)

        return render_to_response('base.html',
                {'page_status': 'account_activated'},
                 context_instance=RequestContext(request))

class PasswordRecovery(View):
    def get(self, request):
        return render_to_response('password_recovery.html', {},
            context_instance=RequestContext(request))

    def send_email(self, user, link_id):
        email = user.email

        mail_context = {'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME, 'link_id' : unicode(link_id)}

        text = render_to_string('mails/password_reset.txt', dictionary=mail_context)
        html = render_to_string('mails/password_reset.html', dictionary=mail_context)

        action_id = create_action_id(actions.PASSWORD_RECOVERY, email)
        subject = 'Восстановление пароля на Rekvizitka.Ru'
        notification_manager.add(action_id, email, subject, text, html, 0)

    def post(self, request):
        if 'email' not in request.POST:
            raise Http404()
        email = request.POST['email'].strip().lower()
        user = User.collection.find_one({'email' : email})
        if not user:
            return render_to_response('password_recovery.html', {'user_not_found' : True,
                                                          'email' : email},
                                      context_instance=RequestContext(request))

        link = PasswordRecoveryLink({'user':user['_id']})
        link.save()

        self.send_email(User(user), link._id)

        return render_to_response('password_recovery.html', {'link_id' : link._id, 'email' : email},
            context_instance=RequestContext(request))

class NewPasswordView(View):
    def get(self, request, link_id):
        try:
            link_oid = ObjectId(link_id)
        except Exception:
            raise Http404()

        link = PasswordRecoveryLink({'_id' : link_oid})
        if not link:
            raise Http404()

        return render_to_response('set_new_password.html', {},
            context_instance=RequestContext(request))

    def post(self, request, link_id):
        try:
            link_oid = ObjectId(link_id)
        except Exception:
            raise Http404()

        link = PasswordRecoveryLink.objects.get_one({'_id' : link_oid})
        if not link:
            raise Http404()

        new_password = request.POST.get('new_password', '').strip()
        new_password_repeat = request.POST.get('new_password_repeat', '').strip()

        pass_error = get_password_error(new_password)
        if pass_error:
            return render_to_response('set_new_password.html', {'error' : True, 'msg' : pass_error},
                context_instance=RequestContext(request))

        if new_password != new_password_repeat:
            return render_to_response('set_new_password.html', {'error' : True, 'msg' : u'Введеные пароли не совпадают'},
                context_instance=RequestContext(request))

        user_dict = User.collection.find_one({'_id' : link.user})
        if not user_dict:
            return render_to_response('set_new_password.html', {'error' : True, 'msg' : u'Не удалось изменить пароль'},
                context_instance=RequestContext(request))
        user = User(user_dict)

        PasswordRecoveryLink.objects.collection.remove({'_id' : link_oid})
        # todo: validate password
        user.set_password(new_password)
        user.backend = "rek.mango.auth.Backend"
        login(request, user)

        return render_to_response('set_new_password.html', {'password_set' : True, 'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME},
            context_instance=RequestContext(request))
