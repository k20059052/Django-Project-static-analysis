from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
from django.shortcuts import redirect
from itertools import chain
from operator import attrgetter

from django.views.generic import FormView
from django.http import HttpResponseRedirect
from ticketing.forms.specialist_faq import FAQForm
from django.urls import reverse, reverse_lazy

from ticketing.models import SpecialistDepartment,SpecialistMessage, FAQ, StudentMessage, Message
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin



from ticketing.models import (
    Ticket,
    SpecialistDepartment,
)

class SpecialistCreateFAQFromTicketView(LoginRequiredMixin, RoleRequiredMixin, FormView, ListView):
    template_name = 'faq/specialist_create_faq_from_ticket.html'
    required_roles = ['SP']
    form_class = FAQForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        specialist_department = SpecialistDepartment.objects.get(
            specialist=self.request.user
        )
        kwargs['department'] = specialist_department.department
        return kwargs

    def form_valid(self, form):
        '''
        Save the form data and redirect to the specialist dashboard.
        
        Args:
            self: object
                An instance of the class that defines the method.
            form : TicketForm
                The validated form object containing the ticket data.
        Returns:
            response : HttpResponse
                A redirect to the specialist dashboard with the ticket type parameter set to 'personal'.
        '''
        form.custom_save(
            specialist=self.request.user,
            department=SpecialistDepartment.objects.get(
                specialist=self.request.user
            ).department,
            question=form.cleaned_data['question'],
            subsection=form.cleaned_data['subsection'],
            answer=form.cleaned_data['answer'],
        )
        return redirect('specialist_dashboard', ticket_type='personal')

    def get_queryset(self):
        '''
        Retrieve and return the message associated with the current ticket.
        
        Args:
            self: object
                An instance of the class that defines the method.
        Returns:
            queryset: [Message]
                The messages associated with the current ticket, sorted by date and time in descending order.
        '''
        student_message = StudentMessage.objects.filter(
            ticket=self.kwargs['pk']
        )
        specialist_message = SpecialistMessage.objects.filter(
            ticket=self.kwargs['pk']
        )
        queryset = sorted(
            chain(student_message, specialist_message),
            key=attrgetter('date_time'),
            reverse=True,
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['ticket'] = Ticket.objects.get(id=self.kwargs['pk'])
        return context

    def post(self, *args, **kwargs):
        super().get(self, *args, **kwargs)
        return super().post(*args, **kwargs)


    
    
    
    
    
    


    
    