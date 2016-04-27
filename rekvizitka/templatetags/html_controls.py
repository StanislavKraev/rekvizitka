from django import template

register = template.Library()

@register.inclusion_tag("tags/select_part.html")
def make_select(select_model_field, select_value, css_name):
    context = {}

    options = []
    if select_model_field.null:
        options.append({'val' : 0,
                        'text' : '----------',
                        'selected' : select_value is None or not len(unicode(select_value))})
    
    for choice in select_model_field.rel.to.objects.all():
        options.append({'val' : choice.id,
                        'text' : unicode(choice),
                        'selected' : choice == select_value})

    select = {
        'css_id' : css_name,
        'css_name' : css_name
    }
    context['select'] = select
    context['options'] = options
    return context

@register.inclusion_tag("tags/select_part.html")
def make_intfield_select(select_model_field, select_value, css_name):
    context = {}

    options = []
    if select_model_field.null:
        options.append({'val' : 0,
                        'text' : '----------',
                        'selected' : select_value is None or not len(unicode(select_value))})

    for choice in select_model_field.choices:
        options.append({'val' : choice[0],
                        'text' : unicode(choice[1]),
                        'selected' : choice[0] == select_value})

    select = {
        'css_id' : css_name,
        'css_name' : css_name
    }
    context['select'] = select
    context['options'] = options
    return context