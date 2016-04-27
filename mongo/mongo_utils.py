from datetime import datetime
from django.utils import timezone

def mongodb_datetime_now():
    nd = timezone.now()
    return datetime(nd.year, nd.month, nd.day, nd.hour, nd.minute, nd.second, microsecond = 0)
  