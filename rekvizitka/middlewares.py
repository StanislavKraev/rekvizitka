from django.contrib.auth import logout
from django.utils.cache import add_never_cache_headers, patch_response_headers
from django.utils.timezone import activate
from rek.rekvizitka.models import CompanyEmployee, Company

CACHE_TIMEOUT = 3600 * 24 * 30

class CompanyEmployeeMiddleware(object):
    def process_request(self, request):
        user = request.user
        if not user:
            return None
        if not user.is_authenticated():
            return None

        employee = CompanyEmployee.objects.get_one({'user_id' : user._id})

        if not employee:
            logout(request)
            return None
        setattr(request, 'employee', employee)

        company = Company.objects.get_one({'_id' : employee.company_id})
        if company:
            setattr(request, 'company', company)
        else:
            logout(request)

        return None

class DisableClientSideCachingMiddleware(object):
    def process_response(self, request, response):
        if request.path.startswith('/combo/'):
            patch_response_headers(response, CACHE_TIMEOUT)
        else:
            add_never_cache_headers(response)
        return response