from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
from ticketing.models import Ticket, SpecialistInbox, SpecialistDepartment


class TicketView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = ['ST', 'SP', 'DI']

    def get(self, request, *args, **kwargs):
        return render(request, 'ticket.html')
