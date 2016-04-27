from django.http import HttpResponse
from rek.kladr.models import Region, District, City, Town, Street
from django.core import serializers
import django.utils.simplejson as json

def getLocations (request, level=1, parent=None):
    response = HttpResponse(mimetype='text/javascript')

    level = int(level) if level else 0
    parent = int(parent) if parent else 0

    parent_level = 0 if not parent else 1 if parent < 100 else 2 if parent < 100000  else 3 if parent < 100000000 else 4 if parent < 100000000000 else 5

    if level == 1:
        locations = Region.objects.all()
    elif level == 2:
        locations = District.objects.filter(region__id = parent) if parent_level == 1\
        else District.objects.all()
    elif level == 3:
        locations = City.objects.filter(district__id = parent) if parent_level == 2\
        else City.objects.filter(region__id = parent, district__id__isnull = True) if parent_level ==  1\
        else City.objects.all()
    elif level == 4:
        locations = Town.objects.filter(city__id = parent) if parent_level == 3\
        else Town.objects.filter(district__id = parent, city__id__isnull = True) if parent_level == 2\
        else Town.objects.filter(region__id = parent, district__id__isnull = True, city__id__isnull = True) if parent_level == 1\
        else Town.objects.all()
    elif level == 5:
        locations = Street.objects.filter(town__id = parent) if parent_level == 4\
        else Street.objects.filter(city__id = parent, town__id__isnull = True) if parent_level == 3\
        else Street.objects.filter(district__id = parent, city__id__isnull = True, town__id__isnull = True) if parent_level == 2\
        else Street.objects.filter(region__id = parent, district__id__isnull = True, city__id__isnull = True, town__id__isnull = True) if parent_level ==  1\
        else Street.objects.all()
    else:
        locations = []

    json = serializers.serialize('json', locations , indent=4, relations=('location_type',))
    response.write(json)    
    return response

def giveEmptySet (request):
    response = HttpResponse(mimetype='text/javascript')
    json = serializers.serialize('json', [])
    response.write(json)
    return response

def getLocationsForAutocomplete (request, level, parent, term, limit):
    level = int(level) if level else 0
    parent = int(parent) if parent else 0
    parent_level = 0 if not parent else\
        1 if parent < 100 else\
        2 if parent < 100000 else\
        3 if parent < 100000000 else\
        4 if parent < 100000000000 else 5

    if level == 1:
        locations = Region.objects.filter(name__istartswith=term)[:limit]
    elif level == 2:
        if parent_level == 1:
            locations = District.objects.filter(region=parent, name__istartswith=term)[:limit]
        else:
            return giveEmptySet(request)
    elif level == 3:
        if parent_level == 1:
            locations = City.objects.filter(region=parent, name__istartswith=term, district__isnull = True)[:limit]
        elif parent_level == 2:
            locations = City.objects.filter(district=parent, name__istartswith=term)[:limit]
        else:
            return giveEmptySet(request)
    elif level == 4:
        if parent_level == 1:
            locations = Town.objects.filter(region=parent, name__istartswith=term, district__isnull = True, city__isnull = True)[:limit]
        elif parent_level == 2:
            locations = Town.objects.filter(district=parent, name__istartswith=term, city__isnull = True)[:limit]
        elif parent_level == 3:
            locations = Town.objects.filter(city=parent, name__istartswith=term)[:limit]
        else:
            return giveEmptySet(request)
    elif level == 5:
        if parent_level == 1:
            locations = Street.objects.filter(region=parent, name__istartswith=term, district__isnull = True,  city__isnull = True, town__isnull = True)[:limit]
        elif parent_level == 2:
            locations = Street.objects.filter(district=parent, name__istartswith=term, city__isnull = True, town__isnull = True)[:limit]
        elif parent_level == 3:
            locations = Street.objects.filter(city=parent, name__istartswith=term, town__isnull = True)[:limit]
        elif parent_level == 4:
            locations = Street.objects.filter(town=parent, name__istartswith=term)[:limit]
        else:
            return giveEmptySet(request)
    else:
        locations = Region.objects.filter(name__istartswith=term)[:limit]

    locations_transformed = [{'label': (location.name + ' ' + location.location_type.abbr + '.'), 'value': location.id, 'postcode': location.postcode} for location in locations]
    #json = serializers.serialize('json', locations_transformed , indent=4)#, relations=('location_type',))

    response = HttpResponse(mimetype='text/javascript')
    response.write(json.dumps(locations_transformed, sort_keys=True, indent=4))
    return response