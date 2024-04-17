from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from ticketing.models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
import copy


class StudentInboxView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Ticket
    template_name = 'student/student_dashboard.html'
    paginate_by = 5  # if pagination is desired
    required_roles = ['ST']

    def get_queryset(self):
        '''
        Returns a queryset of tickets filtered by the current user and their selected ticket type.

        If the request method is GET, it returns all tickets from that user.
        If the request method is POST, it filters tickets based on the selected ticket type.
        Args:
            self: object
                An instance of the class that defines the method.
        Returns:
            tickets: QuerySet 
                A queryset of tickets filtered by the current user and their selected ticket type.
        '''
        tickets = Ticket.objects.filter(student_id=self.request.user.id)
        if self.request.method == 'GET':   # Gets all tickets from that user
            return tickets

        if self.request.method == 'POST':
            ticket_type = self.request.POST.get('type_of_ticket')
            match ticket_type:
                case 'Open':
                    return tickets.filter(status='Open')
                case 'Closed':
                    return tickets.filter(status='Closed')
                case default:
                    return tickets.none()

    def get_context_data(self, **kwargs):
        '''
        Adds the selected type of ticket to the context data.
        
        Args:
            self: object
                An instance of the class that defines the method.
            **kwargs: dict
                Keyword arguments passed to the view.
        Returns:
            context: dict
                The context data containing the selected type of ticket:
                    -context['type_of_ticket']=ticket_type
        '''
        context = super().get_context_data(**kwargs)
        ticket_type = ''
        if self.request.method == 'POST':
            ticket_type = self.request.POST.get('type_of_ticket')

        context['type_of_ticket'] = ticket_type
        return context

    def post(self, request, *args, **kwargs):
        '''
        Handle HTTP POST requests.
        Sets the page to 1 and updates the queryset based on the type of ticket selected.
        Renders the student_dashboard.html template with the updated context.

        Args:
            request : HttpRequest
                The HTTP request object.
            *args
                Variable length argument list.
            **kwargs
                Arbitrary keyword arguments.
        Returns:
            HttpResponse
                The HTTP response object with the updated context:
                    -context['page_obj']=self.queryset() //Messages queryset
                    -context['type_of_ticket']=self.request.POST.get('type_of_ticket')// e.g. 'personal'
        '''

        if "view" in request.POST:
            ticket = Ticket.objects.filter(id = request.POST["view"]).first()
            if ticket.status == Ticket.Status.OPEN:
                return redirect(reverse("student_message", kwargs={"pk": ticket.id}))
            
            elif ticket.status == Ticket.Status.CLOSED:
                return redirect(reverse("archived_ticket", kwargs={"pk": ticket.id}))

        
        # request.GET["page"] = 1
        get_copy = copy.copy(request.GET)
        get_copy['page'] = 1
        request.GET = get_copy
        context = {
            'page_obj': self.get_queryset(),
            'type_of_ticket': self.request.POST.get('type_of_ticket'),
        }
        context.update(super().get(request).context_data)
        return render(request, 'student/student_dashboard.html', context)
