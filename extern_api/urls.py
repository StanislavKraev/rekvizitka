from django.conf.urls.defaults import patterns, url
from rek.extern_api.views import ExportRekDataView

urlpatterns = patterns('rek.extern_api.views',
    url(r'export_rek_data/(?P<code>[abcehkmoptxABCEHKMOPTX1234567890]+)$', ExportRekDataView.as_view(), name='api_export_rek_data'),
)
