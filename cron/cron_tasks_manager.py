import inspect
import sys
from django.conf import settings
from django.utils.importlib import import_module
from rek.cron.cron_task import CronTaskBase

class CronTasksManager(object):
    def __init__(self):
        self.cron_tasks = []
        for app_name in settings.INSTALLED_APPS:
            try:
                #print >> sys.stdout, 'Importing %s.cron' % app_name
                module = import_module('.cron', app_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and CronTaskBase in obj.__bases__:
                        task = obj()
                        self.cron_tasks.append(task)
            except ImportError, ex:
                if unicode(ex) != "No module named cron":
                    print >> sys.stderr, ex

    def run(self):
        for task in self.cron_tasks:
            try:
                task.execute()
            except Exception, ex:
                print >> sys.stderr, ex

cron_tasks_manager = CronTasksManager()
