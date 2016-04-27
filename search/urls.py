# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.search.views import  InfiniteSearch, InfiniteSearchInitialsView

urlpatterns = patterns('rek.search.views',
    url(r'^$', InfiniteSearch.as_view(), name='TinySearch'),
    url(r'^i/$', InfiniteSearchInitialsView.as_view(), name='TinySearchParams')
)
