from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('rek.static.views',
    url(r'^(?P<page_alias>.+)$', 'render', name='static_page'),
)
