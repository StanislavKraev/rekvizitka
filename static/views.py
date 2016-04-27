from django.http import Http404
from django.shortcuts import render_to_response
from rek.static.models import StaticPage
from django.template.context import RequestContext

def render(request, page_alias=''):
    page = StaticPage.objects.get(alias=page_alias, enabled=True)
    if not page:
        raise Http404()

    return render_to_response('static_page_with_sidebar.html',
                              {'page' : page},
                              context_instance=RequestContext(request))

