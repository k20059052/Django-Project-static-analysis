from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
from django.shortcuts import redirect


from ticketing.models import (
    Ticket,
    SpecialistInbox,
    SpecialistDepartment,
    Message,
)


class SpecialistClaimTicketView(LoginRequiredMixin, RoleRequiredMixin, View):
    template_name = 'specialist/specialist_claim_ticket.html'
    required_roles = ['SP']

    def get(self, request, *args, **kwargs):
        '''
        Returning a response for viewing a ticket via the template.
        
        Args:
            self: object
                An instance of the class that defines this method.
            request: HttpRequest
                The HTTP request object containg metadata about the request.
        Returns:
            response: HttpResponse
                The HTTP response object containing the ticket data or an error message.
        Raises:
            ValidationError
                If the user or department is invalid, or if the ticket 
                cannot be viewed  by the specialist.             
        '''
        user = request.user
        # CHECK IF THE TICKET WE ARE VIEWING CAN BE VIEWED BY SPECIALIST
        ticket = Ticket.objects.filter(id=self.kwargs['pk'])

        return self.validate_view_ticket(
            user, self.get_department(), ticket, request
        )

    def post(self, request, *args, **kwargs):
        '''
        Accept a ticket and add it to the specialist's inboox.
        
        Args:
            self: object
                An instance of the class that defines this method.
            request: HttpRequest 
                The HTTP request object that contains the meta data about the request.
        Returns:
            response: HttpResponse
                A redirect to the specialist dashboard, with the ticket type
                parameter set to 'department'.    
        '''
        ticket_id = self.request.POST.get('accept_ticket')
        ticket_list = Ticket.objects.filter(id=ticket_id)
        if len(ticket_list) == 0:
            return redirect('specialist_dashboard', ticket_type='department')
        else:
            SpecialistInbox.objects.create(
                specialist=request.user, ticket=ticket_list[0]
            )

        return redirect('specialist_dashboard', ticket_type='department')

    def validate_view_ticket(self, user, department, ticket, request):
        '''
        The method validates whether the ticket can be viewed by a specialist.
        
        Args:
            self: object
                An instance of the class that defines the method.
            user: User
                The user that is requesting to view the ticket.
            department: Department
                The department that belongs to that specialist user.
            ticket: QuerySet
                The query set containing the ticket be viewed.
            request: HttpRequest
                The HTTP request object that contains metadata about the request.
        Returns:
            response: HttpResponse
                A response containing the ticket data, or a redirect 
                to the specialist dashboard if the ticket cannot be viewed.
        '''
        if len(ticket) > 0 and department == ticket[0].department:
            message = Message.objects.filter(ticket=ticket.first()).first()
            return render(
                request,
                self.template_name,
                {
                    'ticket': ticket.first(),
                    'message': message,
                    'department_name': self.get_department().name,
                },
            )
        else:

            return redirect('specialist_dashboard', ticket_type='department')

    def get_department(self):
        '''
        Retrieve the department of the current specialist.
        
        Args:
            self: object
                An instance of the class that defines the method.
        Returns:
            department: Department 
                The department of the specialist, or an error message if the 
                department cannot be found.
        '''
        try:
            user = self.request.user
            department = (
                SpecialistDepartment.objects.filter(specialist=user).first()
            ).department
            return department
        except:
            return 'Department has not been found'