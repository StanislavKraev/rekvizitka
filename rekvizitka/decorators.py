from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from rek.rekvizitka.account_statuses import CompanyAccountStatus

def registration_completed_required(function=None, redirect_url='/verification/'):
    """
    Checks if user is logged in and registration is completed
    """
    
    def wrapper(request, *args, **kw):
        company = request.company
        if not company:
            return HttpResponseRedirect(redirect_url)

        if CompanyAccountStatus.is_active_account(company.account_status):
            if not company.is_required_data_filled():
                return HttpResponseRedirect('/fill_required/')
            return function(request, *args, **kw)

        return HttpResponseRedirect(redirect_url)
            
    return login_required(wrapper)
