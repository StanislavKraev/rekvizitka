# -*- coding: utf-8 -*-
from rek.billing.models import InvoiceStatusEnum, Account, Transaction, Currency
from rek.rekvizitka.models import Company

def set_paid(invoice, payment_order_number, payment_order_date, payment_order_comment):
    if not payment_order_number or not len(payment_order_number) or not payment_order_date or not payment_order_comment or not len(payment_order_comment):
        raise Exception('Insufficient data to process payment')

    if invoice.status != InvoiceStatusEnum.CREATED:
        raise Exception('Incorrect invoice status')

    company = Company.objects.get_one({'_id' : invoice.payer})
    if not company:
        raise Exception("Can't find payer company with id %s" % unicode(invoice.payer))

    company_account = Account.objects.get_one({'type' : Account.TYPE_COMPANY, 'details.subject_id' : company._id})
    if not company_account:
        raise Exception('Failed to find payer company account')
    bank_account = Account.objects.get_one({'system_id' : Account.FIXED_BANK_ACCOUNT_ID})
    if not bank_account:
        raise Exception('Failed to find bank system account')

    # todo: wrap with transaction
    tr = Transaction({'source' : bank_account._id,
                      'dest' : company_account._id,
                      'amount' : Currency.russian_roubles(invoice.price),
                      'comment' : u"%s Банковский перевод. Платежка N %s от %s." % (payment_order_comment,
                                                            unicode(payment_order_number),
                                                            payment_order_date.strftime('%d-%m-%Y'))})
    tr.save()
    tr.apply()
    invoice.status = InvoiceStatusEnum.PAID
    invoice.objects.update({'_id' : invoice._id}, {'$set' : {'status' : invoice.status}})
