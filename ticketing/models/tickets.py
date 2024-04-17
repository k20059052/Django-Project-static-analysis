from django.db import models
from django.utils.translation import gettext_lazy as _
from ticketing.models.validators.user_validator import *


class Ticket(models.Model):
    student = models.ForeignKey(
        'User', on_delete=models.CASCADE, validators=[validate_user_as_student]
    )
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    header = models.CharField(max_length=100, blank=False)

    class Status(models.TextChoices):
        OPEN = 'Open'
        CLOSED = 'Closed'

    class Meta:
        ordering = ['-id']

    status = models.CharField(
        max_length=20, default=Status.OPEN, choices=Status.choices
    )
    # Tickets are open by default, this can be changed to a SlugField if inbox are separated as follows:
    # .../inbox/open
    # .../inbox/closed
    # etc.
    # As this can automatically create links instead of writing to urls.py everytime a new ticket status is introduced
    class Meta:
        ordering = ['status']


# Abstract Class
class Message(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    date_time = models.DateTimeField(auto_now_add=True)


class StudentMessage(Message):
    pass


class SpecialistMessage(Message):
    responder = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        db_column='responder',
        validators=[validate_user_as_specialist],
    )
