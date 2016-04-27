# -*- coding: utf-8 -*-
from datetime import date
from random import randint
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaulttags import csrf_token
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.views.generic.base import View
from rek import settings
from rek.deferred_notification.actions import create_action_id, FEEDBACK_SENT
from rek.deferred_notification.manager import notification_manager
from rek.feedback.forms import FeedbackForm

class SendFeedbackInitialsView(View):
    @classmethod
    def generate_data(cls, email):
        data = {'email' : email}
        result_json = simplejson.dumps(data)
        return mark_safe(result_json)

    def get(self, request):
        user = request.user
        email = user.email if not user.is_anonymous() else ''
        return HttpResponse(self.generate_data(email), mimetype="application/x-javascript")

class SendFeedback(View):
    def get(self, request):
        template_name = 'apps/feedback/feedback_module/templates/template.html'
        user = request.user
        email = user.email if not user.is_anonymous() else ''

        return render_to_response(template_name, {
            'feedback_module_init' : SendFeedbackInitialsView.generate_data(email),
            'sidebar_mode' : 'feedback',         # todo: ?
            'sidebar_initial_data' : None   # todo: ?
        }, context_instance=RequestContext(request))

    def post(self, request):
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            msg = form.cleaned_data['msg']

            if form.cleaned_data['extra_field'] == get_token(request):
                mail_to = 'support@rekvizitka.ru'

                browser_info = u'IP адрес: %s, браузер: %s, дата: %s' % (request.META['HTTP_HOST'], request.META['HTTP_USER_AGENT'], date.today().strftime("%d.%m.%Y"))
                user_info=''
                if request.user.is_authenticated():
                    user_info=u'Пользователь ID:%s %s' % (unicode(request.user.id), request.user.email)

                plain_text = render_to_string('mail/feedback.txt', { 'text':msg,
                                                                     'user_email':user_email,
                                                                     'browser_info':browser_info,
                                                                     'user_info':user_info },
                                              context_instance=RequestContext(request))

                subject, from_email, to, bcc = 'Сообщение в службу поддержки Rekvizitka.Ru', settings.EMAIL_HOST_USER, [mail_to,],[]

                action = create_action_id(FEEDBACK_SENT, randint(1, 10000))
                notification_manager.add(action, mail_to, subject, plain_text, plain_text, 10)

                result_json = simplejson.dumps({'error' : False})
                return HttpResponse(mark_safe(result_json))

        result_json = simplejson.dumps({'error' : True})
        return HttpResponse(mark_safe(result_json))

