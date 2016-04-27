import datetime
from django.utils import unittest
import pytz
from rek.utils.timezones import known_timezones, make_tz_name

class BaseTestCase(unittest.TestCase):
    def testFirst(self):
        msc_tz = pytz.timezone('Europe/Moscow')
        loc_time = datetime.datetime(2012, 6, 27, 1, 30, 00)
        msc_time = msc_tz.localize(loc_time, is_dst=False)

        loc_time = datetime.datetime(2011, 4, 27, 1, 30, 00)
        msc_time = msc_tz.localize(loc_time, is_dst=False)

        loc_time = datetime.datetime.now()
        zones = [(zone[0] + 1, make_tz_name(zone[1], loc_time, 'en'.lower())) for zone in enumerate(known_timezones)]

#        print(zones)
#        print(full_tz_name('Europe/Moscow', 'en'.lower()))