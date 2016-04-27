# -*- coding: utf-8 -*-
from django import forms

class FeedbackForm(forms.Form):
    email = forms.EmailField(max_length = 50, label='E-mail для ответа', required = True)
    msg = forms.CharField(max_length = 2000, widget = forms.Textarea, required = True, label='Сообщение')
    #для ботов - должно быть пустое и скрывается Javaскриптом при загрузке
    extra_field = forms.CharField(widget = forms.TextInput, required = False, label='Дополнительное поле')
