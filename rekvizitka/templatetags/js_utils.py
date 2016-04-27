from django import template
register = template.Library()

@register.simple_tag
def bool_to_js(val):
    return unicode(val).lower()

