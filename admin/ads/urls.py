# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.admin.ads.views import AdsView, AddPromoActionView, ShowPromoActionsView, ShowPromoActionView, ManagePromoActionView, ManagePromoCodeView
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.admin.ads.views',
    url(r'^$', is_superuser(AdsView.as_view()), name='admin_ads_root'),
    url(r'^add_promo_action/$', is_superuser(AddPromoActionView.as_view()), name='admin_add_promo_action'),
    url(r'^view_promo_actions/$', is_superuser(ShowPromoActionsView.as_view()), name='admin_show_promo_actions'),
    url(r'^view_promo_actions/(?P<action_id>[0-9a-zA-Z]+)/$', is_superuser(ShowPromoActionView.as_view()), name='admin_show_promo_action'),
    url(r'^view_promo_actions/(?P<action_id>[0-9a-zA-Z]+)/manage/$', is_superuser(ManagePromoActionView.as_view()), name='admin_manage_promo_action'),
    url(r'^promo_code/(?P<promo_id>[0-9a-zA-Z]+)/$', is_superuser(ManagePromoCodeView.as_view()), name='admin_manage_promo_code'),
)
