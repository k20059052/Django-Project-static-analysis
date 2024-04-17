from django.contrib import admin
from ticketing.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(SpecialistInbox)
admin.site.register(SpecialistDepartment)
admin.site.register(SpecialistMessage)
