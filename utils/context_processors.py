from django.conf import settings

def rek(request):
    return { 'request' : request,
             'PATH' : request.path,
             'production' : settings.PRODUCTION,
             'CUR_LOCALE' : 'ru',
             'company_rek_id' : request.company.rek_id if hasattr(request, 'company') else '',
             'SITE_DOMAIN_NAME' : settings.SITE_DOMAIN_NAME}
  