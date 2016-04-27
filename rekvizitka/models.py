# -*- coding: utf-8 -*-

import bson
from django.conf import settings

from django.utils import timezone
from django.core.mail.message import EmailMultiAlternatives
from django.template.context import Context
from django.template.loader import get_template
import pytz

from rek.billing.models import Account, Transaction, Currency
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.invites.models import Invite, RecommendationRequest, RecommendationStatusEnum
from rek.mango.auth import User, UserActivationLinks
from rek.mongo.fsm import make_fsm, transition
from rek.mongo.models import ObjectManager, SimpleModel
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.inc_form import IncFormEnum
from rek.rekvizitka.utils import integer_to_code
from rek.system_data.rek_settings import SettingsManager

class StaffSizeEnum(object):
    UNKNOWN = 0
    RANGE_LESS_10 = 1
    RANGE_10_20 = 2
    RANGE_20_50 = 3
    RANGE_50_100 = 4
    RANGE_100_200 = 5
    RANGE_200_500 = 6
    RANGE_500_1000 = 7
    RANGE_1000_10000 = 8
    RANGE_MORE_10000 = 9

    ALL = (UNKNOWN,
           RANGE_LESS_10,
           RANGE_10_20,
           RANGE_20_50,
           RANGE_50_100,
           RANGE_100_200,
           RANGE_200_500,
           RANGE_500_1000,
           RANGE_1000_10000,
           RANGE_MORE_10000)

    @classmethod
    def to_string(cls, size):
        if size == cls.RANGE_LESS_10:
            return u"меньше 10"
        if size == cls.RANGE_10_20:
            return u"от 10 до 20"
        if size == cls.RANGE_20_50:
            return u"от 20 до 50"
        if size == cls.RANGE_50_100:
            return u"от 50 до 100"
        if size == cls.RANGE_100_200:
            return u"от 100 до 200"
        if size == cls.RANGE_200_500:
            return u"от 200 до 500"
        if size == cls.RANGE_500_1000:
            return u"от 500 до 1000"
        if size == cls.RANGE_1000_10000:
            return u"от 1000 до 10000"
        if size == cls.RANGE_MORE_10000:
            return u"больше 10000"
        return u"не указано"

    @classmethod
    def choices(cls):
        return [(status, cls.to_string(status)) for status in cls.ALL]

class CompanyOffice(object):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self.city = kwargs.get('city')
        self.information = kwargs.get('information')
        self.physical_address = kwargs.get('physical_address')
        self.phones = kwargs.get('phones')
        self.fax = kwargs.get('fax')
        self.skype = kwargs.get('skype')
        self.icq = kwargs.get('icq')
        self.email = kwargs.get('email')
        self.map_img = kwargs.get('map_img', {'dim' : (0, 0), 'filename' : ''})

    def get_map_url(self, rek_id):
        return '/grid/profile/%s/%s.jpg' % (rek_id, self.map_img['filename'])

    def get_map_img_id(self):
        return self.map_img['filename']

    def get_map_dimensions(self):
        return self.map_img['dim']

class CompanyCategoryEnum(object):
    CAT_UNKNOWN = ""
    CAT_SMALL_BUSINESS = "small"
    CAT_STARTUP = "startup"
    CAT_SOCIAL_PROJECT = "social_project"

    ALL = (CAT_SMALL_BUSINESS, CAT_STARTUP, CAT_SOCIAL_PROJECT)

    @classmethod
    def to_string(cls, category):
        if category == cls.CAT_SMALL_BUSINESS:
            return u"Малый бизнес"
        elif category == cls.CAT_STARTUP:
            return u"Стартап"
        elif category == cls.CAT_SOCIAL_PROJECT:
            return u"Социальный проект"
        return u"Неизвестная категория"

@make_fsm(initial=CompanyAccountStatus.VERIFIED, field_name='account_status')
class Company(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')                                            # auto index
        self.rek_id = kwargs.get('rek_id')                                      # unique index
        self.owner_employee_id = kwargs.get('owner_employee_id')
        self.short_name = kwargs.get('short_name', '')                          # index
        self.full_name = kwargs.get('full_name', '')                            # index
        self.brand_name = kwargs.get('brand_name', '')                          # index
        self.description = kwargs.get('description', '')
        self.logo_file_id = kwargs.get('logo_file_id')
        self.inc_form = kwargs.get('inc_form', IncFormEnum.IF_OOO)
        self.inn = kwargs.get('inn')                                            # unique index
        self.kpp = kwargs.get('kpp')                                            # index
        self.category_text = kwargs.get('category_text', '')
        self.date_creation = kwargs.get('date_creation', timezone.now())
        self.date_established = kwargs.get('date_established')
        self.staff_size = kwargs.get('staff_size', StaffSizeEnum.UNKNOWN)
        self.options = kwargs.get('options', {'employee' : False})
        self.gen_director = kwargs.get('gen_director', "")
        self.chief_accountant = kwargs.get('chief_accountant', "")
        self.account_status = kwargs.get('account_status', CompanyAccountStatus.JUST_REGISTERED)
        self.is_account_activated = kwargs.get('is_account_activated', False)

        self.web_sites = kwargs.get('web_sites', [])
        self.phones = kwargs.get('phones', [])
        self.emails = kwargs.get('emails', [])
        self.offices = kwargs.get('offices', [])
        self.bank_accounts = kwargs.get('bank_accounts', [])
        self.contractors = kwargs.get('contractors', [])
        self.rec_requesters = kwargs.get('rec_requesters', [])

        self.categories = kwargs.get('categories', [])

        if len(self.offices):
            office_obj_list = []
            for office in self.offices:
                office_obj = CompanyOffice(office)
                office_obj_list.append(office_obj)
            self.offices = office_obj_list

    def _fields(self):
        fields = {
            'rek_id' : self.rek_id,
            'owner_employee_id' : self.owner_employee_id,
            'short_name' : self.short_name,
            'full_name' : self.full_name,
            'brand_name' : self.brand_name,
            'description' : self.description,
            'logo_file_id' : self.logo_file_id,
            'inc_form' : self.inc_form,
            'inn' : self.inn,
            'kpp': self.kpp,
            'category_text' : self.category_text,
            'date_creation' : self.date_creation,
            'date_established' : self.date_established,
            'staff_size' : self.staff_size,
            'options' : self.options,
            'gen_director' : self.gen_director,
            'chief_accountant' : self.chief_accountant,
            'account_status' : self.account_status,
            'web_sites' : self.web_sites,
            'phones' : self.phones,
            'emails' : self.emails,
            'offices' : self.make_office_fields(self.offices),
            'bank_accounts' : self.bank_accounts,
            'contractors' : self.contractors,
            'is_account_activated' : self.is_account_activated,
            'rec_requesters' : self.rec_requesters,
            'categories' : self.categories}

        return fields

    def make_office_fields(self, offices):
        result = []
        for office in offices:
            result.append({
                'city' : office.city,
                'information' : office.information,
                'physical_address' : office.physical_address,
                'phones' : office.phones,
                'fax' : office.fax,
                'skype' : office.skype,
                'icq' : office.icq,
                'email' : office.email,
                'map_img' : office.map_img
            })
        return result

    def is_required_data_filled(self):
        return self.brand_name and len(self.brand_name)

    def is_active(self):
        return self.is_account_activated and \
               CompanyAccountStatus.is_active_account(self.account_status) and \
               self.is_required_data_filled()

    def _opf_full(self):
        if self.inc_form:
            return IncFormEnum.type_to_fullopf(self.inc_form)
        else:
            return ''
    opf_full = property(_opf_full)

    def _opf_abbr(self):
        if self.inc_form:
            return IncFormEnum.type_to_abbr(self.inc_form)
        else:
            return ''
    opf_abbr = property(_opf_abbr)

    def can_be_modified(self):
        return CompanyAccountStatus.is_active_account(self.account_status)

    def _get_name(self):
        return self.brand_name or u'<Название компании не указано>'
    name = property(_get_name)

    def _get_relative_url(self):
        return u'/%s' % self.rek_id
    url = property(_get_relative_url)

    def _get_html_link(self):
        return u'<a href="%s">%s</a>' % (self.url, self.name)
    html_link = property(_get_html_link)

    def is_verified(self):
        return self.account_status == CompanyAccountStatus.VERIFIED or self.account_status == CompanyAccountStatus.SEMI_VERIFIED

    @transition(source=CompanyAccountStatus.JUST_REGISTERED, target=CompanyAccountStatus.VERIFIED)
    def verify(self, brand_name=None, description=None):
        brand_name_filled = (self.brand_name and len(self.brand_name)) or (brand_name and len(brand_name))
        description_filled = (self.description and len(self.description)) or (description and len(description))
        if not brand_name_filled:
            raise Exception("Can't change state to verified. Required data is not filled.")

        if brand_name and len(brand_name):
            self.brand_name = brand_name

        if description and len(description):
            self.description = description

        self.objects.update({'_id' : self._id}, {'$set' : {
            'account_status' : self.account_status,
            'brand_name' : self.brand_name,
            'description' : self.description
        }})
        notification_manager.remove(create_action_id(actions.VERIFICATION_PERIODIC, unicode(self._id)))

    @transition(source=CompanyAccountStatus.VERIFIED, target=CompanyAccountStatus.JUST_REGISTERED)
    def unverify(self):
        self.objects.update({'_id' : self._id}, {'$set' : {
            'account_status' : self.account_status,
        }})

    def get_some_logo_url(self, kind='logo'):
        if not self.logo_file_id:
            return ""
        if isinstance(self.logo_file_id, bson.ObjectId):
            self.logo_file_id = ""

        if self.logo_file_id.find(':') != -1:
            file_id, file_rand = self.logo_file_id.split(':')
            return '/grid/profile/%s/%s-%s.jpg' % (self.rek_id, kind, file_rand)
        return ""

    def get_logo_url(self):
        return self.get_some_logo_url()

    def get_list_logo_url(self):
        return self.get_some_logo_url(kind='list_logo')

    def get_admin_user(self):       # mustdo: rework when user roles are added
        user = None

        employee = CompanyEmployee.objects.get_one({'_id' : self.owner_employee_id})
        if employee:
            user_data = User.find_one({'_id' : employee.user_id})
            if user_data:
                user = User(user_data)

        return user, employee

    def printable_staff_size(self):
        return StaffSizeEnum.to_string(self.staff_size)

    def is_valid(self):
        return self.brand_name and len(self.brand_name)

    def save(self):
        if not self.is_valid():
            return 0
        return super(Company, self).save()

    @classmethod
    def get_micro_logo_url(cls, company_rek_id, logo_id):
        if not logo_id or not isinstance(logo_id, bson.ObjectId):
            return ""
        return "/grid/profile/%s/comment_logo.jpg" % company_rek_id

    @classmethod
    def get_active_company_by_rek_id(cls, rek_id):
        if not rek_id or not isinstance(rek_id, basestring):
            return None
        query = {'rek_id' : rek_id,
                 'is_account_activated' : {'$ne' : False},
                 'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}}

        return cls.objects.get_one(query)

    def add_contractor(self, new_contractor, contractor_company):
        for contractor in self.contractors:
            if contractor['id'] == new_contractor._id:
                return

        data = {
            'id' : new_contractor._id,
            'logo' : contractor_company.get_some_logo_url(),
            'brand_name' : contractor_company.brand_name,
            'rek_id' : contractor_company.rek_id
        }
        self.objects.collection.update({'_id' : self._id}, {'$push' : {'contractors': data}})
        self.contractors.append(data)

Company.objects = ObjectManager(Company, 'companies',
    [('date_creation', -1),
        ('short_name', 1),
        ('full_name', 1),
        ('brand_name', 1),
        ('kpp', 1),
        ('inn', 1)],

    [('rek_id', 1)])

@make_fsm(initial='new', field_name='profile_status')
class CompanyEmployee(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.user_id = kwargs.get('user_id')                        # index
        self.company_id = kwargs.get('company_id')                  # index
        self.first_name = kwargs.get('first_name', '')
        self.second_name = kwargs.get('second_name', '')            # index
        self.middle_name = kwargs.get('middle_name', '')
        self.title = kwargs.get('title', '')
        self.phone = kwargs.get('phone', '')                        # index
        self.avatar = kwargs.get('avatar')
        self.male = kwargs.get('male')
        self.birth_date = kwargs.get('birth_date')
        self.profile_status = kwargs.get('profile_status', 'new')
        self.deleted = kwargs.get('deleted', False)
        self.timezone = kwargs.get('timezone', 'Europe/Moscow') or 'Europe/Moscow'

        self._tz = pytz.timezone(self.timezone)

    def _fields(self):
        fields = {
            'user_id' : self.user_id,
            'company_id' : self.company_id,
            'first_name' : self.first_name,
            'second_name' : self.second_name,
            'middle_name' : self.middle_name,
            'title' : self.title,
            'phone' : self.phone,
            'avatar' : self.avatar,
            'male' : self.male,
            'birth_date' : self.birth_date,
            'profile_status' : self.profile_status,
            'deleted' : self.deleted,
            'timezone' : self.timezone
        }
        return fields

    def set(self, **kwargs):
        if not self._id:
            return
        self.objects.collection.update({'_id' : self._id}, {"$set" : kwargs})

    def get_tz(self):
        return self._tz

    def get_some_avatar_url(self, kind='avatar'):
        if not self.avatar:
            return ""
        if isinstance(self.avatar, bson.ObjectId):
            self.avatar = ""

        if self.avatar.find(':') != -1:
            file_id, file_rand = self.avatar.split(':')
            return '/grid/employee/%s/%s-%s.jpg' % (self._id, kind, file_rand)
        return ""

    def get_avatar_url(self):
        return self.get_some_avatar_url()

    def get_full_name(self):
        parts = []
        if len(self.second_name):
            parts.append(self.second_name)
        if len(self.first_name):
            parts.append(self.first_name)
        if len(self.middle_name):
            parts.append(self.middle_name)

        if not len(parts):
            return u'Администратор'

        return u' '.join(parts)

CompanyEmployee.objects = ObjectManager(CompanyEmployee, 'company_employees', [('user_id', 1),
    ('company_id', 1), ('second_name', 1), ('phone', 1)])

def create_staff_user(email):
    password = User.make_random_password()
    created_user = User.create_user(email, password)
    created_user.save()

    return created_user, password

def send_staff_confirmation_email(email, sender, code):
    mail_context = {'code': code,
                    'sender': sender.full_name,
                    'company' : sender.company.get_name()}

    plain_text_template = get_template('mails/staff_confirm.txt')
    html_template = get_template('mails/staff_confirm.html')

    plain_text = plain_text_template.render(Context(mail_context))
    html = html_template.render(Context(mail_context))

    subject = u'Вас добавили в сотрудники компании %s в деловой сети Rekvizitka.Ru' % mail_context['company']

    action = create_action_id(actions.CONFIRM_NEW_EMPLOYEE, code)
    notification_manager.add(action, email, subject, plain_text, html, 10)

def send_password_to_user(email, password):
    mail_context = {'password' : password}

    plain_text_template = get_template('mails/password_set.txt')
    html_template = get_template('mails/password_set.html')

    plain_text = plain_text_template.render(Context(mail_context))
    html = html_template.render(Context(mail_context))

    subject = u'Пароль Вашего аккаунта в деловой сети Rekvizitka.Ru'
    from_email, to,  bcc = settings.EMAIL_HOST_USER, [email,], []
    msg = EmailMultiAlternatives(subject, plain_text, from_email, to, bcc)
    msg.attach_alternative(html, "text/html")
    msg.send()

def get_user_company(user):
    employee = CompanyEmployee.objects.get_one_partial({'user_id' : user._id}, {'company_id' : 1})
    if not employee:
        return None
    company = Company.objects.get_one({'_id' : employee.company_id})
    return company

def generate_rek_id():
    if settings.TEST_RUN:
        return 'CK1'
    return integer_to_code(SettingsManager.inc_and_return_property('company_auto_index'))

def create_new_account(email, password, brand_name, promo_code = None, invite_cookie = None):
    # mustdo: add "transaction"
    created_user = User.create_user(email, password)
    if not created_user:
        raise Exception('failed to create user')

    activation_link = UserActivationLinks({'user' : created_user._id})
    activation_link.save()

    new_employee = CompanyEmployee({'user_id':created_user._id, 'timezone' : 'Europe/Moscow'})
    new_employee.save()

    new_company = Company({'rek_id':generate_rek_id(),
                           'owner_employee_id':new_employee._id,
                           'brand_name' : brand_name})
    new_company.save()

    new_billing_account = Account({'type' : Account.TYPE_COMPANY,
                                   'name' : "Счет компании",
                                   'details' : {'subject_id' : new_company._id}})
    new_billing_account.save()

    if promo_code:
        promo_code.use(new_company._id)
        promo_account = Account.objects.get_one({'system_id' : Account.FIXED_PROMO_ACCOUNT_ID})
        transaction = Transaction({'source' : promo_account._id,
                                   'dest' : new_billing_account._id,
                                   'amount' : Currency.russian_roubles(SettingsManager.get_property("registration_promo_action_amount")),
                                   'comment' : u"Бонус при регистрации компании по промо-коду %s" % unicode(promo_code.code)})
        transaction.save()
        transaction.apply()

    new_employee.set(company_id=new_company._id)

    if invite_cookie and len(invite_cookie):
        invite = Invite.objects.get_one({'cookie_code' : invite_cookie})
        if invite:
            rec_request = RecommendationRequest({'requester' : new_company._id,
                                                 'recipient' : invite.sender,
                                                 'status' : RecommendationStatusEnum.ACCEPTED,
                                                 'message' : u'Регистрация по приглашению: %s' % invite.message,
                                                 'viewed' : True,
                                                 'requester_email' : 'registration@rekvizitka.ru'})
            rec_request.save()
            invite.rec_request = rec_request._id
            invite.save()
            if SettingsManager.get_property('rnes') < 2:
                new_company.objects.update({'_id' : new_company._id}, {'$set' : {'account_status' : CompanyAccountStatus.VERIFIED}})
                new_company.account_status = CompanyAccountStatus.VERIFIED

                dest_account = Account.objects.get_one({'type' : Account.TYPE_COMPANY,
                                                        'details.subject_id' : invite.sender})

                if dest_account:
                    promo_account = Account.objects.get_one({'system_id' : Account.FIXED_PROMO_ACCOUNT_ID})
                    if promo_account:
                        new_trans = Transaction({'source' : promo_account._id,
                                                 'dest' : dest_account._id,
                                                 'amount' : Currency.russian_roubles(SettingsManager.get_property('invite_bonus')),
                                                 'comment' : u'Бонус за приглашение компании "%s" (%s)' % (brand_name, new_company.rek_id)})
                        new_trans.save()
                        new_trans.apply()
    return created_user, password, new_company, activation_link

def get_company_admin_user(company):
    employee = CompanyEmployee.objects.get_one({'_id' : company.owner_employee_id})
    if not employee:
        return None

    user_data = User.collection.find_one({'_id' : employee.user_id})
    if not user_data:
        return None

    return User(user_data)

def get_categories_list(company):
    cat_list = []
    for cat in CompanyCategoryEnum.ALL:
        cat_list.append({'id' : cat,
                         'repr' : CompanyCategoryEnum.to_string(cat),
                         'state' : cat in company.categories})
    return cat_list

class PasswordRecoveryLink(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.user = kwargs.get('user')
        self.created = kwargs.get('created', timezone.now())

    def _fields(self):
        return {'user' : self.user,
                'created' : self.created}

PasswordRecoveryLink.objects = ObjectManager(PasswordRecoveryLink, 'password_recovery_links', [('user', 1),
    ('created', -1)])

