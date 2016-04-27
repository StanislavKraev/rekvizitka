# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from rek.feedback.views import SendFeedback, SendFeedbackInitialsView

urlpatterns = patterns('',
    url(r'^$', SendFeedback.as_view(), name='SendFeedback'),
    url(r'^i/$', SendFeedbackInitialsView.as_view(), name='feedback_data_view'),
)
