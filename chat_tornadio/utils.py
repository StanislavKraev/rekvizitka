# -*- coding: utf-8 -*-
import time

def get_cts():
    return int(round(time.time() * 100000))

def cts_from_timedelta(td):
    ts = td.seconds + td.days * 24 * 3600
    return ts * 100000
