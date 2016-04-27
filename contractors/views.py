# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.views.generic.base import View
import itertools
from rek.contractors.models import Contractor, ContractorStatusEnum, ContractorPrivacy
from rek.contractors.permissions import ContractorPermission
from rek.rekvizitka.models import Company
from rek.rekvizitka.templatetags import portal

class ContractorsInitialsView(View):

    @classmethod
    def serialize_data(cls, contractor_data, viewed):
        result = {}
        for key in contractor_data:
            result[key] = unicode(contractor_data[key])
        result['viewed'] = viewed
        return result

    @classmethod
    def generate_data_obj(cls, company, my_company):

        own = my_company is not None and my_company.rek_id == company.rek_id

        outgoing_items = []
        incoming_items = []

        items = Contractor.objects.collection.find({'$or' : [{'company_1' : company._id},
                                                             {'company_2' : company._id}]})
        items_list = [item for item in items]
        if own:
            outgoing_items = [cls.serialize_data(item['company_2_data'], item['viewed']) for item in itertools.ifilter(
                lambda item: item['status'] == ContractorStatusEnum.RECEIVED and item['company_1'] == company._id, items_list)]

            incoming_items = [cls.serialize_data(item['company_1_data'], item['viewed']) for item in itertools.ifilter(
                lambda item: item['status'] == ContractorStatusEnum.RECEIVED and item['company_2'] == company._id, items_list)]

        checker = ContractorPermission(my_company, company)
        rek_partners = []
        for item in items_list:
            if item['status'] != ContractorStatusEnum.ACCEPTED:
                continue
            contractor_data = item['company_2_data'] if item['company_1'] == company._id else item['company_1_data']
            if not checker.can_view_contractor(contractor_data):
                continue
            rek_partners.append(cls.serialize_data(contractor_data, item['viewed']))

        data = { 'brand_name' : company.brand_name,
                 'category_text' : company.category_text or "",
                 'rek_id' : company.rek_id,
                 'own' : own,
                 'rek_partners' : rek_partners,
                 'incoming_requests' : incoming_items,
                 'outgoing_requests' : outgoing_items,
                 'company_logo' : company.get_logo_url()
        }

        return data

    def get(self, request, rek_id):
        my_company = getattr(request, 'company', None)
        try:
            target_company = Company.objects.get_one({'rek_id' : rek_id})
            if not target_company:
                raise Exception
        except Exception:
            raise Http404()

        data = self.generate_data_obj(target_company, my_company)
        data.update(portal.get_common_data_for_company(request, target_company))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class ContractorsView(View):
    template = "apps/partners/partners_list/templates/template.html"
    def get(self, request, rek_id):
        my_company = getattr(request, 'company', None)
        try:
            target_company = Company.objects.get_one({'rek_id' : rek_id})
            if not target_company:
                raise Exception
        except Exception:
            raise Http404()

        data = ContractorsInitialsView.generate_data_obj(target_company, my_company)
        data.update(portal.get_common_data_for_company(request, target_company))
        response_content = mark_safe(simplejson.dumps(data))

        return render_to_response(self.template, {
            'partners_settings_init' : response_content,
            }, context_instance = RequestContext(request))

class IncomingContractorsView(View):
    template = "apps/partners/incoming_requests/templates/template.html"
    def get(self, request):
        my_company = request.company
        data = ContractorsInitialsView.generate_data_obj(my_company, my_company)
        data.update(portal.get_common_data_for_company(request, my_company))
        response_content = mark_safe(simplejson.dumps(data))
        return render_to_response(self.template, {
            'partners_settings_init' : response_content,
            }, context_instance = RequestContext(request))

class OutgoingContractorsView(View):
    template = "apps/partners/outgoing_requests/templates/template.html"
    def get(self, request):
        my_company = request.company
        data = ContractorsInitialsView.generate_data_obj(my_company, my_company)
        data.update(portal.get_common_data_for_company(request, my_company))
        response_content = mark_safe(simplejson.dumps(data))
        return render_to_response(self.template, {
            'partners_settings_init' : response_content,
            }, context_instance = RequestContext(request))

class PartnershipBaseView(View):
    def post(self, request):
        target_company_rek_id = request.POST.get('rek_id', '').strip()
        try:
            target_company = Company.get_active_company_by_rek_id(target_company_rek_id)
            if not target_company:
                raise Exception
            if request.company and target_company._id == request.company._id:
                raise Exception
        except Exception:
            raise Http404()

        return self.handle_request(target_company, request.company)

    def handle_request(self, company, my_company):
        raise Exception('Must be overridden')

class PartnershipRequestView(PartnershipBaseView):
    def handle_request(self, company, my_company):
        existing_contractor = Contractor.objects.get_one({'$or' : [{'company_1' : my_company._id,
                                                                    'company_2' : company._id},
                                                                   {'company_2' : my_company._id,
                                                                    'company_1' : company._id}]})
        if existing_contractor:
            if existing_contractor.company_2 == my_company._id:
                Contractor.objects.collection.update({'_id' : existing_contractor._id},
                                                     {'$set' : {'status' : ContractorStatusEnum.ACCEPTED}})
                Company.objects.collection.update({'_id' : my_company._id},
                        {'$push' : {'contractors' : make_company_contractor(company)}})
                Company.objects.collection.update({'_id' : company._id},
                        {'$push' : {'contractors' : make_company_contractor(my_company)}})

                return HttpResponse("{}", mimetype="application/x-javascript")
            return HttpResponse('{"error":true, "msg":"Already in contractors lists"}', mimetype="application/x-javascript")

        new_contractor = Contractor({'company_1' : my_company._id,
                                     'company_2' : company._id,
                                     'company_1_data' : {
                                         'rek_id' : my_company.rek_id,
                                         'brand_name' : my_company.brand_name,
                                         'logo' : my_company.get_some_logo_url(),
                                         'kind_of_activity' : my_company.category_text,
                                         'employee_id' : my_company.owner_employee_id,
                                         'privacy' : ContractorPrivacy.VISIBLE_EVERYONE
                                     },
                                     'company_2_data' : {
                                         'rek_id' : company.rek_id,
                                         'brand_name' : company.brand_name,
                                         'logo' : company.get_some_logo_url(),
                                         'kind_of_activity' : company.category_text,
                                         'employee_id' : company.owner_employee_id,
                                         'privacy' : ContractorPrivacy.VISIBLE_EVERYONE
                                     }})
        new_contractor.save()
        return HttpResponse("{}", mimetype="application/x-javascript")

class PartnershipDeleteView(PartnershipBaseView):
    def handle_request(self, company, my_company):
        existing_contractor = Contractor.objects.get_one({'$or' : [{'company_1' : my_company._id,
                                                                    'company_2' : company._id},
                {'company_2' : my_company._id,
                 'company_1' : company._id}]})
        if not existing_contractor:
            return HttpResponse('{"error":true, "msg":"Not in contractors lists"}', mimetype="application/x-javascript")

        Contractor.objects.collection.remove({'_id' : existing_contractor._id})

        new_contractor_data_list = []
        for contractor_data in company.contractors:
            if contractor_data['company_id'] != my_company._id:
                new_contractor_data_list.append(contractor_data)
        Company.objects.collection.update({'_id' : company._id},
                                          {'$set' : {'contractors' : new_contractor_data_list}})

        new_contractor_data_list = []
        for contractor_data in my_company.contractors:
            if contractor_data['company_id'] != company._id:
                new_contractor_data_list.append(contractor_data)
        Company.objects.collection.update({'_id' : my_company._id},
                {'$set' : {'contractors' : new_contractor_data_list}})

        return HttpResponse("{}", mimetype="application/x-javascript")

def make_company_contractor(company):
    return {
        'company_id' : company._id,
        'rek_id' : company.rek_id,
        'logo' : company.get_logo_url(),
        'brand_name' : company.brand_name
    }

class PartnershipAcceptView(PartnershipBaseView):
    def handle_request(self, company, my_company):
        existing_contractor = Contractor.objects.get_one({'company_2' : my_company._id,
                                                          'company_1' : company._id,
                                                          'status' : ContractorStatusEnum.RECEIVED})
        if not existing_contractor:
            return HttpResponse('{"error":true, "msg":"Not in contractors lists"}', mimetype="application/x-javascript")

        Contractor.objects.collection.update({'_id' : existing_contractor._id},
                                             {'$set' : {'status' : ContractorStatusEnum.ACCEPTED}})
        Company.objects.collection.update({'_id' : my_company._id},
                                          {'$push' : {'contractors' : make_company_contractor(company)}})
        Company.objects.collection.update({'_id' : company._id},
                {'$push' : {'contractors' : make_company_contractor(my_company)}})
        return HttpResponse("{}", mimetype="application/x-javascript")

class PartnershipSettingsView(View):
    def post(self, request):
        target_company_rek_id = request.POST.get('rek_id', '').strip()
        try:
            target_company = Company.get_active_company_by_rek_id(target_company_rek_id)
            if not target_company:
                raise Exception
        except Exception:
            raise Http404()

        privacy = request.POST.get('privacy', '').strip()

        try:
            my_company = request.company
            contractor = Contractor.objects.get_one({'status' : ContractorStatusEnum.ACCEPTED,
                                                     '$or' : [{'company_1' : my_company._id,
                                                               'company_2' : target_company._id},
                                                              {'company_2' : my_company._id,
                                                               'company_1' : target_company._id}]})
            if not contractor:
                raise Exception
            if privacy not in ContractorPrivacy.ALL:
                raise Exception
        except Exception:
            raise Http404()

        if my_company._id == contractor.company_1:
            Contractor.objects.collection.update({'_id' : contractor._id},
                                                 {'$set' : {'company_2_data.privacy' : privacy}})
        else:
            Contractor.objects.collection.update({'_id' : contractor._id},
                                                 {'$set' : {'company_1_data.privacy' : privacy}})

        return HttpResponse("{}", mimetype="application/x-javascript")

class PartnershipRejectView(PartnershipBaseView):
    def handle_request(self, company, my_company):
        existing_contractor = Contractor.objects.get_one({'company_2' : my_company._id,
                                                          'company_1' : company._id,
                                                          'status' : ContractorStatusEnum.RECEIVED})
        if not existing_contractor:
            return HttpResponse('{"error":true, "msg":"Not in contractors lists"}', mimetype="application/x-javascript")

        Contractor.objects.collection.update({'_id' : existing_contractor._id},
                {'$set' : {'status' : ContractorStatusEnum.DECLINED}})
        return HttpResponse("{}", mimetype="application/x-javascript")

class PartnershipMarkViewedView(PartnershipBaseView):
    def handle_request(self, company, my_company):
        existing_contractor = Contractor.objects.get_one({'company_1' : company._id,
                                                          'company_2' : my_company._id,
                                                          'status' : ContractorStatusEnum.RECEIVED,
                                                          'viewed' : False})
        if not existing_contractor:
            return HttpResponse('{"error":true, "msg":"Not found"}', mimetype="application/x-javascript")

        Contractor.objects.collection.update({'_id' : existing_contractor._id},
                                             {'$set' : {'viewed' : True}})
        return HttpResponse("{}", mimetype="application/x-javascript")
