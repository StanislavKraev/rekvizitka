# -*- coding: utf-8 -*-
import sys
from bson.objectid import ObjectId
from django.template.loader import render_to_string
from django.utils import timezone

from rek.billing.models import Transaction, Invoice, InvoiceStatusEnum
from rek.cron.cron_task import CronTaskBase
from rek.deferred_notification import actions
from rek.deferred_notification.actions import create_action_id
from rek.deferred_notification.manager import notification_manager
from rek.rekvizitka.models import Company, get_company_admin_user

class RepairTransactionsTask(CronTaskBase):
    def execute(self):
        print >> sys.stdout, 'Executing RepairTransactionsTask'
        bad_transactions = Transaction.objects.get({'state' : {'$nin' : [Transaction.STATE_INITIAL, Transaction.STATE_DONE]}})
        for transaction in bad_transactions:
            transaction.complete()

class RotInvoicesTask(CronTaskBase):
    def send_rotten_invoice_notification(self, email, invoice_number, invoice_name, amount, date):
        action = create_action_id(actions.INVOICE_ROTTEN, invoice_number)

        data = {'name' : invoice_name,
                'number' : unicode(invoice_number),
                'amount' : unicode(amount),
                'date' : date.strftime('%d-%m-%Y')}

        plain_text = render_to_string('mails/invoice_rotten.txt', dictionary=data)
        html = render_to_string('mails/invoice_rotten.html', dictionary=data)

        notification_manager.add(action, email, u'Окончание срока действия счета', plain_text, html, 1)

    def execute(self):
        print >> sys.stdout, 'Executing RotInvoicesTask'
        invoices = Invoice.objects.collection.find({'status' : {'$ne' : InvoiceStatusEnum.EXPIRED},
                                                    'expire_date' : {'$lte' : timezone.now()}})
        for invoice in invoices:
            try:
                company_id = ObjectId(invoice['payer'])
            except Exception:
                continue
            company = Company.objects.get_one({'_id' : company_id})
            if not company:
                continue
            admin_user = get_company_admin_user(company)
            if admin_user:
                self.send_rotten_invoice_notification(admin_user.email,
                                                      invoice['number'],
                                                      invoice['position'],
                                                      invoice['price'],
                                                      invoice['create_date'])

        Invoice.objects.update({'status' : {'$ne' : InvoiceStatusEnum.EXPIRED},
                                'expire_date' : {'$lte' : timezone.now()}},
                               {'$set' : {'status' : InvoiceStatusEnum.EXPIRED}}, multi=True)
