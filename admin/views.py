# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from django.views.generic.base import View

class AdminMainView(View):
    def get(self, request):
        return render_to_response('amain.html', {}, context_instance=RequestContext(request))
