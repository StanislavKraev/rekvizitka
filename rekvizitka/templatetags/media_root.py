from django.conf import settings
from django import template
register = template.Library()

@register.simple_tag
def media_root():
    return getattr(settings, 'MEDIA_ROOT', '/')