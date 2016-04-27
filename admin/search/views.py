# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.base import View

class SearchMainView(View):
    def get(self, request):
        return render_to_response("search/asearch_main.html", {}, context_instance=RequestContext(request))
