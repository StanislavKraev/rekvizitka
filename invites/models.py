# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from django.utils import timezone
from rek.mongo.models import SimpleModel, ObjectManager

class RecommendationStatusEnum:
    RECEIVED = 0 #when contractor send to contracor(first time view this request)
    DECLINED = 1
    ACCEPTED = 2

    @classmethod
    def choices(cls):
        return ((cls.DECLINED, cls.type_to_name(cls.DECLINED)),
                (cls.ACCEPTED, cls.type_to_name(cls.ACCEPTED)),
                (cls.RECEIVED, cls.type_to_name(cls.RECEIVED)),)

    @classmethod
    def type_to_name(cls, type):
        if type == cls.DECLINED:
            return u'отклонена'
        elif type == cls.ACCEPTED:
            return u'рекомендована'
        elif type == cls.RECEIVED:
            return u'получена'
        return u'-'

class RecommendationRequest(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.requester = kwargs.get('requester')    # company id
        self.recipient = kwargs.get('recipient')    # company id
        self.status = kwargs.get('status', RecommendationStatusEnum.RECEIVED)
        self.send_date = kwargs.get('send_date', timezone.now())
        self.message = kwargs.get('message', '')
        self.viewed = kwargs.get('viewed', False)
        self.requester_email = kwargs.get('requester_email')

    def _fields(self):
        return {
            'requester' : self.requester,
            'recipient' : self.recipient,
            'status' : self.status,
            'send_date' : self.send_date,
            'message' : self.message,
            'viewed' : self.viewed,
            'requester_email' : self.requester_email
        }

RecommendationRequest.objects = ObjectManager(RecommendationRequest, 'recommendation_requests',
                                              [('requester', 1), ('recipient', 1), ('send_date', -1)])

class Invite(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}

        self._id = kwargs.get('_id')
        self.message = kwargs.get('message')
        self.email = kwargs.get('email')
        self.cookie_code = kwargs.get('cookie_code', unicode(ObjectId()))
        self.created = kwargs.get('created', timezone.now())
        self.sender = kwargs.get('sender')
        self.rec_request = kwargs.get('rec_request')

    def _fields(self):
        return {
            'message' : self.message,
            'email' : self.email,
            'cookie_code' : self.cookie_code,
            'created' : self.created,
            'sender' : self.sender,
            'rec_request' : self.rec_request
        }

Invite.objects = ObjectManager(Invite, 'invites', [('email', 1), ('cookie_code', 1), ('sender', 1), ('rec_request', 1)])
