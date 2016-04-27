from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from rek.billing.views import DepositToppingUpView, DepositPaymentsView, DepositInitialsView, DepositDepositView
from rek.billing.views import AddVerifyBill, SendBill,bill_html, bill_pdf

urlpatterns = patterns('rek.billing.views',
    url(r'^verification/place_bill/$', login_required(AddVerifyBill.as_view()), name='add_verify_bill'),
    url(r'^send_verify_bill/$', login_required(SendBill.as_view()), name='send_bill'),
    url(r'^get/(?P<bill_id>[0-9a-zA-Z-]+)/bill.html$', login_required(bill_html), name='get_html_bill'),
    url(r'^get/(?P<bill_id>[0-9a-zA-Z-]+)/bill.pdf$', login_required(bill_pdf), name='get_pdf_bill'),
    url(r'^deposit/$', login_required(DepositDepositView.as_view()), name='deposit_view'),
    url(r'^deposit/topping-up/$', login_required(DepositToppingUpView.as_view()), name='deposit_topping_up'),
    url(r'^deposit/payments/$', login_required(DepositPaymentsView.as_view()), name='deposit_payments'),
    url(r'^deposit/s/$', login_required(DepositInitialsView.as_view()), name='deposit_payments'),
)
