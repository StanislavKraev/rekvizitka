# -*- coding: utf-8 -*-
import re

from django import forms
from django.forms.widgets import PasswordInput
from django.conf import settings
from rek.mango.auth import User
from rek.promotions.models import RegistrationPromoCode
from rek.rekvizitka.utils import validateEmail

if "notification" not in settings.INSTALLED_APPS:
    notification = None

class SubscribeForm(forms.Form):
    email = forms.EmailField(required=True, label='Введите e-mail')

class PasswordResetForm(forms.Form):
    email = forms.EmailField(required=True, label='Введите свой e-mail логин')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.find_one(email=email):
            raise forms.ValidationError("Такого адреса не существует")
        return email

class SignupForm(forms.Form):
    email = forms.EmailField(required=True, label='Логин (e-mail)', max_length=70)
    brand_name = forms.CharField(required=True)
    password = forms.CharField(required=True)
    promo_code_part1 = forms.CharField(required=False)
    promo_code_part2 = forms.CharField(required=False)
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not validateEmail(email):
            setattr(self, 'email_error_str', u"Некорректный email")
            raise forms.ValidationError(u"Некорректный email")
        if User.find_one({'email' :  email}):
            setattr(self, 'email_error_str', u"Пользователь с таким адресом электронной почты уже существует")
            raise forms.ValidationError(u"Пользователь с таким адресом электронной почты уже существует")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6:
            setattr(self, 'password_error_str', u'Некорректный пароль. Минимальная длина 6 символов.')
            raise forms.ValidationError(u'Некорректный пароль. Минимальная длина 6 символов.')
        if not re.match(r"^[a-zA-Z0-9-&*!@#%^()_\.]+$", password):
            setattr(self, 'password_error_str', u'Некорректный пароль. Недопустимый символ.')
            raise forms.ValidationError(u'Некорректный пароль. Недопустимый символ.')
        return password

    def clean_brand_name(self):
        brand_name = self.cleaned_data['brand_name']
        if not len(brand_name):
            setattr(self, 'brand_name_error_str', u'Некорректное наименование компании')
            raise forms.ValidationError(u'Некорректное наименование компании')
        return brand_name

    def prepare_promo_code(self, promo_code_raw):
        if not promo_code_raw or not len(promo_code_raw):
            return None
        promo_code = promo_code_raw.strip()
        return unicode(int(promo_code))

    def clean_promo_code_part1(self):
        try:
            promo_code = self.prepare_promo_code(self.cleaned_data['promo_code_part1'])
        except Exception:
            setattr(self, 'promo_code_error_str', u'Некорректный промо код')
            raise forms.ValidationError(u'Некорректный промо код')

        return promo_code

    def clean_promo_code_part2(self):
        try:
            promo_code = self.prepare_promo_code(self.cleaned_data['promo_code_part2'])
        except Exception:
            setattr(self, 'promo_code_error_str', u'Некорректный промо код')
            raise forms.ValidationError(u'Некорректный промо код')

        return promo_code

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        promo_part1 = cleaned_data.get("promo_code_part1")
        promo_part2 = cleaned_data.get("promo_code_part2")
        if not promo_part1 or not promo_part2:
            cleaned_data['promo_code'] = None
            return cleaned_data
        promo_code = int(promo_part1 + promo_part2)

        try:
            if promo_code < RegistrationPromoCode.MIN_CODE_VALUE or promo_code > RegistrationPromoCode.MAX_CODE_VALUE:
                raise ValueError()
            code_obj = RegistrationPromoCode.objects.get_one({'code' : promo_code})
            if not code_obj or not code_obj.active:
                raise ValueError()

        except ValueError:
            setattr(self, 'promo_code_error_str', u'Некорректный промо код')
            raise forms.ValidationError(u'Некорректный промо код')

        cleaned_data['promo_code'] = code_obj
        return cleaned_data


class SigninForm(forms.Form):
    username = forms.EmailField(max_length=70)
    password = forms.CharField(widget=PasswordInput)
    publicpc = forms.BooleanField(required=False, initial=False, )

class EditProfileForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super (EditProfileForm, self).__init__(*args, **kwargs)
        self.request = request

    full_name = forms.CharField(max_length=255, required=False)
    old_password = forms.CharField(max_length=50, widget=PasswordInput, required=False)
    new_password = forms.CharField(max_length=50, widget=PasswordInput, required=False)
    new_password_repeat = forms.CharField(max_length=50, widget=PasswordInput, required=False)
    phone = forms.CharField(max_length=255, required=False)

    def clean_old_password(self):
        if not self.data['new_password']:
            return ''
        if not self.request.user.check_password(self.data['old_password']):
            raise forms.ValidationError("Неверно введён действующий пароль")

    def clean_new_password_repeat(self):
        new_password = self.data['new_password']
        new_password_repeat = self.data['new_password_repeat']
        if not new_password:
            return ''
        if new_password != new_password_repeat:
            raise forms.ValidationError("Новый пароль и его повторение не совпадают между собой")
