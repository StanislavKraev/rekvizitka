from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^api/regions$', 'rek.bik.views.getRegions'),
    (r'^api/banks/region_(?P<region_id>\d+)$', 'rek.bik.views.getBanks'),
    #(r'^(?P<page_alias>.+)$', 'rek.static.views.showPageByAlias'),
)
