# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe

class AdminImageWidget(forms.ClearableFileInput):
    """
    A ImageField Widget for admin that shows a thumbnail.
    """
    template_with_initial = u'%(initial_text)s: %(initial)s<br> %(clear_template)s<br />%(input_text)s: %(input)s'
    def render(self, name, value, attrs=None):
        output = ''
        try:
            width = value.width
            height = value.height
            url = value.url
        except Exception:
            return super(AdminImageWidget, self).render(name, value, attrs)

        output += u"""<div style="text-align: left"><a target="_blank" href="%s">
                   <img src="%s" style="max-height: 100px;border: 1px solid #ccc"/></a>
                   <p style="margin:0;padding:0;text-align:left;">Размер: %s x %s</p><br>
                   """ % (url, url, width, height)
        output += super(AdminImageWidget, self).render(name, value, attrs)
        output += '</div>'
        return mark_safe(output)
