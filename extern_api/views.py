from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.base import View
from rek.rekvizitka import utils
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import Company, CompanyAddress, AddressTypeEnum, Account

class ExportRekDataView(View):
    def get(self, request, code):
        try:
            company = Company.objects.get(id=utils.code_to_integer(code))
            if not company.is_active():
                raise ValueError()
        except (Company.DoesNotExist, ValueError):
            return render_to_response(
                'export/show_company.xml',
                {
                    'error': 'company not found',
                    'rek_code': code
                },
                context_instance=RequestContext(request),
                mimetype='text/xml'
            )

        try:
            company_legal_address = CompanyAddress.objects.filter(company = company, address_type_val = AddressTypeEnum.LEGAL)[:1][0]
        except Exception:
            raise Http404()

        try:
            phone = company_legal_address.addressphone_set.all()[:1][0]
        except Exception:
            phone = None

        try:
            email = company_legal_address.addressemail_set.all()[:1][0]
        except Exception:
            email = None

        try:
            website = company_legal_address.companywebsite_set.all()[:1][0]
        except Exception:
            website = None

        try:
            account = Account.objects.filter(company=company)[:1][0]
        except Exception:
            account = None

        return render_to_response(
            'export/show_company.xml',
            {
                'company': company,
                'address': company_legal_address,
                'rek_code': code,
                'account': account,
                'email' : email,
                'phone' : phone,
                'website' : website
                },
            context_instance=RequestContext(request),
            mimetype='text/xml'
        )
