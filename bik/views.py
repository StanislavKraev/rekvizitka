from django.http import HttpResponse
from rek.bik.models import Region, Bank
from django.core import serializers

def getRegions (request):
    response = HttpResponse(mimetype='text/javascript')
    json = serializers.serialize('json', Region.objects.all(), indent=4)
    response.write(json)
    return response

def getBanks (request, region_id=0):
    response = HttpResponse(mimetype='text/javascript')
    region_id = int(region_id) if region_id else 0
    json = serializers.serialize('json', Bank.objects.filter(region__id=region_id), indent=4, relations='region')
    response.write(json)
    return response