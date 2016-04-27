# -*- coding: utf-8 -*-

import bson
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic.base import View
from rek.mail_messages.messages_manager import MailMessage, messages_manager
from rek.mail_messages.settings_manager import messages_user_settings_manager
from rek.mongo.mongo_utils import mongodb_datetime_now
from rek.rekvizitka import utils
from rek.rekvizitka.models import Company, CompanyEmployee, get_user_employee

class CompanyMessagesView(View):
    template_name = "apps/messaging/letters_page/templates/letters_page.html"
    def get(self, request):
        res_dict = { 'init_module' : MessageModuleInitialsView.generate_module(request)}
        return render_to_response(self.template_name, res_dict, context_instance=RequestContext(request))

class CompanyContactsView(CompanyMessagesView):
    template_name = "apps/messaging/contacts_page/templates/contacts_page.html"

class CompanySettingsView(CompanyMessagesView):
    template_name = "apps/messaging/settings_page/templates/settings_page.html"

class MessageModuleInitialsView(View):

    @classmethod
    def generate_module(cls, request):
        user_message_settings = messages_user_settings_manager.get_user_settings(request.user.id)

        message_folders = {
            'inbox_folder': (MailMessage.FOLDER_INBOX , messages_manager.get_message_count(request.user.id, MailMessage.FOLDER_INBOX)),
            'sent_folder': (MailMessage.FOLDER_SENT, messages_manager.get_message_count(request.user.id, MailMessage.FOLDER_SENT)),
            'spam_folder': (MailMessage.FOLDER_SPAM, messages_manager.get_message_count(request.user.id, MailMessage.FOLDER_SPAM)),
            'draft_folder': (MailMessage.FOLDER_DRAFT, messages_manager.get_message_count(request.user.id, MailMessage.FOLDER_DRAFT)),
            'deleted_folder': (MailMessage.FOLDER_DELETED, messages_manager.get_message_count(request.user.id, MailMessage.FOLDER_DELETED))
        }

        res_dict = {
            'user_message_settings': user_message_settings,
            'message_folders': message_folders,
            'default_mail_folder': MailMessage.FOLDER_INBOX
        }
        return render_to_string("modules/messaging/messaging_application__init/templates/messaging_application__init.js", res_dict, RequestContext(request))

    def get(self, request):
        return HttpResponse(MessageModuleInitialsView.generate_module(request), mimetype="application/x-javascript")

def get_unicode_mail_headers(headers):
    return [{'DATE': u'%s' % header[u'DATE'],
             'FROM': u'%s' % header[u'FROM'],
             'TO': u'%s' % header[u'TO'] } for header in headers]

def append_companies_list(company_rek, companies_list):
    is_exist = False
    for company in companies_list:
        if company['rek'] == company_rek:
            is_exist = True
            break
    if not is_exist:
        try:
            added_company = Company.objects.get(id=utils.code_to_integer(company_rek))
        except Company.DoesNotExist:
            return companies_list
        
        companies_list.append({
            'rek': company_rek, #REK_ID
            'brand': added_company.brandname,
            'url': added_company.url,
            'logo': added_company.get_logo().url,
        })
    return companies_list

def append_employees_list(employee_id, employees_list):
    is_exist = False
    for employee in employees_list:
        if employee['id'] == employee_id:
            is_exist = True
            break
    if not is_exist:
        try:
            employee_user = User.objects.get(id = employee_id)
        except User.DoesNotExist:
            return employees_list
        try:
            added_employee = CompanyEmployee.objects.get(user = employee_user)
        except CompanyEmployee.DoesNotExist:
            return employees_list
        
        employees_list.append({
            'id': employee_id,
            'avatar': added_employee.get_avatar(),
            'full_name': added_employee.full_name,
            'position': added_employee.title,
            'email': added_employee.user.email,
        })
    return employees_list

class MessagesCollectionView(View):
    def post(self, request):

        try:
            startIndex = request.POST.get('start') or 0
            if startIndex:
                startIndex = int(startIndex)
            count = request.POST.get('count')
            if count:
                count = int(count)
            else:
                return HttpResponseBadRequest("can't fetch all messages")
            version = request.POST.get('v')
            if version:
                version = int(version)
        except ValueError:
            return HttpResponseBadRequest("can't fetch all messages")

        folder = request.POST.get('folder') or MailMessage.FOLDER_INBOX

        user_id = self.request.user.id
        if not user_id:
            return HttpResponseBadRequest("Can't find user")
        
        result_messages = []

        message_list = messages_manager.get_messages(owner = user_id, limit = count, skip = startIndex, folder = bson.ObjectId(folder))

        for msg in message_list:
            sender_company_rek = msg.company_rek
            sender = msg.headers[-1][u'FROM']

            result_msg_data = {
                'id': unicode(msg._id),
                'subject' : msg.subject,
                'content' : msg.text,
                'sentDate': unicode(msg.send_date),
                'author': sender,
                'from_company_rek': sender_company_rek
            }
            if msg.is_important:
                result_msg_data['important'] = 1
            if msg.is_official:
                result_msg_data['official'] = 1
            if msg.is_read:
                result_msg_data['read'] = 1
            if msg.is_auto_answer:
                result_msg_data['aanswer'] = 1
            if msg.is_deleted:
                result_msg_data['deleted'] = 1

            result_messages.append(result_msg_data)

        result_json = simplejson.dumps({'messages' : result_messages, 'folder' : unicode(folder)})
        return HttpResponse(result_json, mimetype='application/javascript')

class SetMessageImportant(View):
    def post(self, request):
        result_status = 5 #unknown_error
        message_id = None

        user_id = self.request.user.id
        if not user_id:
            result_status = 1 #User not found

        if 'message_id' in request.POST:
            message_id = request.POST['message_id']
        else:
            result_status = 2 #Bad request

        if result_status == 5:
            message = messages_manager.get_one_message(bson.ObjectId(message_id), user_id)
            message.is_important = not message.is_important
            message.save()
            if message.is_important:
                result_status = 3 #ok true
            else:
                result_status = 4 #ok false

        return HttpResponse(simplejson.dumps({'result_status': result_status}), mimetype='application/javascript')

class ContactsCollectionView(View):
    def get(self, request):
        result=[]
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

class SettingsCollectionView(View):
    def get(self, request):
        result=[]
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')


#Test functions

class ViewForm(View):
    def get(self, request):
        return render_to_response('send_form.html', context_instance=RequestContext(request))

class AddMessages(View):
    def get(self, request):
        owner_id = self.request.user.id
        from_id = 28
        employee = get_user_employee(self.request.user)
        company_rek = employee.company.code_view

        for i in xrange(20):
            mail_text = 'text text text %d' % i
            mail_subject = 'subject %d' % i
            message = MailMessage(owner = owner_id, text = mail_text, company_rek = company_rek, subject = mail_subject,folder = MailMessage.FOLDER_INBOX, headers= [{'FROM':from_id, 'TO':owner_id, 'DATE':mongodb_datetime_now()}])
            message.save()


        return HttpResponse('True', mimetype='text/html')
