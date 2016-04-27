# -*- coding: utf-8 -*-

from django.conf.urls import *
from django.views.generic.base import TemplateView

from rek import settings
from rek.combo_loader.views import ComboLoaderView

urlpatterns = patterns('',
    url(
        r'^combo/$',        ComboLoaderView.as_view(), name='combo_loader'),
        (r'^chat/',         include('rek.chat.urls')),
        (r'^',              include('rek.rekvizitka.urls')),
        (r'^',              include('rek.profile.urls')),
        (r'^',              include('rek.contractors.urls')),
        (r'^search/',       include('rek.search.urls')),
        (r'^',              include('rek.invites.urls')),
        (r'^',              include('rek.billing.urls')),
        (r'^promotions/',   include('rek.promotions.urls')),
        (r'^feedback/',     include('rek.feedback.urls')),
)
