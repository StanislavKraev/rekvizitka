# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from rek.rekvizitka.decorators import registration_completed_required
from rek.contractors.views import (ContractorsView,
                                   IncomingContractorsView,
                                   OutgoingContractorsView,
                                   ContractorsInitialsView,
                                   PartnershipRequestView,
                                   PartnershipDeleteView,
                                   PartnershipAcceptView,
                                   PartnershipSettingsView,
                                   PartnershipRejectView,
                                   PartnershipMarkViewedView)

urlpatterns = patterns('rek.contractors.views',
    url(r'^(?P<rek_id>[a-zA-Z0-9]+)/contractors/$', ContractorsView.as_view(), name="contractors_main"),
    url(r'^contractors/incoming/$', login_required(IncomingContractorsView.as_view()), name="in_contractors_main"),
    url(r'^contractors/outgoing/$', login_required(OutgoingContractorsView.as_view()), name="out_contractors_main"),
    url(r'^(?P<rek_id>[a-zA-Z0-9]+)/contractors/i/$', ContractorsInitialsView.as_view(), name="contractors_initials"),
    url(r'^contractors/add/$', registration_completed_required(PartnershipRequestView.as_view()), name="new_partners"),
    url(r'^contractors/delete/$', registration_completed_required(PartnershipDeleteView.as_view()), name="delete_partner"),
    url(r'^contractors/accept/$', registration_completed_required(PartnershipAcceptView.as_view()), name="accept_partner"),
    url(r'^contractors/reject/$', registration_completed_required(PartnershipRejectView.as_view()), name="reject_partner"),
    url(r'^contractors/settings/$', registration_completed_required(PartnershipSettingsView.as_view()), name="save_partner_settings"),
    url(r'^contractors/mark_viewed/$', login_required(PartnershipMarkViewedView.as_view()), name="mark_partner_viewed"),
)
