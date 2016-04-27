from django.contrib import admin
from rek.bik.models import Region, Bank
from autocomplete.views import autocomplete, AutocompleteSettings
from autocomplete.admin import AutocompleteAdmin

class BankRegionAutocomplete(AutocompleteSettings):
    search_fields = ('^name', 'id')
    save_on_top     = True

autocomplete.register(Bank.region, BankRegionAutocomplete)

class BankAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name','id', 'region', 'city', 'correspondent_account')
    list_filter     = ('region', 'city')
    search_fields   = ('name', 'region__name')
    save_on_top     = True

admin.site.register(Region)
admin.site.register(Bank, BankAdmin)
