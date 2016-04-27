# -*- coding: utf-8 -*-

from django.contrib.auth import login, authenticate as auth_authenticate, logout as auth_logout
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.base import View
from rek.rekvizitka.utils import validateEmail

class LoginAdminView(View):
    def get(self, request):
        return render_to_response('alogin.html', {}, context_instance=RequestContext(request))

    def post(self, request):
        error_msg = ''
        if 'login' not in request.POST:
            return HttpResponseForbidden()

        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        if not len(email) or not len(password):
            error_msg = 'Заполните email и пароль'
        elif not validateEmail(email):
            error_msg = 'Неверный email адрес'
        else:
            auth_user = auth_authenticate(username=email, password=password)

            if auth_user:
                try:
                    login(request, auth_user)
                    next_url = request.GET['next'] if 'next' in request.GET else request.POST['next'] if 'next' in request.POST else '/'
                    if next_url:
                        return HttpResponseRedirect(next_url)
                except Exception:
                    pass

                error_msg = "Неизвестная ошибка. Попробуйте позже."
            else:
                error_msg = "Неправильная пара email-пароль. Попробуйте еще раз."

        return render_to_response('alogin.html',
                                  {'login_error_message' : error_msg},
                                  context_instance=RequestContext(request))

class LogoutAdminView(View):
    def post(self, request):
        auth_logout(request)
        return HttpResponseRedirect('/login/')
