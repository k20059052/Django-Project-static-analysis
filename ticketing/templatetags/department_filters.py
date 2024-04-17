from ticketing.models import Department
from ticketing.utility.user import *
from django import template
register = template.Library()

@register.filter
def user_department_string(user):
    department = get_user_department(user)
    if department == None:
        return 'None'
    return department.name
