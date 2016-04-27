from django import template

register = template.Library()

@register.inclusion_tag('forms/init_form_submitter_simple.html')
def form_ajax_submit(ajax_editable, edit_button_selector,
                     ajax_editor, form_selector,
                     edit_form_selector, cancel_button_selector,
                     modify_button_selector, tab_index,
                     extra_post_args = '{}'):
    
    context = ajax_editable.get_context_data()
    context['url'] = ajax_editor.url + context['url_tag']
    del context['url_tag']
    context['edit_button_selector'] = edit_button_selector
    context['form_selector'] = form_selector
    context['edit_form_selector'] = edit_form_selector
    context['cancel_button_selector'] = cancel_button_selector
    context['modifyButtonSelector'] = modify_button_selector
    context['tabIndex'] = tab_index
    context['extra_post_args'] = extra_post_args

    return context

@register.inclusion_tag('ro_additional_info.html')
def ro_additional_info(company):
    return { 'company' : company }

@register.inclusion_tag('ro_employee_list.html')
def ro_employee_list(company):
    return { 'company' : company}