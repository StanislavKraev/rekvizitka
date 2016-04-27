from django import forms
from django.forms import formsets
from django.template.defaultfilters import escapejs
from django.utils.safestring import mark_safe

class DivForm(forms.Form):
    def as_ul(self):
        return self._html_output(
            normal_row = u'<li%(html_class_attr)s><span class="key">%(errors)s%(label)s </span> '
                         '<span class="value">%(field)s</span>%(help_text)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' <span class="helptext">%s</span>',
            errors_on_separate_row = False)

REG_FORMSET_JS = """
<script type="text/javascript" ajax="true">
    Rek.InplaceFormEdit.initFormset('%(form_class)s', '%(div_empty_form)s', '%(form_name)s', %(change_callback)s);
</script>"""

class ExtFormSet(formsets.BaseFormSet):
    form_css_class = None

    def _generate_name(self, form_name, id):
        return '%s_form_%s' % (form_name, str(id))

    def _surround_with_div(self, form_name, id, value):
        return '<div class="formset_form" id="%s">%s</div>' % (self._generate_name(form_name, id), value)

    def as_ul(self, jsChangeCallback = None):
        forms = u' '.join([self._surround_with_div(form.name, i, form.as_ul()) for i, form in enumerate(self)])
        return mark_safe(u'\n'.join([unicode(self.management_form), forms]) + \
                         REG_FORMSET_JS % { 'div_empty_form' : escapejs(self.div_empty_form),
                                            'form_name' : self.empty_form.name,
                                            'form_class' : self.form_css_class,
                                            'change_callback': jsChangeCallback or 'null'})

    def _div_empty_form(self):
        form = self.empty_form
        form_str = form.as_ul()
        return self._surround_with_div(form.name, '__prefix__',form_str)

    div_empty_form = property(_div_empty_form)
