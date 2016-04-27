# -*- coding: utf-8 -*-

class CronTaskBase(object):
    def execute(self):
        raise Exception('Must be overridden')