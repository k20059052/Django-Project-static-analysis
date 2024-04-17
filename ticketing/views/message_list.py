from django.shortcuts import render

from ticketing.mixins import RoleRequiredMixin
from ticketing.models import (
    Message,
    Ticket,
    StudentMessage,
    SpecialistMessage,
    SpecialistDepartment,
)
from django.views.generic import DetailView, ListView, CreateView
from itertools import chain
from operator import attrgetter
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Message
    template_name = 'partials/message_list.html'
    required_roles = ['ST', 'SP']
    # paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        '''
        Check if the logged-in user is authorized to access the specialist message view for a particular ticket.
        
        Args:
            self: object
                An instance of the class that defines the method.
            request: HttpRequest 
                The HTTP request object containing all the metadata with the request.
            *args: tuple 
                Positional arguments passed to the method.
            **kwargs: dict
                Keyword arguments passed t the method.
        Returns:
            HttpResponseRedirect
                A redirect to the student dashboard if the user is not authorized to access the specialist message view.
        '''
        allowed_ids = list(
            SpecialistDepartment.objects.filter(
                department=getattr(
                    Ticket.objects.get(id=self.kwargs['pk']), 'department'
                )
            ).values_list('specialist', flat=True)
        )
        allowed_ids.append(
            getattr(
                getattr(Ticket.objects.get(id=self.kwargs['pk']), 'student'),
                'id',
            )
        )
        if self.request.user.id not in allowed_ids:
            return HttpResponseRedirect(reverse('student_dashboard'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        '''
        Get messages associated with the ticket with the ID 
        specified in the URL parameters.
        
        Args:
            self: object
                An instance of the class that defines the method.
        Returns:
            queryset=QuerySet
                A queryset containing the messages for the ticket. Sorted by most recent created.
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

    def get_context_data(self, **kwargs):
        '''
        Returning the context data to be displayed to the template.
        
        Args:
            self: object
                An instance of the class that defines the method.
            **kwargs: dict
                Keyword arguments passed onto the context_data method.
        Rteurns 
            context: dict
                A dictionary containing the context data:
                    -context['ticket']=Ticket.objects.get(id=self.kwargs['pk']) // all tickets related to user
        '''
        context = super().get_context_data(**kwargs)
        context['ticket'] = Ticket.objects.get(id=self.kwargs['pk'])
        return context
