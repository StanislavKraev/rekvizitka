# -*- coding: utf-8 -*-
from datetime import timedelta
import sys
from django.utils import timezone
from rek.cron.cron_task import CronTaskBase
from rek.invites.models import RecommendationRequest, RecommendationStatusEnum
from rek.rekvizitka.models import Company
from rek.system_data.rek_settings import SettingsManager

class RemoveOldRecRequestsTask(CronTaskBase):
    def execute(self):
        print >> sys.stdout, 'Executing RemoveOldRecRequestsTask'

        query = {
            'status': {'$ne': RecommendationStatusEnum.ACCEPTED},
            'send_date': {'$lte': timezone.now() - timedelta(seconds=SettingsManager.get_property('rtimeout') * 3600)}
        }
        items_to_remove = RecommendationRequest.objects.get(query)
        if not len(items_to_remove):
            return

        requested_companies = {}
        for item in items_to_remove:
            requester = item.requester
            recipient = item.recipient
            if recipient not in requested_companies:
                requested_companies[recipient] = set([requester])
            else:
                requested_companies[recipient].add(requester)

        for requested_company in requested_companies:
            requester_list = requested_companies[requested_company]
            Company.objects.update({'_id' : requested_company},
                                   {'$pullAll' : {'rec_requesters' : list(requester_list)}})

        RecommendationRequest.objects.collection.remove(query)
