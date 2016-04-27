# -*- coding: utf-8 -*-
from decimal import *
from datetime import datetime
from bson.objectid import ObjectId
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import get_template, render_to_string
from django.utils import timezone, simplejson
from django.views.generic.base import View
import pytz
from rek.billing import invoice_manager
from rek.billing.models import Account, Transaction, Invoice, InvoiceStatusEnum, Currency
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.rekvizitka.models import Company, get_company_admin_user

class FinancesMainView(View):
    def get(self, request):
        data = {}
        return render_to_response('finances/finances_main.html', data, context_instance=RequestContext(request))

class FinancesAccountsView(View):
    def get(self, request):
        data = {}
        system_accounts = []
        account = Account.objects.get_one({'system_id' : ObjectId(Account.FIXED_PROMO_ACCOUNT_ID)})
        if account:
            system_accounts.append({
                'id' : account._id,
                'name' : account.name,
                'type' : account.type,
                'balance' : account.balance
            })
        account = Account.objects.get_one({'system_id' : ObjectId(Account.FIXED_ADS_ACCOUNT_ID)})
        if account:
            system_accounts.append({
                'id' : account._id,
                'name' : account.name,
                'type' : account.type,
                'balance' : account.balance
            })
        account = Account.objects.get_one({'system_id' : ObjectId(Account.FIXED_BANK_ACCOUNT_ID)})
        if account:
            system_accounts.append({
                'id' : account._id,
                'name' : account.name,
                'type' : account.type,
                'balance' : account.balance
            })

        data['system_accounts'] = system_accounts

        accounts_datas = []
        accounts = Account.objects.get({'type' : Account.TYPE_COMPANY})
        for account in accounts:
            company = Company.objects.get_one({'_id' : account.details['subject_id']})
            account_data = {
                'id' : account._id,
                'name' : account.name,
                'type' : account.type,
                'balance' : account.balance,
                'company_name' : company.brand_name if company else 'Неизвестно!'
            }
            accounts_datas.append(account_data)
        data['company_accounts'] = accounts_datas

        return render_to_response('finances/finances_accounts.html', data, context_instance=RequestContext(request))

class FinancesAccountView(View):
    def get_account_qualified_name(self, account):
        if account.type == Account.TYPE_COMPANY:
            company = Company.objects.get_one({'_id' : account.details['subject_id']})
            company_name = company.brand_name if company else u"<Не найдена>"
            return u"%s (компания %s)" % (account.name, company_name)
        return account.name

    def get(self, request, account_id):
        try:
            account = Account.objects.get_one({'_id' : ObjectId(account_id)})
            if not account:
                raise Exception()
        except Exception:
            raise Http404()

        data = {}

        human_types = {Account.TYPE_UNKNOWN : 'Не задано',
                       Account.TYPE_COMPANY : 'Счет компании',
                       Account.TYPE_EMPLOYEE : 'Счет сотрудника',
                       Account.TYPE_VIRTUAL : 'Виртуальный счет',
                       Account.TYPE_BANK : 'Банковский счет'}
        account_data = {
            'id' : account._id,
            'name' : account.name,
            'type' : account.type,
            'human_type' : human_types[account.type],
            'balance' : account.balance
        }

        if account.type == Account.TYPE_COMPANY:
            company = Company.objects.get_one({'_id' : account.details['subject_id']})
            if company:
                account_data['company_name'] = company.brand_name if company else 'Неизвестно!'
                account_data['company_url'] = "/search/companies/%s/" % company.rek_id

        transactions = []

        all_transactions = Transaction.objects.collection.find({'$or' : [
                                                                                {'source' : account._id},
                                                                                {'dest' : account._id}
                                                                        ]}).sort('finished', -1)
        human_states = {Transaction.STATE_INITIAL : ('initial', 'gray'),
                        Transaction.STATE_PENDING : ('pending', 'yellow'),
                        Transaction.STATE_COMMITTED : ('committed', 'orange'),
                        Transaction.STATE_DONE : ('done', 'green')}
        tz = pytz.timezone("Europe/Moscow")
        for tr in all_transactions:
            source_account = ""
            dest_account = ""
            transaction = Transaction(tr)
            value = transaction.amount.amount * transaction.amount.rate
            if account._id == transaction.source_account:
                value = -value

            finished = transaction.finished.astimezone(tz)
            started = transaction.started.astimezone(tz)

            if account._id == transaction.source_account:
                dest_account_obj = Account.objects.get_one({'_id' : transaction.dest_account})
                dest_account = self.get_account_qualified_name(dest_account_obj) if dest_account_obj else "Не найден!"
            else:
                source_account_obj = Account.objects.get_one({'_id' : transaction.source_account})
                source_account = self.get_account_qualified_name(source_account_obj) if source_account_obj else "Не найден!"

            transactions.append({'started' : started.strftime('%d.%m.%Y %H:%M'),
                                 'finished' : finished.strftime('%d.%m.%Y %H:%M'),
                                 'comment' : transaction.comment,
                                 'amount' : unicode(value),
                                 'state' : transaction.state,
                                 'human_state' : human_states[transaction.state],
                                 'source' : source_account,
                                 'dest' : dest_account})

        data['account'] = account_data
        data['transactions'] = transactions
        return render_to_response('finances/finances_account.html', data, context_instance=RequestContext(request))

class InvoicePayView(View):
    def get(self, request):
        data = {}
        return render_to_response('finances/invoice_pay.html', data, context_instance=RequestContext(request))

    def post(self, request):
        if 'pay' not in request.POST:
            return HttpResponseBadRequest('Do not know what to do')

        invoice_id = request.POST.get('invoice_id', '')
        if not len(invoice_id):
            return HttpResponseBadRequest('Incorrect invoice id')

        try:
            invoice_bid = ObjectId(invoice_id)
        except Exception:
            return HttpResponseBadRequest('Incorrect invoice id')

        invoice = Invoice.objects.get_one({'_id' : invoice_bid})
        if not invoice:
            return HttpResponseBadRequest('Incorrect invoice id')

        platezhka_nomer = request.POST.get('platezhka_nomer', '').strip()
        platezhka_date = request.POST.get('platezhka_date', '').strip()
        platezhka_comment = request.POST.get('platezhka_comment', '').strip()
        invoice_number = request.POST.get('invoice_number', '').strip()

        errors = {}

        if not len(platezhka_nomer):
            errors['platezhka_nomer'] = 'Поле не может быть пустым'

        pay_date = timezone.now()
        if not len(platezhka_date):
            errors['platezhka_date'] = 'Поле не может быть пустым'
        else:
            try:
                pay_date = datetime.strptime(platezhka_date, '%d-%m-%Y')
                if not pay_date:
                    raise ValueError()
            except ValueError:
                errors['platezhka_date'] = 'Некорректная дата платежа'

        if not len(platezhka_comment):
            errors['platezhka_comment'] = 'Поле не может быть пустым'

        if not len(errors):
            try:
                invoice_manager.set_paid(invoice, platezhka_nomer, pay_date, platezhka_comment)
                return HttpResponseRedirect('/finances/')
            except Exception, ex:
                errors['general'] = 'Failed to complete operation (%s)' % ex.message

        data = {'errors' : errors,
                'platezhka_nomer' : platezhka_nomer,
                'platezhka_date' : platezhka_date,
                'platezhka_comment' : platezhka_comment,
                'invoice_number' : invoice_number}
        return render_to_response('finances/invoice_pay.html', data, context_instance=RequestContext(request))

class GetInvoiceDataView(View):
    def get(self, request):
        invoice_id = request.GET.get('invoiceId')
        if not invoice_id or not len(invoice_id):
            raise Http404()

        invoice = Invoice.objects.get_one({'number' : invoice_id, 'status' : InvoiceStatusEnum.CREATED})
        if not invoice:
            raise Http404()

        company = Company.objects.get_one({'_id' : invoice.payer})
        data_dict = {
                     'Платильщик' : (u'компания <a href="/search/companies/%s/">%s</a>' % (company.rek_id, company.brand_name)) if company else '<не найдена!>',
                     'Номер' : invoice.number,
                     'Получатель' : invoice.recipient,
                     'Адрес получателя' : invoice.address,
                     'Счет получателя' : invoice.account,
                     'Комментарий' : invoice.comment,
                     'Создан' : unicode(invoice.create_date),
                     'Истекает' : unicode(invoice.expire_date),
                     'Услуга' : invoice.position,
                     'Сумма' : unicode(invoice.price) + u' руб.'}

        data = {'success' : True, 'data' : data_dict, 'invoiceId' : unicode(invoice._id)}
        return HttpResponse(simplejson.dumps(data), mimetype="application/javascript")

class DepositTransferView(View):
    def send_deposit_transaction_msg(self, email, transaction_id, amount):
        action = create_action_id(actions.DEPOSIT_TRANSACTION, transaction_id)

        data = {'amount' : unicode(amount), 'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}
        plain_text = render_to_string('mails/popolnenie_deposita.txt', data)
        html = render_to_string('mails/popolnenie_deposita.html', data)

        notification_manager.add(action, email, 'Начисление средств на депозит', plain_text, html, 1)

    def get(self, request):
        data = {'errors' : {}}
        return render_to_response('finances/deposit_transfer.html', data, context_instance=RequestContext(request))

    def post(self, request):
        errors = {}
        amount_data_dec = None
        data = {'errors' : errors}

        company_rek_id = request.POST.get('company_rek_id', '').strip()
        amount = request.POST.get('amount', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not len(amount):
            errors['amount'] = 'Введите корректную сумму'
        else:
            try:
                amount_data_dec = Decimal(amount)
                amount_data = Currency.russian_roubles(amount_data_dec)
            except Exception:
                errors['amount'] = 'Введите корректную сумму'

        if not len(comment):
            errors['comment'] = 'Поле не может быть пустым'

        company = None
        if not len(company_rek_id):
            errors['company_rek_id'] = 'Введите корректный rek-номер компании'
        else:
            company = Company.objects.get_one({'rek_id' : company_rek_id})
            if not company:
                errors['company_rek_id'] = u'Не удалось найти компанию'

        if not len(errors) and company:
            #noinspection PyUnboundLocalVariable
            company_account = Account.objects.get_one({'type' : Account.TYPE_COMPANY,
                                                       'details.subject_id' : company._id})
            if not company_account:
                errors['general'] = 'Не найден счет компании'
            else:
                promo_account = Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID})
                admin_user = get_company_admin_user(company)
                if not admin_user:
                    errors['general'] = 'Не найден пользователь компании для отправки письма!'
                else:
                    if not promo_account:
                        errors['general'] = 'Не найден системный банковский счет'
                    else:
                        #noinspection PyUnboundLocalVariable
                        transaction = Transaction({'source' : promo_account._id,
                                                   'dest' : company_account._id,
                                                   'amount' : amount_data,
                                                   'comment' : comment})
                        transaction.save()
                        transaction.apply()

                        self.send_deposit_transaction_msg(admin_user.email, transaction._id, amount_data_dec)
                        return HttpResponseRedirect('/finances/')

        data['company_rek_id'] = company_rek_id
        data['amount'] = amount
        data['comment'] = comment
        return render_to_response('finances/deposit_transfer.html', data, context_instance=RequestContext(request))
