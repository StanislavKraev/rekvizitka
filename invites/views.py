# -*- coding: utf-8 -*-
import bson
from bson.objectid import ObjectId
from django.conf import settings
from django.core.urlresolvers import reverse

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import Context, RequestContext
from django.template.loader import get_template, render_to_string
from django.utils import simplejson, timezone
from django.utils.safestring import mark_safe
from django.utils.timezone import utc
from django.views.generic.base import View
from django.core.mail.message import EmailMultiAlternatives

from rek.billing.models import Invoice, InvoiceStatusEnum
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id, RECOMMENDATION_ASKED, INVITATION
from rek.deferred_notification.manager import notification_manager
from rek.invites.models import  RecommendationRequest, RecommendationStatusEnum, Invite
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import   Company
from rek.rekvizitka.permissions import CompanyPermission
from rek.rekvizitka.templatetags import portal
from rek.rekvizitka.utils import is_valid_email
from rek.system_data.rek_settings import SettingsManager

class  RecommendationCollectionView(View):
    def get(self, request):
        company = request.company

        recommendation_list = RecommendationRequest.objects.get({'recipient' : company._id,
                                                                 'status' : RecommendationStatusEnum.RECEIVED})

        result=[]
        for rcm in recommendation_list:
            result_data = {
                'recommendation_id' : str(rcm._id),
                'message' : rcm.message,
                'requester' : str(rcm.requester),
                'viewed': rcm.viewed
            }
            result.append(result_data)

        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

class AcceptRecommendationView(View):
    def send_accepted_message(self, email, company_name):
        # mustdo: send through deferred notification system
        mail_context = {'company_name': company_name}
        plain_text_template = get_template('mail/recommendet.txt')
        plain_text = plain_text_template.render(Context(mail_context))
        html_template = get_template('mail/recommendet.html')
        html = html_template.render(Context(mail_context))
        subject, from_email, to, bcc = 'Ваша компания рекомендована в Реквизитке', settings.EMAIL_HOST_USER, [email,], []
        msg = EmailMultiAlternatives(subject, plain_text, from_email, to, bcc)
        msg.attach_alternative(html, "text/html")
        msg.send()

    def post(self, request, recommendation_id):
        # mustdo: add transaction
        company = request.company
        try:
            recommendation_id_obj = bson.ObjectId(recommendation_id)
        except Exception:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Запрос не найден."}),
                mimetype='application/javascript')

        recommendation = RecommendationRequest.objects.get_one({'_id' : recommendation_id_obj,
                                                                'recipient' : company._id,
                                                                'status' : RecommendationStatusEnum.RECEIVED})

        if not recommendation:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Запрос не найден."}),
                                                   mimetype='application/javascript')

        RecommendationRequest.objects.update({'_id' : recommendation_id_obj},
                                             {'$set' : {'status' : RecommendationStatusEnum.ACCEPTED}})

        company_to_recommend = recommendation.requester
        Company.objects.update({'_id' : recommendation.recipient}, {'$pull' : {'rec_requesters' : company_to_recommend}})
        accepted_requests_count = RecommendationRequest.objects.count({'status' : RecommendationStatusEnum.ACCEPTED,
                                                                       'requester' : company_to_recommend})
        if accepted_requests_count >= SettingsManager.get_property('rnes'):
            requester_company = Company.objects.get_one({'_id' : company_to_recommend})
            if requester_company.account_status == CompanyAccountStatus.JUST_REGISTERED:
                Company.objects.update({'_id' : company_to_recommend},
                                       {'$set' : {'account_status' : CompanyAccountStatus.VERIFIED}})
                notification_manager.remove(create_action_id(actions.VERIFICATION_PERIODIC, unicode(company_to_recommend)))

                self.send_accepted_message(recommendation.requester_email, company.brand_name)

        return HttpResponse(simplejson.dumps({'error' : False,
                                              'success_message' : "Рекомендация подтверждена."}),
                                               mimetype='application/javascript')

class GiveRecommendationView(View):
    def post(self, request, code):
        my_company = request.company
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            raise Http404()

        recommendation = RecommendationRequest.objects.get_one({'recipient' : my_company._id,
                                                                'requester' : company._id})

        if recommendation:
            if recommendation.status == RecommendationStatusEnum.ACCEPTED:
                return HttpResponse(simplejson.dumps({'error' : True, 'error_message' : "Already given"}), mimetype='application/javascript')
            if recommendation.status == RecommendationStatusEnum.RECEIVED:
                proxy_view = AcceptRecommendationView()
                return proxy_view.post(request, unicode(recommendation._id))
            RecommendationRequest.objects.collection.remove({'_id' : recommendation._id})

        new_recommendation = RecommendationRequest({'recipient' : my_company._id,
                                                    'requester' : company._id,
                                                    'status' : RecommendationStatusEnum.ACCEPTED})
        new_recommendation.save()
        return HttpResponse('{}', mimetype='application/javascript')

class TakeAwayRecommendationView(View):
    def post(self, request, code):
        my_company = request.company
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            raise Http404()

        recommendation = RecommendationRequest.objects.get_one({'recipient' : my_company._id,
                                                                'requester' : company._id,
                                                                'status' : RecommendationStatusEnum.ACCEPTED})

        if not recommendation:
            return HttpResponse(simplejson.dumps({'error' : True, 'msg' : 'Not found'}), mimetype='application/javascript')
        RecommendationRequest.objects.collection.remove({'_id' : recommendation._id})

        return HttpResponse('{}', mimetype='application/javascript')

class DeclineRecommendationView(View):
    def post(self, request, recommendation_id):
        company = request.company

        try:
            recommendation_id_obj = bson.ObjectId(recommendation_id)
        except Exception:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Запрос не найден."}),
                mimetype='application/javascript')

        recommendation = RecommendationRequest.objects.get_one({'_id' : recommendation_id_obj,
                                                                'recipient' : company._id,
                                                                'status' : RecommendationStatusEnum.RECEIVED})

        if not recommendation:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Запрос не найден."}),
                mimetype='application/javascript')

        RecommendationRequest.objects.update({'_id' : recommendation_id_obj},
                                             {'$set' : {'status' : RecommendationStatusEnum.DECLINED}})

        Company.objects.update({'_id' : recommendation.recipient}, {'$pull' : {'rec_requesters' : recommendation.requester}})

        return HttpResponse(simplejson.dumps({'error' : False,
                                              'success_message' : "Рекомендация закрыта."}),
                                               mimetype='application/javascript')

class AskForRecommendationView(View):
    def send_rec_message(self, email, message, rec_id, recipient_rek_id, requester_brand_name):
        mail_context = {'text': message,
                        'company_name' : requester_brand_name,
                        'our_recommendations_url' : "http://%s%s" % (settings.SITE_DOMAIN_NAME,
                                                                     reverse('we_recommend_view', kwargs={'code' : recipient_rek_id}))}
        plain_text_template = get_template('mails/recommended.txt')
        plain_text = plain_text_template.render(Context(mail_context))
        html_template = get_template('mails/recommended.html')
        html = html_template.render(Context(mail_context))
        subject = 'Запрос рекомендации на сайте Rekvizitka.Ru'

        action = create_action_id(RECOMMENDATION_ASKED, rec_id)
        notification_manager.add(action, email, subject, plain_text, html, 120)
    
    def post(self, request, code):
        try:
            rec_message = request.POST['message']
        except Exception:
            return HttpResponseBadRequest("No message field")

        company_to_ask = Company.get_active_company_by_rek_id(code)
        if not company_to_ask:
            return HttpResponseNotFound("Company with rec id %s can not be found." % code)
        my_company = request.company
        employee = request.employee

        check = CompanyPermission(request.user, employee, my_company)
        result_dict = {}
        if not check.can_ask_recommendation(company_to_ask, result_dict):
            if len(result_dict):
                result_dict['error'] = True
                return HttpResponse(simplejson.dumps(result_dict), mimetype='application/javascript')
            return HttpResponseForbidden("Can't ask for a recommendation")

        rec = RecommendationRequest({'requester' : my_company._id,
                                     'recipient' : company_to_ask._id,
                                     'message' : rec_message,
                                     'requester_email' : request.user.email})
        rec.save()
        if my_company._id not in company_to_ask.rec_requesters:
            company_to_ask.rec_requesters.append(my_company._id)
            Company.objects.collection.update({'_id' : company_to_ask._id}, {'$push' : {'rec_requesters' : my_company._id} })

        admin_user, admin_employee = company_to_ask.get_admin_user()

        requester_brand_name = my_company.brand_name
        recipient_rek_id = code
        self.send_rec_message(admin_user.email, rec_message, rec._id, recipient_rek_id, requester_brand_name)

        return HttpResponse(simplejson.dumps({'success' : True,
                                              'max_req_count_reached' : RecommendationRequest.objects.count({'requester' : my_company._id}) >= SettingsManager.get_property('rmax')        }),
                                               mimetype='application/javascript')

class RecommendInitialsView(View):
    @classmethod
    def generate_data_obj(cls, company, my_company, employee = None):
        own = False
        if my_company and company.rek_id == my_company.rek_id:
            own = True

        if not own and not company.is_active():
            return {}

        data = {"categoryText" : company.category_text or "",
                "brandName" : company.brand_name,
                "rek_id" : company.rek_id,
                "own" : own,
                "verify_rec_number" : SettingsManager.get_property("rnes"),
                "company_logo" : company.get_logo_url(),
                "authorized" : my_company is not None,
                "verified" : CompanyAccountStatus.is_active_account(company.account_status),
                "employee_id" : unicode(employee) if employee else u""}

        company_id = company._id
        if own:
            invoice = Invoice.objects.get_one({'expire_date' : {'$gte' : timezone.now()},
                                               'payer' : my_company._id,
                                               'status' : InvoiceStatusEnum.CREATED})
            if invoice:
                employee_tz = utc
                issued = invoice.create_date.astimezone(employee_tz)
                data['bill'] = {'id' : unicode(invoice._id),
                                 'service_title' : invoice.position,
                                 'price' : invoice.price,
                                 'status' : invoice.status,
                                 'issued' : issued.strftime('%d.%m.%Y %H:%M'),
                                 'number' : invoice.number}

        corresponding_rec_reqs = RecommendationRequest.objects.get({'$or' : [{'requester' : company_id},
                                                                             {'recipient' : company_id}]})

        sent_not_accepted_list = []
        sent_accepted_list = []
        received_accepted = []
        received_not_accepted = []

        max_req_count = 0

        for rec in corresponding_rec_reqs:
            if rec.requester == company_id:
                acceptor = Company.objects.get_one({'_id' : rec.recipient})
                max_req_count += 1
                if acceptor:
                    if rec.status == RecommendationStatusEnum.RECEIVED:
                        sent_not_accepted_list.append({
                            'rek_id' : acceptor.rek_id,
                            'brand_name' : acceptor.brand_name
                        })
                    elif rec.status == RecommendationStatusEnum.ACCEPTED:
                        sent_accepted_list.append({
                            'rek_id' : acceptor.rek_id,
                            'brand_name' : acceptor.brand_name,
                            'logo' : acceptor.get_some_logo_url(kind='list_logo'),
                            'kind_of_activity' : acceptor.category_text
                        })
            elif rec.recipient == company_id:
                sender = Company.objects.get_one({'_id' : rec.requester})
                if sender:
                    if rec.status == RecommendationStatusEnum.ACCEPTED:
                        received_accepted.append({'rek_id' : sender.rek_id,
                                                  'brand_name' : sender.brand_name})
                    elif rec.status == RecommendationStatusEnum.RECEIVED:
                        received_not_accepted.append({
                            'rek_id' : sender.rek_id,
                            'brand_name' : sender.brand_name,
                            'logo' : sender.get_some_logo_url(kind='list_logo'),
                            'kind_of_activity' : sender.category_text,
                            'request_id' : unicode(rec._id),
                            'msg' : rec.message
                        })

        max_req_count_reached = max_req_count >= SettingsManager.get_property('rmax')

        data.update({'sent_accepted_list' : sent_accepted_list,
                     'received_accepted' : received_accepted})

        if own:
            data.update({'sent_not_accepted_list' : sent_not_accepted_list,
                         'received_not_accepted' : received_not_accepted,
                         'max_req_count_reached' : max_req_count_reached})

        if own:
            my_company_id = my_company._id
            sent_invites_obj_list = Invite.objects.get({'sender' : my_company_id})
            sent_invites_not_used = []
            sent_invites_used = []
            for invite_obj in sent_invites_obj_list:
                if invite_obj.rec_request:
                    invited_rec = RecommendationRequest.objects.get_one({'_id' : invite_obj.rec_request})
                    if not invited_rec:
                        continue
                    invited_company = Company.objects.get_one({'_id' : invited_rec.requester})
                    if not invited_company:
                        continue
                    sent_invites_used.append({
                        'brand_name' : invited_company.brand_name,
                        'rek_id' : invited_company.rek_id
                    })
                else:
                    sent_invites_not_used.append({
                        'email' : invite_obj.email,
                        'date' : invite_obj.created.strftime('%d.%m.%Y')
                    })

            data.update({'sent_invites' : sent_invites_not_used,
                         'sent_registered_invites' : sent_invites_used})
        return data

    def get(self, request, code):
        my_company = getattr(request, 'company', None)
        employee = getattr(request, 'employee', None)
        company = Company.objects.get_one({'rek_id' : code})

        if not company:
            raise Http404()

        data = self.generate_data_obj(company, my_company, company.owner_employee_id)
        data.update(portal.get_common_data_for_company(request, company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class RecommendView(View):
    template = 'apps/recommendations/template.html'
    def get(self, request):
        if not hasattr(request, 'company'):
            raise Http404()
        company = request.company
        employee = request.employee

        data = RecommendInitialsView.generate_data_obj(company, company, employee._id)
        data.update(portal.get_common_data_for_company(request, company))
        recommend_module_init = mark_safe(simplejson.dumps(data))

        return render_to_response(self.template, {
            'recommend_module_init' : recommend_module_init,
            'sidebar_mode' : 'some_company',
            'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))


class VerifyRecommendView(RecommendView):
    template = 'apps/recommendations/verification/templates/template.html'

    def get(self, request):
        if not hasattr(request, 'company'):
            raise Http404()
        company = request.company
        if company.account_status == CompanyAccountStatus.VERIFIED:
            return HttpResponseRedirect('/')
        employee = request.employee

        data = RecommendInitialsView.generate_data_obj(company, company, employee._id)
        data.update(portal.get_common_data_for_company(request, company))
        recommend_module_init = mark_safe(simplejson.dumps(data))
        return render_to_response(self.template, {
            'recommend_module_init' : recommend_module_init,
            'sidebar_mode' : 'some_company',
            'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))

class OurProposersRecommendView(View):
    template = 'apps/recommendations/our_proposers/templates/template.html'
    def get(self, request, code):
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            raise Http404()
        my_company = getattr(request, 'company', None)
        employee = getattr(request, 'employee', None)

        data = RecommendInitialsView.generate_data_obj(company, my_company, company.owner_employee_id)
        data.update(portal.get_common_data_for_company(request, company))
        recommend_module_init = mark_safe(simplejson.dumps(data))

        return render_to_response(self.template, {
            'recommend_module_init' : recommend_module_init,
            'sidebar_mode' : 'some_company',
            'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))

class WeRecommendRecommendView(View):
    template = 'apps/recommendations/we_recommend/templates/template.html'
    def get(self, request, code):
        company = Company.objects.get_one({'rek_id' : code})
        if not company:
            raise Http404()
        my_company = getattr(request, 'company', None)
        employee = getattr(request, 'employee', None)

        data = RecommendInitialsView.generate_data_obj(company, my_company, company.owner_employee_id)
        data.update(portal.get_common_data_for_company(request, company))
        recommend_module_init = mark_safe(simplejson.dumps(data))

        return render_to_response(self.template, {
            'recommend_module_init' : recommend_module_init,
            'sidebar_mode' : 'some_company',
            'sidebar_initial_data' : company
            }, context_instance = RequestContext(request))

class InvitesRecommendView(RecommendView):
    template = 'apps/recommendations/invites/templates/template.html'

class SendInviteView(View):
    def send_invitation_message(self, email, invite_id, message, brand_name, cookie_code):
        mail_context = {'text' : message,
                        'brand_name' : brand_name,
                        'join_url' : u"http://%s/invites/join/%s/" % (settings.SITE_DOMAIN_NAME, cookie_code),
                        'main_page_link' : u"http://%s/" % settings.SITE_DOMAIN_NAME }

        subject = 'Вас пригласили в деловую сеть Реквизитка'

        plain_text = render_to_string('mail/invite.txt', dictionary=mail_context)
        html = render_to_string('mail/invite.html', dictionary=mail_context)

        action = create_action_id(INVITATION, invite_id)
        notification_manager.add(action, email, subject, plain_text, html, 0)

    def post(self, request):
        if not request.company:
            return HttpResponseBadRequest()

        data = {'success' : True }

        message = request.POST.get('msg', '').strip()
        email = request.POST.get('email', '').strip().lower()

        if not is_valid_email(email):
            data = {'success' : False,
                    'email_invalid' : True}
            return HttpResponse(simplejson.dumps(data), mimetype="application/x-javascript")

        if not len(message):
            return HttpResponseBadRequest()

        if User.collection.find({'email' : email}).count():
            data = {'success' : False,
                    'email_exists' : True}
            return HttpResponse(simplejson.dumps(data), mimetype="application/x-javascript")

        invite = Invite({'message' : message,
                         'email' : email,
                         'sender' : request.company._id})
        invite.save()
        self.send_invitation_message(email, invite._id, message, request.company.brand_name, invite.cookie_code)

        return HttpResponse(simplejson.dumps(data), mimetype="application/x-javascript")

class JoinByInviteView(View):
    def get(self, request, cookie_code):
        try:
            cookie_code_obj = ObjectId(cookie_code)
            invite = Invite.objects.get_one({'cookie_code' : cookie_code, 'rec_request' : None})
            if not invite:
                raise Exception('Not found')

            response = HttpResponseRedirect('/')
            response.set_cookie('invite', cookie_code, max_age=3600 * 30)
            return response
        except Exception:
            pass

        return HttpResponseRedirect('/')
