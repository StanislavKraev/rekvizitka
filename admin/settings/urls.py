# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.admin.settings.views import ManageSettings
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.admin.settings.views',
    url(r'^$', is_superuser(ManageSettings.as_view()), name='admin_manage_settings'),
)
