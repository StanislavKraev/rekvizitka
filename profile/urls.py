# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from rek.profile.views import EditProfileView, ChangePasswordView

urlpatterns = patterns('rek.profile.views',
    url(r'^profile/edit/$', login_required(EditProfileView.as_view()), name='edit_profile'),
    url(r'^profile/change_pwd/$', login_required(ChangePasswordView.as_view()), name='change_password'),
)
