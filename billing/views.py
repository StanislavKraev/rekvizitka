# -*- coding: utf-8 -*-
import cStringIO as StringIO
import bson

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import render_to_response
from django.template.context import Context, RequestContext
from django.template.loader import get_template
from django.utils import simplejson, timezone
from django.utils.safestring import mark_safe
from django.views.generic.base import View

from ho import pisa
from rek.billing.models import Invoice, InvoiceStatusEnum, Account, Transaction
from rek.billing.bill_context import bill_default_context_pdf, bill_default_context_html
from rek.rekvizitka.templatetags import portal
from rek.rekvizitka.utils import summ_words
from rek.system_data.rek_settings import SettingsManager

class AddVerifyBill(View):
    def post(self, request):
        if not hasattr(request, 'company') or not hasattr(request, 'employee'):
            raise Http404()

        bills_count = Invoice.objects.count({'expire_date' : {'$gte' : timezone.now()},
                                             'payer' : request.company._id,
                                             'status' : InvoiceStatusEnum.CREATED})
        if bills_count:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Такой счет уже существует."}),
                                                  mimetype='application/javascript')

        rekvizitka_bank_account = SettingsManager.get_property('rekvizitka_bank_account')
        bill_data = {
            'payer' : request.company._id,
            'number' : u'КЦ-%d' % SettingsManager.inc_and_return_property('bill_auto_index'),
            'position' : u'Верификация в информационной системе',
            'status' : InvoiceStatusEnum.CREATED,
            'duration_days':30,
            'price' : SettingsManager.get_property('verify_bill_price')
        }
        bill_data.update(rekvizitka_bank_account)
        new_bill = Invoice(bill_data)
        new_bill.save()

        employee = request.employee
        employee_tz = employee.get_tz()
        issued = new_bill.create_date.astimezone(employee_tz)

        return HttpResponse(simplejson.dumps({'error' : False,
                                              'bill' : {'id' : unicode(new_bill._id),
                                                        'service_title' : bill_data['position'],
                                                        'price' : bill_data['price'],
                                                        'status' : bill_data['status'],
                                                        'issued' : issued.strftime('%d.%m.%Y %H:%M'),
                                                        'number' : new_bill.number}}),
                            mimetype='application/javascript')

class SendBill(View):
    def post(self, request):
        try:
            bill_id_str = request.POST['bill_id']
        except KeyError:
            return HttpResponseBadRequest()
        company = request.company

        try:
            bill_id = bson.ObjectId(bill_id_str)
        except Exception:
            return HttpResponseBadRequest()
        bill = Invoice.objects.get_one({'_id' : bill_id, 'payer' : company._id})

        if bill:
            if timezone.now() > bill.expire_date and bill.status != InvoiceStatusEnum.EXPIRED:
                bill.status = InvoiceStatusEnum.EXPIRED
                bill.objects.update({'_id' : bill._id}, {'$set' : {'status' : InvoiceStatusEnum.EXPIRED}})
            if bill.status == InvoiceStatusEnum.EXPIRED:
                bill = None

        if not bill:
            return HttpResponse(simplejson.dumps({'error' : True,
                                                  'error_message' : "Такой счет не найден."}),
                                                  mimetype='application/javascript')

        plain_text_template = get_template('mails/send_bill.txt')
        html_template = get_template('mails/send_bill.html')

        plain_text = plain_text_template.render(Context({}))
        html = html_template.render(Context({}))
        email = request.user.email
        subject, from_email, to,  bcc = 'Счет верификации на Rekvizitka.Ru', settings.EMAIL_HOST_USER, [email,], []
        msg = EmailMultiAlternatives(subject, plain_text, from_email, to, bcc)
        msg.attach_alternative(html, "text/html")

        context=bill_default_context_pdf

        context['recipient']['name']= bill.recipient
        context['recipient']['address']=bill.address
        context['recipient']['rekvizitka_link']='http://%s/2A82' % settings.SITE_DOMAIN_NAME
        context['recipient']['account']=bill.account
        context['recipient']['account_name']=bill.account_name
        context['recipient']['bank']['name']=bill.bank_name
        context['recipient']['bank']['bik']=bill.bank_bik
        context['recipient']['bank']['account']=bill.bank_account
        context['bill']['number'] = bill.number
        context['bill']['date'] = bill.create_date.strftime("%d.%m.%Y")
        context['bill']['position']=bill.position
        context['bill']['sum']['in_digits']=bill.price
        context['bill']['sum']['in_words']=summ_words(str(bill.price)+".00")
        context['bill']['duration']=get_duration_text(bill.duration_days)
        context['payer']['name'] = ''

        bill_pdf = generate_pdf('static/bill.html', context)
        if bill_pdf:
            msg.attach(u'verification_bill.pdf', bill_pdf, 'application/pdf')

        msg.send()

        return HttpResponse(simplejson.dumps({'error' : False}),
                            mimetype='application/javascript')

def get_duration_text(duration_days):
    result=''
    if duration_days > 100:
       duration_days_temp = int(str(duration_days)[-2:])
    else:
       duration_days_temp = duration_days

    if duration_days_temp <= 20: #1,2,3
        k = duration_days_temp
    else: # >20 => 1,2,3
        k = int(str(duration_days_temp)[-1:])

    if k==1:
        result = "календарного дня"
    if 1 < k < 5:
        result = "календарных дней"
    if 5 <= k <= 20 or k==0:
        result = "календарных дней"

    return '%d %s' % (duration_days, result)

def generate_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result)
    if not pdf.err:
        res = result.getvalue()
        result.close()
        return res
    return None

def write_pdf(template_src, context_dict):
    result = generate_pdf(template_src, context_dict)
    if result:
        return HttpResponse(result, mimetype='application/pdf')
    return HttpResponseServerError("Couldn't generate pdf")

def make_bill(request, bill_id, context=None):
    company = request.company
    bill = Invoice.objects.get_one({'_id' : bson.ObjectId(bill_id), 'payer' : company._id})

    if bill:
        if timezone.now() > bill.expire_date and bill.status != InvoiceStatusEnum.EXPIRED:
            bill.status = InvoiceStatusEnum.EXPIRED
            bill.objects.update({'_id' : bill._id}, {'$set' : {'status' : InvoiceStatusEnum.EXPIRED}})
        if bill.status == InvoiceStatusEnum.EXPIRED:
            bill = None

    if not bill:
        return None

    context.update({
        'recipient' : {
            'name' : bill.recipient,
            'address' : bill.address,
            'rekvizitka_link' : 'http://%s/2A82' % settings.SITE_DOMAIN_NAME,
            'account' : bill.account,
            'account_name' : bill.account_name,
            'bank' : {
                'name' : bill.bank_name,
                'bik' : bill.bank_bik,
                'account' : bill.bank_account
            }
        },
        'bill' : {
            'number' : bill.number,
            'date' : bill.create_date.strftime("%d.%m.%Y"),
            'position' : bill.position,
            'sum' : {
                'in_digits' : bill.price,
                'in_words' : summ_words(str(bill.price)+".00")
            },
            'duration' : get_duration_text(bill.duration_days)
        },
        'payer' : {'name' : ''
        }
    })

    return context

def bill_pdf(request, bill_id):
    context = make_bill(request, bill_id, bill_default_context_pdf)
    if not context:
        raise Http404()
    return write_pdf('bill.html', context)

def bill_html(request, bill_id):
    context = make_bill(request, bill_id, bill_default_context_html)
    if not context:
        raise Http404()
    context['print'] = True
    return render_to_response('bill.html', context, context_instance=RequestContext(request))

class DepositInitialsView(View):
    @classmethod
    def generate_data_obj(cls, company, employee):
        account = Account.objects.get_one({'details.subject_id' : company._id, 'type' : Account.TYPE_COMPANY})
        if not account:
            return {}
        all_transactions = Transaction.objects.collection.find({'$and' :
                                                                        [{'state' : Transaction.STATE_DONE},
                                                                         {'$or' : [
                                                                                    {'source' : account._id},
                                                                                    {'dest' : account._id}
                                                                                  ]}
                                                                        ]}).sort('finished', 1)
        balance = 0
        history = []
        employee_tz = employee.get_tz()
        for tr in all_transactions:
            transaction = Transaction(tr)
            value = transaction.amount.amount * transaction.amount.rate
            if account._id == transaction.source_account:
                value = -value
            balance += value
            finished = transaction.finished.astimezone(employee_tz)
            history.append([finished.strftime('%d.%m.%Y %H:%M'), unicode(value), unicode(balance), transaction.comment])
        history.reverse()
        data = {
            "categoryText" : company.category_text,
            "history" : history,
            "sortby" : ['date', 'acc'],
            "account_balance" : unicode(account.balance.amount)
        }
        return data

    def get(self, request):
        if not hasattr(request, 'company'):
            raise Http404()
        data = self.generate_data_obj(request.company, request.employee)
        data.update(portal.get_common_data_for_company(request, request.company))
        response_content = mark_safe(simplejson.dumps(data))

        return HttpResponse(response_content, mimetype="application/x-javascript")

class DepositView(View):
    template = 'apps/deposit/template.html'
    def get(self, request):
        if not hasattr(request, 'company'):
            raise Http404()

        data = DepositInitialsView.generate_data_obj(request.company, request.employee)
        data.update(portal.get_common_data_for_company(request, request.company))
        response_content = mark_safe(simplejson.dumps(data))

        return render_to_response(self.template, {
                'deposit_module_init' : response_content,
            }, context_instance = RequestContext(request))

class DepositDepositView(DepositView):
    template = 'apps/deposit/deposit/templates/template.html'

class DepositToppingUpView(DepositView):
    template = 'apps/deposit/topping_up/templates/template.html'

class DepositPaymentsView(DepositView):
    template = 'apps/deposit/payments/templates/template.html'

