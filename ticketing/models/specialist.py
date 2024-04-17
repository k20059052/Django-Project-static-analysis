from django.db import models
from django.utils.translation import gettext_lazy as _
from ticketing.models.validators.user_validator import *


class SpecialistDepartment(models.Model):
    specialist = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        db_column='specialist',
        validators=[validate_user_as_specialist],
    )
    department = models.ForeignKey(
        'Department', on_delete=models.CASCADE, db_column='department'
    )


class SpecialistInbox(models.Model):
    specialist = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        db_column='specialist',
        validators=[validate_user_as_specialist],
    )
    ticket = models.ForeignKey(
        'Ticket', on_delete=models.CASCADE, db_column='ticket'
    )
