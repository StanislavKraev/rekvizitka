# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

from rek.rekvizitka.views import ShowCompanySettings, ProfileSettingsInitialsView, ShowCompanyRekContacts, ShowCompanyRekAbout, IndexView, ProfileModuleInitialsView, AccountActivationView, TimeZonesListView, SaveSettingsView, PasswordRecovery, NewPasswordView

urlpatterns = patterns('rek.rekvizitka.views',
    url(r'^$', IndexView.as_view(), name='index_view'),
    
    (r'^logout/?$', 'logout'),

    url(r'^(?P<code>[abcehkmoprtxABCEHKMOPRTX1234567890]+)/$', RedirectView.as_view(url="profile/"), name='showCompany'),
    url(r'^(?P<code>[abcehkmoprtxABCEHKMOPRTX1234567890]+)/contacts/$', ShowCompanyRekContacts.as_view(), name='showCompanyContacts'),
    url(r'^(?P<code>[abcehkmoprtxABCEHKMOPRTX1234567890]+)/profile/$', ShowCompanyRekAbout.as_view(), name='showCompanyProfile'),

    url(r'^settings/$', login_required(ShowCompanySettings.as_view()), name='showCompanySettings'),
    url(r'^settings/s/$', login_required(ProfileSettingsInitialsView.as_view()), name='settings_initials'),
    url(r'^settings/edit/$', login_required(SaveSettingsView.as_view()), name='save_settings'),
    url(r'^settings/s/zones/$', login_required(TimeZonesListView.as_view()), name='time_zones_list'),
    url(r'^additional-settings/$', login_required(ShowCompanySettings.as_view()), name='showCompanyAdditionalSettings'),
    url(r'^change-password/$', login_required(ShowCompanySettings.as_view()), name='settings_change_password'),
    url(r'^password-recovery/$', PasswordRecovery.as_view(), name='password_recovery'),
    url(r'^new-password/(?P<link_id>.+)/$', NewPasswordView.as_view(), name='set_new_password'),

    url(r'^profile/i/(?P<company_rek_id>[abcehkmoprtxABCEHKMOPRTX1234567890]+)$', ProfileModuleInitialsView.as_view(), name='profile_settings'),
    url(r'^profile/s/$', login_required(ProfileSettingsInitialsView.as_view()), name='profile_settings_initial_view'),

    url(r'^activate_account/(?P<link_id>.+)$', AccountActivationView.as_view(), name='activation_view'),
)

