# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.admin.search.company_views import SearchCompanyView, MakeCompanyView, ShowCompanyView, ManageCompanyView, VerifyCompanyInvoiceView
from rek.admin.search.views import SearchMainView
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.admin.search.views',
    url(r'^$', is_superuser(SearchMainView.as_view()), name='admin_search_main'),

    url(r'^companies/$', is_superuser(SearchCompanyView.as_view()), name='admin_search_companies'),
    url(r'^companies/new/$', is_superuser(MakeCompanyView.as_view()), name='admin_make_company'),
    url(r'^companies/(?P<code>[a-zA-Z0-9]+)/$', is_superuser(ShowCompanyView.as_view()), name='admin_show_company'),
    url(r'^companies/(?P<code>[a-zA-Z0-9]+)/manage/$', is_superuser(ManageCompanyView.as_view()), name='admin_manage_company'),
    url(r'^companies/(?P<code>[a-zA-Z0-9]+)/verify_invoice/$', is_superuser(VerifyCompanyInvoiceView.as_view()), name='admin_verify_company_invoice'),

    #    url(r'^employees/$', is_superuser(SearchEmployeeView.as_view()), name='admin_search_employees'),
#    url(r'^employees/new/$', is_superuser(MakeEmployeeView.as_view()), name='admin_make_employee'),
#    url(r'^employees/(?P<code>[a-zA-Z0-9]+)/$', is_superuser(ShowEmployeeView.as_view()), name='admin_show_employee'),
#    url(r'^employees/(?P<code>[a-zA-Z0-9]+)/manage/$', is_superuser(ManageEmployeeView.as_view()), name='admin_manage_employee'),
)
