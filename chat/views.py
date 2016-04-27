# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
import memcache
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.views.generic.base import View
from rek.chat.models import ChatDialog, DialogMessage
from rek.chat_tornadio.utils import get_cts
from rek.rekvizitka.models import CompanyEmployee, Company
from rek.rekvizitka.templatetags import portal

INITIAL_DIALOG_MESSAGE_COUNT = 2
SHOW_MORE_MESSAGE_COUNT = 10

mem_cache = memcache.Client(['127.0.0.1:11211'])

def is_employee_online(employee_id):
    return mem_cache.get('on-%s' % str(employee_id)) == 1

def get_message_list_data(message_list, employee_tz):
    return [{'date' : message['date'].astimezone(employee_tz).isoformat(),
             'text' : message['text'],
             'author' : unicode(message['creator']),
             'id' : unicode(message['_id'])} for message in message_list]

class DialogListInitialsView(View):
    @classmethod
    def generate_data_obj(cls, employee, company):
        data = {'rekid' : company.rek_id,
                'brandname' : company.brand_name,
                'emplid' : unicode(employee._id),
                'company_logo' : company.get_logo_url(),
                'categorytext' : company.category_text}
        dialogs = ChatDialog.objects.get({'parties' : employee._id,
                                          'last_message_party' : {'$ne' : None},
                                          'hidden_by_parties' : {'$ne' : employee._id}})

        dialog_list_data = []
        companion_employee_list = {}
        data['dialogs'] = dialog_list_data
        data['correspts'] = companion_employee_list
        employee_id_set = set()
        employee_tz = employee.get_tz()
        for dialog in dialogs:
            if not dialog.last_message_party: # empty dialog
                continue
            companion_employees = dialog.parties
            try:
                companion_employees.remove(employee._id)
            except ValueError:
                pass

            employee_id_set.update(companion_employees)
            companion_employee = companion_employees[0] if len(companion_employees) else None
            if companion_employee:
                dialog_data = {'id' : unicode(dialog._id),
                               'correspt' : unicode(companion_employee),
                               'isViewed' : employee._id not in dialog.not_viewed_by_parties,
                               'lastmessage' : {
                                    'text' : dialog.last_message_text,
                                    'correspt' : unicode(dialog.last_message_party),
                                    'time' : dialog.last_message_date.astimezone(employee_tz).isoformat() if dialog.last_message_date else u'',
                                    'id' : unicode(dialog.last_message_id)}
                               }
                dialog_list_data.append(dialog_data)

        employee_id_set.add(employee._id)
        for companion_employee_id in employee_id_set:
            try:
                companion_employee = CompanyEmployee.objects.get_one({'_id' : companion_employee_id})
                if companion_employee:
                    company = Company.objects.get_one({'_id' : companion_employee.company_id})
                    companion_employee_list[unicode(companion_employee_id)] = {'avatarurl' : companion_employee.get_avatar_url(),
                                                                               'fullname' : companion_employee.get_full_name(),
                                                                               'companyname' : company.brand_name if company else u"",
                                                                               'online' : is_employee_online(companion_employee._id),
                                                                               'company_rek_id' : company.rek_id}
            except Exception:
                pass

        return data

    def get(self, request):
        employee = request.employee
        company = request.company

        data = self.generate_data_obj(employee, company)
        data.update(portal.get_common_data_for_company(request, company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class DialogInitialsView(View):
    @classmethod
    def generate_data_obj(cls, dialog, my_employee, my_company):
        companions = dialog.parties
        try:
            companions.remove(my_employee._id)
        except ValueError:
            pass
        dialog_companion = companions[0] if len(companions) else None

        if not dialog_companion:
            mark_safe(simplejson.dumps({}))

        companion_set = set([dialog_companion])

        employee_tz = my_employee.get_tz()
        messages = []
        data = {'dialog' : {
                    'id' : unicode(dialog._id),
                    'messages' : messages,
                    'isViewed' : my_employee._id not in dialog.not_viewed_by_parties,
                    'correspt' : unicode(dialog_companion),
                    'lastmessage' : {
                        'text' : dialog.last_message_text,
                        'correspt' : unicode(dialog.last_message_party),
                        'time' : dialog.last_message_date.astimezone(employee_tz).isoformat() if dialog.last_message_date else u'',
                        'id' : unicode(dialog.last_message_id)}if dialog.last_message_party else None
                    }
        }

        companion_set.add(my_employee._id)

        data.update({'rekid' : my_company.rek_id,
                     'brandname' : my_company.brand_name,
                     'emplid' : unicode(my_employee._id),
                     'company_logo' : my_company.get_logo_url(),
                     'categorytext' : my_company.category_text})

        data['correspts'] = {}
        for companion_id in companion_set:
            companion = CompanyEmployee.objects.get_one({'_id' : companion_id})
            if companion:
                company = Company.objects.get_one({'_id' : companion.company_id})
                brand_name = company.brand_name if company else u'<Неизвестно>'
                data['correspts'][unicode(companion._id)] = {'fullname' : companion.get_full_name(),
                                                              'companyname' : brand_name,
                                                              'avatarurl' : companion.get_avatar_url(),
                                                              'online' : is_employee_online(companion._id),
                                                              'company_rek_id' : company.rek_id if company else u''}

        last_messages = DialogMessage.objects.collection.find({'dialog' : dialog._id}).sort('date', -1).limit(INITIAL_DIALOG_MESSAGE_COUNT + 1)
        messages_count = last_messages.count(True)
        has_more = messages_count == INITIAL_DIALOG_MESSAGE_COUNT + 1

        if has_more:
            messages.extend(get_message_list_data(last_messages, employee_tz)[0:-1])
        else:
            messages.extend(get_message_list_data(last_messages, employee_tz))

        data['dialog']['has_more'] = has_more

        return data

    def get(self, request, dialog_id):
        try:
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'parties' : request.employee._id})
            if not dialog:
                raise Exception()
        except Exception:
            return HttpResponse(mark_safe(simplejson.dumps({'error' : True, 'msg' : 'No such dialog'})))

        data = self.generate_data_obj(dialog, request.employee, request.company)
        data.update(portal.get_common_data_for_company(request, request.company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class DialogListView(View):
    def get(self, request):
        company = request.company
        employee = request.employee

        data = DialogListInitialsView.generate_data_obj(employee, company)
        data.update(portal.get_common_data_for_company(request, company))
        module_init = mark_safe(simplejson.dumps(data))
        response = render_to_response('apps/chat/dialoglist/templates/template.html',
                {
                'chat_module_init' : module_init,
                'sidebar_mode' : 'some_company',
                'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))
        response.set_cookie('cts', get_cts(), max_age=3600)
        return response

class ChatDialogView(View):
    def get(self, request, dialog_id):
        employee = request.employee
        try:
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'hidden_by_parties' : {'$ne' : employee._id},
                                                 'parties' : employee._id})
            if not dialog:
                raise Exception()
        except Exception:
            raise Http404()

        company = request.company

        data = DialogInitialsView.generate_data_obj(dialog, employee, company)
        data.update(portal.get_common_data_for_company(request, company))
        module_initials = mark_safe(simplejson.dumps(data))
        response = render_to_response('apps/chat/dialog/templates/template.html',
                {
                'chat_module_init' : module_initials,
                'sidebar_mode' : 'some_company',
                'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))
        response.set_cookie('cts', get_cts(), max_age=3600)
        return response

class CreateDialogView(View):
    def get_dialog_initials(self, dialog, employee, employee_tz, my_company, my_employee):
        last_messages = DialogMessage.objects.collection.find({'dialog' : dialog._id}).sort('date', -1).limit(INITIAL_DIALOG_MESSAGE_COUNT)
        dialog_data = {'dialog' : {
                'id' : unicode(dialog._id),
                'messages' : get_message_list_data(last_messages, employee_tz),
            },
            'rekid' : my_company.rek_id,
            'brandname' : my_company.brand_name,
            'emplid' : unicode(my_employee._id),
            'company_logo' : my_company.get_logo_url(),
            'categorytext' : my_company.category_text
        }
        dialog_data['dialog']['companion'] = unicode(employee._id)

        company = Company.objects.get_one({'_id' : employee.company_id})
        brand_name = company.brand_name if company else u'Неизвестная компания'
        dialog_data['companion'] = {'id' : unicode(employee._id),
                                    'fullname' : employee.get_full_name(),
                                    'logo_url' : employee.get_avatar_url(),
                                    'brandname' : unicode(brand_name),
                                    'online' : is_employee_online(employee._id),
                                    'company_rek_id' : company.rek_id if company else u''}
        return dialog_data

    def post(self, request, companion_id):
        try:
            companion_employee = CompanyEmployee.objects.get_one({'_id' : ObjectId(companion_id)})
            if not companion_employee:
                raise Exception()
        except Exception:
            return HttpResponse(mark_safe(simplejson.dumps({'error':True})))

        my_employee = request.employee
        my_company = request.company
        if not my_company.is_active():
            return HttpResponse(mark_safe(simplejson.dumps({'error':True})))

        employee_tz = my_employee.get_tz()
        if my_employee._id == companion_employee._id:
            return HttpResponse(mark_safe(simplejson.dumps({'error':True})))

        existing_dialog = ChatDialog.objects.get_one({'parties' : {'$all' : [my_employee._id, companion_employee._id]}})
        if existing_dialog:
            return HttpResponse(mark_safe(simplejson.dumps(self.get_dialog_initials(existing_dialog, companion_employee, employee_tz, my_company, my_employee))))

        new_dialog = ChatDialog({'parties' : [my_employee._id, companion_employee._id],
                                 'creator' : my_employee._id})
        new_dialog.save()
        return HttpResponse(mark_safe(simplejson.dumps(self.get_dialog_initials(new_dialog, companion_employee, employee_tz, my_company, my_employee))))

class DeleteDialogView(View):
    def get(self, request, dialog_id):
        employee = request.employee
        try:
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'parties' : employee._id})
            if not dialog:
                raise Exception()
        except Exception:
            return HttpResponse(mark_safe(simplejson.dumps({'error' : True, 'msg' : 'dialog not found'})))

        ChatDialog.objects.collection.update({'_id' : dialog._id},
                                             {'$addToSet' : {'hidden_by_parties' : employee._id}})
        return HttpResponse(mark_safe(simplejson.dumps({})))

class MoreMessagesView(View):
    def get(self, request, dialog_id):
        employee = request.employee
        try:
            start = int(request.GET.get('s', '0').strip())
            if start < 0:
                start = 0
        except Exception:
            start = 0

        try:
            count = int(request.GET.get('n', str(SHOW_MORE_MESSAGE_COUNT)).strip())
            if count > 1000 or count < 1:
                count = SHOW_MORE_MESSAGE_COUNT
        except Exception:
            count = SHOW_MORE_MESSAGE_COUNT

        try:
            dialog = ChatDialog.objects.get_one({'_id' : ObjectId(dialog_id),
                                                 'last_message_party' : {'$ne' : None},
                                                 'parties' : employee._id})
            if not dialog:
                raise Exception()
        except Exception:
            return HttpResponse(mark_safe(simplejson.dumps({'error' : True, 'msg' : 'dialog not found'})))

        messages = DialogMessage.objects.collection.find({'dialog' : dialog._id}).sort('date', -1).skip(start).limit(count + 1)
        messages_count = messages.count(True)
        has_more = messages_count == count + 1

        employee_tz = employee.get_tz()
        if has_more:
            message_list = get_message_list_data(messages, employee_tz)[0:-1]
        else:
            message_list = get_message_list_data(messages, employee_tz)
        return HttpResponse(mark_safe(simplejson.dumps({'messages' : message_list,
                                                        'has_more' : has_more})))
