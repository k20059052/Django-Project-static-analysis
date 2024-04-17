from ticketing.models import User
from ticketing.utility import user
from django import template
from django import forms
register = template.Library()


@register.filter
def is_radio_select(field):
    return isinstance(field.field.widget, forms.RadioSelect)
