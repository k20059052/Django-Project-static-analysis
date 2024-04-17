from ticketing.models import User
from django import template
register = template.Library()


@register.filter
def is_selected(selected, id):
    return str(id) in selected
