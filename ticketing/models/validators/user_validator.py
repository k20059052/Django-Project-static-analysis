from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ticketing.models.users import User


def validate_user_as_specialist(user_id):
    user = User.objects.get(id=user_id)
    if user.role != 'SP':
        raise ValidationError(
            _('%(user)s is not a specialist'),
            params={'user': user},
        )


def validate_user_as_student(user_id):
    user = User.objects.get(id=user_id)
    if user.role != 'ST':
        raise ValidationError(
            _('%(user)s is not a student'),
            params={'user': user},
        )
