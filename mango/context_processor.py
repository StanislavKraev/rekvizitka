from django.utils.functional import SimpleLazyObject
from rek.mango.auth import AnonymousUser

def auth(request):
    def get_user():
        if hasattr(request, 'user'):
            return request.user
        else:
            return AnonymousUser()

    return { 'user': SimpleLazyObject(get_user) }
