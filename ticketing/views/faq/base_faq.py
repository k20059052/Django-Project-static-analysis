from django.contrib.auth.decorators import login_required
from ticketing.decorators import roles_allowed
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from ticketing.models import *


class BaseFaq(ListView):
    model = Department
    template_name = 'faq/faq.html'
    paginate_by = 9
    def get_queryset(self):
        return Department.objects.all()
