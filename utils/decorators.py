from functools import wraps
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings

def is_superuser(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        if request.user.is_anonymous():
            return HttpResponseRedirect(settings.LOGIN_URL)

        if request.user.is_superuser:
            return f(request, *args, **kwds)
        else:
            logout(request)
            return HttpResponseForbidden()
    return wrapper
