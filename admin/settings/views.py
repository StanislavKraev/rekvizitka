# -*- coding: utf-8 -*-
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.base import View
from rek.system_data.rek_settings import SettingsManager

class ManageSettings(View):
    def get(self, request):
        errors = {}
        data = {'company_auto_index' : SettingsManager.get_property('company_auto_index'),
                'bill_auto_index' : SettingsManager.get_property('bill_auto_index'),
                'verify_bill_price' : SettingsManager.get_property('verify_bill_price'),
                'registration_promo_action_amount' : SettingsManager.get_property('registration_promo_action_amount'),
                'rnes' : SettingsManager.get_property('rnes'),
                'rmax' : SettingsManager.get_property('rmax'),
                'rtimeout' : SettingsManager.get_property('rtimeout'),
                'verifylettercount' : SettingsManager.get_property('verifylettercount'),
                'verifyletterdelaydays' : SettingsManager.get_property('verifyletterdelaydays'),
                'invite_bonus' : SettingsManager.get_property('invite_bonus'),
                'errors' : errors}
        return render_to_response('settings/manage_settings.html', data, context_instance=RequestContext(request))

    def post(self, request):
        if 'save_settings' not in request.POST:
            return HttpResponseBadRequest()
        errors = {}
        data = {'company_auto_index' : SettingsManager.get_property('company_auto_index'),
                'bill_auto_index' : SettingsManager.get_property('bill_auto_index'),
                'verify_bill_price' : SettingsManager.get_property('verify_bill_price'),
                'registration_promo_action_amount' : SettingsManager.get_property('registration_promo_action_amount'),
                'rnes' : SettingsManager.get_property('rnes'),
                'rmax' : SettingsManager.get_property('rmax'),
                'rtimeout' : SettingsManager.get_property('rtimeout'),
                'verifylettercount' : SettingsManager.get_property('verifylettercount'),
                'verifyletterdelaydays' : SettingsManager.get_property('verifyletterdelaydays'),
                'invite_bonus' : SettingsManager.get_property('invite_bonus'),
                'errors' : errors}

        verify_bill_price = request.POST.get('verify_bill_price').strip()
        registration_promo_action_amount = request.POST.get('registration_promo_action_amount').strip()

        if len(verify_bill_price):
            try:
                verify_bill_price_int = int(verify_bill_price)
                if verify_bill_price_int <= 0 or verify_bill_price_int > 1000000:
                    raise Exception()
                if verify_bill_price_int != data['verify_bill_price']:
                    SettingsManager.set_property('verify_bill_price', verify_bill_price_int)
                    data['verify_bill_price'] = verify_bill_price_int
            except ValueError:
                errors['verify_bill_price'] = "Введите корректную сумму"

        if len(registration_promo_action_amount):
            try:
                registration_promo_action_amount_int = int(registration_promo_action_amount)
                if registration_promo_action_amount_int <= 0 or registration_promo_action_amount_int > 1000000:
                    raise Exception()
                if registration_promo_action_amount_int != data['registration_promo_action_amount']:
                    SettingsManager.set_property('registration_promo_action_amount', registration_promo_action_amount_int)
                    data['registration_promo_action_amount'] = registration_promo_action_amount_int
            except ValueError:
                errors['registration_promo_action_amount'] = "Введите корректную сумму"

        rnes = request.POST.get('rnes', '').strip()
        rmax = request.POST.get('rmax', '').strip()
        rtimeout = request.POST.get('rtimeout', '').strip()
        verifylettercount = request.POST.get('verifylettercount', '').strip()
        verifyletterdelaydays = request.POST.get('verifyletterdelaydays', '').strip()
        invite_bonus = request.POST.get('invite_bonus', '').strip()

        self.update_int_setting('rnes', rnes, 1, 100, errors, data)
        self.update_int_setting('rmax', rmax, 1, 100, errors, data)
        self.update_int_setting('rtimeout', rtimeout, 1, 24 * 365, errors, data)

        self.update_int_setting('verifylettercount', verifylettercount, 0, 100, errors, data)
        self.update_int_setting('verifyletterdelaydays', verifyletterdelaydays, 1, 366, errors, data)
        self.update_int_setting('invite_bonus', invite_bonus, 0, 3000, errors, data)

        if not len(errors):
            return HttpResponseRedirect(request.path)

        return render_to_response('settings/manage_settings.html', data, context_instance=RequestContext(request))

    def update_int_setting(self, setting_name, string_val, min_value, max_value, errors_dict, data_dict, error_msg = None):
        try:
            val_i = int(string_val)
            if val_i < min_value or val_i > max_value:
                raise Exception()
            if val_i != SettingsManager.get_property(setting_name):
                SettingsManager.set_property(setting_name, val_i)
                data_dict[setting_name] = val_i
        except Exception:
            errors_dict[setting_name] = "Введите целочисленное значение [%d - %d]" % (min_value, max_value) if not error_msg else error_msg

