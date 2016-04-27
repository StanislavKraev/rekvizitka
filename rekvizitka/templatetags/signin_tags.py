# -*- coding: utf-8 -*-
from django import template
from rek.rekvizitka.forms import SigninForm, SignupForm

register = template.Library()

@register.inclusion_tag("includes/navigation/index.html", takes_context=True)
def signin_form(context):
    result = {}
    for d in context:
        result.update(d)
    if 'top_signin_form' not in result:
        result['top_signin_form'] = SigninForm()
    if 'signup_form' not in result:
        result['signup_form'] = SignupForm()
    if 'request' in context:
        result['show_login_form'] = 'next' in context['request'].GET
    return result

