#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.forms import ModelForm
from rek.kladr.models import Region, District, City, Town, Street
from rek.kladr.models import Level, CenterType
from rek.kladr.models import LocationTypesLevel1, LocationTypesLevel2, LocationTypesLevel3
from rek.kladr.models import LocationTypesLevel4, LocationTypesLevel5

from autocomplete.views import autocomplete, AutocompleteSettings
from autocomplete.admin import AutocompleteAdmin

class LocationAutocomplete(AutocompleteSettings):
    search_fields = ('^name', '^id')

autocomplete.register(District.region, LocationAutocomplete)
autocomplete.register(City.district, LocationAutocomplete)
autocomplete.register(City.region, LocationAutocomplete)
autocomplete.register(Town.city, LocationAutocomplete)
autocomplete.register(Town.district, LocationAutocomplete)
autocomplete.register(Town.region, LocationAutocomplete)
autocomplete.register(Street.town, LocationAutocomplete)
autocomplete.register(Street.city, LocationAutocomplete)
autocomplete.register(Street.district, LocationAutocomplete)
autocomplete.register(Street.region, LocationAutocomplete)

class RegionAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name', 'location_type', 'id', 'postcode')
    list_filter     = ('location_type',)
    list_per_page   = 200
    save_on_top     = True

class DistrictAdminForm(forms.ModelForm):
    class Meta:
        model = District

    def clean_region(self):
        if (int(self.cleaned_data['id']) // 1000) != int(self.cleaned_data['region'].id):
            raise forms.ValidationError("Первые цифры кода района должны совпадать с кодом региона: %s != %s"
                % (self.cleaned_data['id'] // 1000, self.cleaned_data['region'].id))
        return self.cleaned_data['region']


class DistrictAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name', 'location_type', 'id', 'region', 'postcode', 'center_type')
    list_filter     = ('center_type', 'location_type')
    search_fields   = ('name', 'region__name',)
    raw_id_fields   = ('region',)
    list_per_page   = 200
    save_on_top     = True

    form = DistrictAdminForm

class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City

    def clean_region(self):
        if (int(self.cleaned_data['id']) // 1000000) != int(self.cleaned_data['region'].id):
            raise forms.ValidationError("Первые цифры кода города должны совпадать с кодом региона: %s != %s"
                % (self.cleaned_data['id'] // 1000000, self.cleaned_data['region'].id))
        return self.cleaned_data['region']

    def clean_district(self):
        if self.cleaned_data['district']:
            if (int(self.cleaned_data['id']) // 1000) != int(self.cleaned_data['district'].id):
                raise forms.ValidationError("Второй сегмент кода города должен совпадать с кодом района региона: %s != %s"
                    % (self.cleaned_data['id'] // 1000, self.cleaned_data['district'].id))
        return self.cleaned_data['district']

class CityAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name', 'location_type', 'id', 'region', 'district', 'postcode', 'center_type')
    list_filter     = ('center_type', 'location_type')
    search_fields   = ('name', 'region__name', 'district__name')
    raw_id_fields   = ('region', 'district')
    list_per_page   = 200
    save_on_top     = True

    form = CityAdminForm

class TownAdminForm(forms.ModelForm):
    class Meta:
        model = Town

    def clean_region(self):
        if (int(self.cleaned_data['id']) // 1000000000) != int(self.cleaned_data['region'].id):
            raise forms.ValidationError("Первые цифры кода населённого пункта должны совпадать с кодом региона: %s != %s"
                % (self.cleaned_data['id'] // 1000000000, self.cleaned_data['region'].id))
        return self.cleaned_data['region']

    def clean_district(self):
        if self.cleaned_data['district']:
            if (int(self.cleaned_data['id']) // 1000000) != int(self.cleaned_data['district'].id):
                raise forms.ValidationError("Второй сегмент кода населённого пункта должен совпадать с кодом района региона: %s != %s"
                    % (self.cleaned_data['id'] // 1000000, self.cleaned_data['district'].id))
        return self.cleaned_data['district']

    def clean_city(self):
        if self.cleaned_data['city']:
            if (int(self.cleaned_data['id']) // 1000) != int(self.cleaned_data['city'].id):
                raise forms.ValidationError("Третий сегмент кода населённого пункта должен совпадать с кодом города: %s != %s"
                    % (self.cleaned_data['id'] // 1000, self.cleaned_data['city'].id))
        return self.cleaned_data['city']

class TownAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name', 'location_type', 'id', 'region', 'district', 'city', 'postcode', 'center_type')
    list_filter     = ('center_type', 'location_type')
    search_fields   = ('name', 'region__name', 'district__name', 'city__name')
    raw_id_fields   = ('region', 'district', 'city')
    list_per_page   = 200
    save_on_top     = True

    form = TownAdminForm

class StreetAdminForm(forms.ModelForm):
    class Meta:
        model = Street

    def clean_region(self):
        if (int(self.cleaned_data['id']) // 10000000000000) != int(self.cleaned_data['region'].id):
            raise forms.ValidationError("Первые цифры кода улицы должны совпадать с кодом региона: %s != %s"
                % (self.cleaned_data['id'] // 10000000000000, self.cleaned_data['region'].id))
        return self.cleaned_data['region']

    def clean_district(self):
        if self.cleaned_data['district']:
            if (int(self.cleaned_data['id']) // 1000000000) != int(self.cleaned_data['district'].id):
                raise forms.ValidationError("Второй сегмент кода улицы должен совпадать с кодом района региона: %s != %s"
                    % (self.cleaned_data['id'] // 10000000000, self.cleaned_data['district'].id))
        return self.cleaned_data['district']

    def clean_city(self):
        if self.cleaned_data['city']:
            if (int(self.cleaned_data['id']) // 10000000) != int(self.cleaned_data['city'].id):
                raise forms.ValidationError("Третий сегмент кода улицы должен совпадать с кодом города: %s != %s"
                    % (self.cleaned_data['id'] // 10000000, self.cleaned_data['city'].id))
        return self.cleaned_data['city']

    def clean_town(self):
        if self.cleaned_data['town']:
            if (int(self.cleaned_data['id']) // 10000) != int(self.cleaned_data['town'].id):
                raise forms.ValidationError("Третий сегмент кода улицы должен совпадать с кодом населенного пункта: %s != %s"
                    % (self.cleaned_data['id'] // 1000, self.cleaned_data['town'].id))
        return self.cleaned_data['town']

class StreetAdmin(AutocompleteAdmin, admin.ModelAdmin):
    list_display    = ('name', 'id', 'location_type', 'region', 'district', 'city', 'town')
    list_filter     = ('location_type',)
    search_fields   = ('name', 'city__name', 'town__name')
    raw_id_fields   = ('region', 'district', 'city', 'town')
    list_per_page   = 200
    save_on_top     = True

    form = StreetAdminForm

admin.site.register(Level)
admin.site.register(CenterType)
admin.site.register(LocationTypesLevel1)
admin.site.register(LocationTypesLevel2)
admin.site.register(LocationTypesLevel3)
admin.site.register(LocationTypesLevel4)
admin.site.register(LocationTypesLevel5)
admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(Street, StreetAdmin)
