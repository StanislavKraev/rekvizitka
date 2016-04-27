# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns
from rek.mail_messages.views import CompanyMessagesView, ViewForm, MessagesCollectionView, AddMessages, SetMessageImportant, CompanyContactsView, CompanySettingsView, MessageModuleInitialsView
from rek.rekvizitka.decorators import registration_completed_required
from rek.utils.decorators import is_superuser

urlpatterns = patterns('rek.mail_messages.views',
    url(r'^$', registration_completed_required(CompanyMessagesView.as_view()), name='messages'),
    url(r'^letters/$', registration_completed_required(CompanyMessagesView.as_view()), name='messages_letters'),
    url(r'^contacts/$', registration_completed_required(CompanyContactsView.as_view()), name='messages_contacts'),
    url(r'^settings/$', registration_completed_required(CompanySettingsView.as_view()), name='messages_settings'),

    url(r'^letters/important/$', registration_completed_required(SetMessageImportant.as_view()), name='set_message_important'),
    url(r'^c/$', registration_completed_required(MessagesCollectionView.as_view()), name='collection_messages'),
    url(r'^i/$', registration_completed_required(MessageModuleInitialsView.as_view()), name='messages_initials_module'),

    #test urls
    url(r'^form/$', is_superuser(ViewForm.as_view()), name='view_form'),
    url(r'^add_me_message/$', is_superuser(AddMessages.as_view()), name='add_messages'),
)
