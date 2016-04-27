# -*- coding: utf-8 -*-

import sys
from django.core.management.base import BaseCommand
from rek.cron.cron_tasks_manager import cron_tasks_manager

class Command(BaseCommand):
    help = u'Run all cron tasks\n'

    def handle(self, *args, **options):
        print >> sys.stdout, 'Cron run...'
        cron_tasks_manager.run()