from ticketing.models import User
from django import template
register = template.Library()

@register.filter
def user_role_string(value):
    match value:
        case User.Role.STUDENT:
            return "Student"        
        case User.Role.SPECIALIST:
            return "Specialist"
        case User.Role.DIRECTOR:
            return "Director"
    return "None"
