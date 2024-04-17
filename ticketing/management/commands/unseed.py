from django.core.management.base import BaseCommand, CommandError
from ticketing.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.all().delete()
        Department.objects.all().delete()
        SpecialistDepartment.objects.all().delete()
        SpecialistInbox.objects.all().delete()
        SpecialistMessage.objects.all().delete()
        FAQ.objects.all().delete()
