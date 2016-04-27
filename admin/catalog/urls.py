# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.admin.catalog.views',
#    url(r'^$', is_superuser(), name='admin_'),
)
