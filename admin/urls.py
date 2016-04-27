# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from rek.admin.auth_views import LoginAdminView, LogoutAdminView
from rek.admin.views import AdminMainView
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.profile.views',
    url(r'^$', is_superuser(AdminMainView.as_view()), name='admin_main_view'),
    url(r'^login/$', LoginAdminView.as_view(), name='admin_login_view'),
    url(r'^logout/$', is_superuser(LogoutAdminView.as_view()), name='admin_logout_view'),
    (r'^ads/',include('rek.admin.ads.urls')),
    (r'^catalog/',include('rek.admin.catalog.urls')),
    (r'^finances/',include('rek.admin.finances.urls')),
    (r'^search/',include('rek.admin.search.urls')),
    (r'^settings/',include('rek.admin.settings.urls')),
    (r'^statistics/',include('rek.admin.statistics.urls')),
)
