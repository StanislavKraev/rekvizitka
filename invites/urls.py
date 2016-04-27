# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from rek.invites.views import VerifyRecommendView, OurProposersRecommendView, WeRecommendRecommendView, InvitesRecommendView, RecommendInitialsView, AskForRecommendationView, AcceptRecommendationView, DeclineRecommendationView, SendInviteView, JoinByInviteView, GiveRecommendationView, TakeAwayRecommendationView
from rek.rekvizitka.decorators import registration_completed_required
from rek.rekvizitka.views import VerifyCollectionView

urlpatterns = patterns('',
    url(r'^verification/$', login_required(VerifyRecommendView.as_view()), name='verify_view'),
    url(r'^(?P<code>[0-9a-zA-Z]+)/our_proposers/$', OurProposersRecommendView.as_view(), name='our_proposers_view'),
    url(r'^(?P<code>[0-9a-zA-Z]+)/we_recommend/$', WeRecommendRecommendView.as_view(), name='we_recommend_view'),
    url(r'^invites/$', registration_completed_required(InvitesRecommendView.as_view()), name='invites_view'),
    url(r'^recommendations/data/(?P<code>[0-9a-zA-Z]+)/$', RecommendInitialsView.as_view(), name='recommend_data'),
    url(r'^recommendations/ask/(?P<code>[0-9a-zA-Z]+)/$', login_required(AskForRecommendationView.as_view()), name='ask_recommendation'),
    url(r'^recommendations/accept/(?P<recommendation_id>[0-9a-zA-Z]+)/$', registration_completed_required(AcceptRecommendationView.as_view()), name='accept_recommendation'),
    url(r'^recommendations/give/(?P<code>[0-9a-zA-Z]+)/$', registration_completed_required(GiveRecommendationView.as_view()), name='givi_recommendation'),
    url(r'^recommendations/take-away/(?P<code>[0-9a-zA-Z]+)/$', registration_completed_required(TakeAwayRecommendationView.as_view()), name='otobrat_recommendation'),
    url(r'^recommendations/decline/(?P<recommendation_id>[0-9a-zA-Z]+)/$', registration_completed_required(DeclineRecommendationView.as_view()), name='decline_recommendation'),
    url(r'^verify/c/(?P<page>[1234567890]+)$', login_required(VerifyCollectionView.as_view()), name="verify_collection_view"),
    url(r'^invites/send/$', registration_completed_required(SendInviteView.as_view()), name='send_invite'),
    url(r'^invites/join/(?P<cookie_code>[0-9a-zA-Z]+)/$', JoinByInviteView.as_view(), name='join_by_invite'),
)
