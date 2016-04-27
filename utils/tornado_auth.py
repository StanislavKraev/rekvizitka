# -*- coding: utf-8 -*-

from django.middleware.csrf import CsrfViewMiddleware
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import CompanyEmployee, Company
from rek.tornado_srv.utils import get_authenticated_user
csrf_checker = CsrfViewMiddleware()

class DjangoFakeRequest(object):
    def __init__(self, tornado_request, csrf_token):
        self.COOKIES = {}
        for cookie in tornado_request.cookies:
            self.COOKIES[cookie] = tornado_request.cookies[cookie].value
        self.META = {}
        self.method = tornado_request.method
        self.path = tornado_request.path
        self.POST = {'csrfmiddlewaretoken' : csrf_token}

    def is_secure(self):
        return False        # mustdo: get protocol

def get_authorized_parameters(csrf_key, session_key, request):
    company = None

    django_request = DjangoFakeRequest(request, csrf_key)
    if csrf_checker.process_view(django_request, {}, None, None):
        return None, None, None

    user_data = get_authenticated_user(session_key)
    user = User(user_data)
    if user_data and user and not user.is_anonymous():
        employee = CompanyEmployee.objects.get_one({'user_id' : user._id})

        if employee:
            company = Company.objects.get_one(employee.company_id)
    else:
        return None, None, None

    return user, company, employee

def require_login(handler_class):
    def wrap_execute(handler_execute):
        def require_auth(handler, kwargs):
            request = handler.request
            session_id = request.cookies['sessionid'].value
            csrf_key = request.cookies['csrftoken'].value
            # todo: asyncmongo!
            user, company, employee = get_authorized_parameters(csrf_key, session_id, request)

            if not user or not employee or not company:
                handler._transforms = []
                handler.redirect('/')
                return False

            setattr(request, 'user', user)
            setattr(request, 'company', company)
            setattr(request, 'employee', employee)
            return True

        def _execute(self, transforms, *args, **kwargs):
            if not require_auth(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)
        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class

def require_verified(handler_class):
    def wrap_execute(handler_execute):
        def require_auth(handler, kwargs):
            request = handler.request
            session_id = request.cookies['sessionid'].value
            csrf_key = request.cookies['csrftoken'].value
            # todo: asyncmongo!
            user, company, employee = get_authorized_parameters(csrf_key, session_id, request)

            if not user or not employee or not company:
                handler._transforms = []
                handler.redirect('/')
                return False

            if not CompanyAccountStatus.is_active_account(company.account_status):
                handler._transforms = []
                handler.redirect('/verification/')
                return False

            setattr(request, 'user', user)
            setattr(request, 'company', company)
            setattr(request, 'employee', employee)
            return True

        def _execute(self, transforms, *args, **kwargs):
            if not require_auth(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)
        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class
