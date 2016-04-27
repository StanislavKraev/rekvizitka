# -*- coding: utf-8 -*-
import time
from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson, timezone
from django.utils.safestring import mark_safe
from django.views.generic.base import View

from rek.rekvizitka.models import Company, CompanyCategoryEnum
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.templatetags import portal

MAX_PAGE_COUNT = 10

class TinySearchInitialsView(View):
    @classmethod
    def generate_data(cls, query="", page=1):
        page -= 1
        if page < 0 or page > 12344:
            page = 0

        data = {'query' : query,
                'page' : page,
                'results' : []}

        total = 0
        if query and len(query):
            no_company_id = False
            criteria_main = {'rek_id' : query.upper(),
                             'is_account_activated' : {'$ne' : False},
                             'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}}
            query_result = Company.objects.collection.find(criteria_main)

            if query_result.count() != 1:
                no_company_id = True
            else:
                found_company = Company(query_result[0])
                if not found_company.is_active():
                    no_company_id = True
                else:
                    total = 1

            criteria_main = {'$or' : []}
            if no_company_id:
                try:
                    term_as_integer = int(query)
                except ValueError:
                    term_as_integer = 0

                if term_as_integer:
                    criteria_main['$or'] = [{'inn' : term_as_integer}, {'kpp' : term_as_integer}]

                search_dict = {'$regex' : '.*%s.*' % query, '$options' : 'i'}
                criteria_main['$or'].extend([
                        {'brand_name' : search_dict},
                        {'short_name' : search_dict},
                        {'full_name' : search_dict},
                        {'category_text' : search_dict},
                        {'description' : search_dict}])
                criteria_main = {'$and' : [criteria_main,
                                           {'is_account_activated' : {'$ne' : False},
                                            'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}}]}

                query_result = Company.objects.collection.find(criteria_main).sort('date_creation', -1).skip(page * MAX_PAGE_COUNT).limit(MAX_PAGE_COUNT)
                total = Company.objects.count(criteria_main)
        else:
            query_result = Company.objects.collection.find({
                'is_account_activated' : {'$ne' : False},
                'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}
            }).sort('date_creation', -1).skip(page * MAX_PAGE_COUNT).limit(MAX_PAGE_COUNT)
            total = Company.objects.count({'is_account_activated' : {'$ne' : False},
                                           'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES}})

        for company_obj in query_result:
            found_company = Company(company_obj)
            data['results'].append({'bname' : found_company.brand_name,
                                    'logo' : found_company.get_list_logo_url(),
                                    'company_url' : reverse("showCompany", kwargs={'code' : found_company.rek_id}),
                                    'kind_of_activity' : found_company.category_text})
        data['pagination'] = {'page' : page + 1,
                              'count' : total / MAX_PAGE_COUNT + (1 if total % MAX_PAGE_COUNT else 0)}

        result_json = simplejson.dumps(data)
        return mark_safe(result_json)

    def get(self, request):
        query = request.GET.get('q', "")
        page_str = request.GET.get('p', "1")
        try:
            page = int(page_str)
        except ValueError:
            page = 1

        return HttpResponse(self.generate_data(query=query, page=page), mimetype="application/x-javascript")

class TinySearch(View):
    def get(self, request):
        query = request.GET.get('q', "")
        page_str = request.GET.get('p', "1")
        try:
            page = int(page_str)
        except ValueError:
            page = 1

        template_name = "apps/search/templates/search.html"

        return render_to_response(template_name,
                                  {'search_initials' : TinySearchInitialsView.generate_data(query=query, page=page),
                                   'sidebar_mode' : 'search',
                                   'sidebar_initial_data' : {'show_mode' : 'companies'}
                                  },
                                  context_instance=RequestContext(request))

class InfiniteSearchInitialsView(View):
    @classmethod
    def generate_data_obj(cls, query="", start_ts=0, categories = None):
        categories = categories or []

        if start_ts < 1293829200: # 2011.1.1
            start_ts = 2000000000

        data = {'query' : query,
                'results' : []}

        try:
            start_date = datetime.fromtimestamp(start_ts, timezone.get_current_timezone())
            if not start_date:
                raise Exception()
        except Exception:
            start_date = datetime(2033, 2, 1)

        if query and len(query):
            criteria_main = {'$or' : []}

            try:
                term_as_integer = int(query)
            except ValueError:
                term_as_integer = 0

            if term_as_integer:
                criteria_main['$or'] = [{'inn' : term_as_integer}, {'kpp' : term_as_integer}]
            else:
                criteria_main['$or'] = [{'rek_id' : query.upper()}]

            search_dict = {'$regex' : '.*%s.*' % query, '$options' : 'i'}
            criteria_main['$or'].extend([
                    {'brand_name' : search_dict},
                    {'full_name' : search_dict},
                    {'category_text' : search_dict},
                    {'description' : search_dict}])
            criteria_main = {'$and' : [criteria_main,
                    {'is_account_activated' : {'$ne' : False},
                     'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES},
                     'date_creation' : {'$lt' : start_date}}]}
            if len(categories):
                if len(categories) == 1:
                    criteria_main['$and'].append({'categories' : categories[0]})
                else:
                    criteria_main['$and'].append({'categories' : {'$all' : categories}})

            query_result = Company.objects.collection.find(criteria_main).sort('date_creation', -1).limit(MAX_PAGE_COUNT)
        else:
            criteria_main = {
                'is_account_activated' : {'$ne' : False},
                'account_status' : {'$in' : CompanyAccountStatus.ACTIVE_ACCOUNT_STATUSES},
                'date_creation' : {'$lt' : start_date}
            }
            if len(categories):
                if len(categories) == 1:
                    criteria_main['categories'] = categories[0]
                else:
                    criteria_main['categories'] = {'$all' : categories}

            query_result = Company.objects.collection.find(criteria_main).sort('date_creation', -1).limit(MAX_PAGE_COUNT)

        total_count = query_result.count()
        limited_count = query_result.count(True)
        data['has_more'] = total_count > limited_count

        last_date = None
        for company_obj in query_result:
            found_company = Company(company_obj)
            data['results'].append({'bname' : found_company.brand_name,
                                    'logo' : found_company.get_list_logo_url(),
                                    'company_url' : reverse("showCompany", kwargs={'code' : found_company.rek_id}),
                                    'kind_of_activity' : found_company.category_text})
            last_date = found_company.date_creation
        if last_date:
            data['last_ts'] = int(time.mktime(last_date.timetuple()))

        return data

    def get(self, request):
        query = request.GET.get('q', "")
        start_ts = request.GET.get('start_ts', "2000000000")
        try:
            start_ts = int(start_ts)
        except ValueError:
            start_ts = 1

        categories = []
        for cat in CompanyCategoryEnum.ALL:
            if cat in request.GET:
                categories.append(cat)

        data = self.generate_data_obj(query=query, start_ts=start_ts, categories=categories)
        data.update(portal.get_common_data_for_search(request, {'show_mode' : 'companies'}))
        response_content = mark_safe(simplejson.dumps(data))
        return HttpResponse(response_content, mimetype="application/x-javascript")

class InfiniteSearch(View):
    def get(self, request):
        query = request.GET.get('q', "")
        start_ts = request.GET.get('start_ts', "2000000000")
        try:
            start_ts = int(start_ts)
        except ValueError:
            start_ts = 2000000000
        categories = []
        for cat in CompanyCategoryEnum.ALL:
            if cat in request.GET:
                categories.append(cat)

        template_name = "apps/search/templates/search.html"

        data = InfiniteSearchInitialsView.generate_data_obj(query=query, start_ts=start_ts, categories=categories)
        data.update(portal.get_common_data_for_search(request, {'show_mode' : 'companies'}))
        response_content = mark_safe(simplejson.dumps(data))
        return render_to_response(template_name,
                {'search_initials' : response_content,
                 'sidebar_mode' : 'search',
                 'sidebar_initial_data' : {'show_mode' : 'companies'}
            },
            context_instance=RequestContext(request))
