import codecs, os
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import View
from django.core.cache import cache

class ComboLoaderView(View):
    ROOT = settings.COMBO_LOADER_ROOT

    def get(self, request):
        cur_locale = 'ru'
        request_full_path = request.get_full_path()
        cached =  cache.get(request_full_path) if len(request_full_path) < 240 else None
        if cached:
            split_pos = cached.find('&&&&', 0, 100)
            if split_pos >= 0:
                mimetype = cached[:split_pos]
                content = cached[split_pos + 4:]

                return HttpResponse(content, mimetype)

        file_list = request.GET.keys()
        if not len(file_list):
            return HttpResponse()

        type = None
        content_list = []
        for file_name in file_list:
            base, ext = os.path.splitext(file_name)
            if ext == '.js':
                newType = 'js'
            elif ext == '.css':
                newType = 'css'
            else:
                return HttpResponseBadRequest("Unknown file type requested: %s" % ext)

            if not type:
                type = newType
            elif type != newType:
                return HttpResponseBadRequest("Only same file format types are allowed")

            path = os.path.join(os.path.join(self.ROOT, cur_locale), file_name)
            with codecs.open(path, 'r', 'utf-8') as file:
                content_list.append(file.read())

        mimetypes = {'css' : 'text/css',
                     'js' : 'application/x-javascript'}

        mimetype = mimetypes.get(type)
        if not mimetype:
            return HttpResponseBadRequest("Unknown file type requested.")

        content = '\n'.join(content_list)
        if len(request_full_path) < 240:
            cache.set(request_full_path, '&&&&'.join((mimetype, content)), settings.COMBO_SRV_CACHE_TIMEOUT)
        return HttpResponse(content, mimetype)
