from django.conf.urls.defaults import *

urlpatterns = patterns('rek.kladr.views',
    (r'api/locations/level_1$', 'getLocations', {'level': 1, 'parent': None}),
    (r'api/locations/level_(?P<level>\d+)/parent_(?P<parent>\d+)$', 'getLocations'),
    (r'api/locations/level_\d+$', 'giveEmptySet'),
    (r'api/locations/level/(?P<level>\d+)/parent/(?P<parent>\d*)/term/(?P<term>.*)$',
        'getLocationsForAutocomplete', {'limit': 5}),
    (r'api/locations/level/(?P<level>\d+)/term/(?P<term>.*)$',
        'getLocationsForAutocomplete', {'limit': 5, 'parent': None}),
)
