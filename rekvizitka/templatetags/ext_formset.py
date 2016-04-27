from django import template

register = template.Library()

@register.simple_tag()
def ext_formset_as_ul(formset, onChange):
    return formset.as_ul(onChange)
