# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from rek.chat.views import DialogListView, ChatDialogView, CreateDialogView, DialogListInitialsView, DialogInitialsView, DeleteDialogView, MoreMessagesView
from rek.rekvizitka.decorators import registration_completed_required

urlpatterns = patterns('rek.chat.views',
    url(r'^$', registration_completed_required(DialogListView.as_view()), name='chat_dialog_list'),
    url(r'^list/i/$', registration_completed_required(DialogListInitialsView.as_view()), name='dialog_list_initials'),
    url(r'^dialog/(?P<dialog_id>[0-9a-zA-Z-]+)/i/$', registration_completed_required(DialogInitialsView.as_view()), name='dialog_initials'),
    url(r'^dialog/(?P<dialog_id>[0-9a-zA-Z-]+)/$', registration_completed_required(ChatDialogView.as_view()), name='chat_dialog_view'),
    url(r'^create/(?P<companion_id>[0-9a-zA-Z-]+)/$', login_required(CreateDialogView.as_view()), name='create_dialog'),
    url(r'^delete/(?P<dialog_id>[0-9a-zA-Z-]+)/$', registration_completed_required(DeleteDialogView.as_view()), name='delete_dialog'),
    url(r'^mm/(?P<dialog_id>[0-9a-zA-Z-]+)/$', registration_completed_required(MoreMessagesView.as_view()), name='show_more_messages'),
)
