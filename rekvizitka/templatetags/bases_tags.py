# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.inclusion_tag("modules/portal/main_header/templates/main_header_unauth.html")
def logged_out():
    return {}
