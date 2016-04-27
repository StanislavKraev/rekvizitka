# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.admin.finances.views import FinancesMainView, FinancesAccountsView, FinancesAccountView, InvoicePayView, GetInvoiceDataView, DepositTransferView
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.admin.finances.views',
    url(r'^$', is_superuser(FinancesMainView.as_view()), name='admin_finances'),
    url(r'^accounts/$', is_superuser(FinancesAccountsView.as_view()), name='admin_finances_accounts'),
    url(r'^accounts/(?P<account_id>[0-9a-zA-Z-]+)/$', is_superuser(FinancesAccountView.as_view()), name='admin_finances_account'),
    url(r'^invoice_pay/$', is_superuser(InvoicePayView.as_view()), name='admin_invoice_pay'),
    url(r'^invoice_pay/get_invoice_data/$', is_superuser(GetInvoiceDataView.as_view()), name='admin_get_invoice_data'),
    url(r'^deposit_transfer/$', is_superuser(DepositTransferView.as_view()), name='admin_deposit_transfer'),
)
