from ticketing.mixins import RoleRequiredMixin
from ticketing.models import Message, Ticket, StudentMessage, SpecialistMessage, SpecialistInbox
from django.views.generic import DetailView, ListView, CreateView
from itertools import chain
from django.shortcuts import redirect
from operator import attrgetter
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class StudentMessageView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = StudentMessage
    template_name = 'student/student_message.html'
    fields = ['content']
    required_roles = ['ST', 'SP']

    def dispatch(self, request, *args, **kwargs):
        '''
        Checks if the current user is allowed to access a particular ticket based on their specialist department. If the user
        is not allowed to access the ticket, they are redirected to the specialist dashboard page. Otherwise, the method calls
        the `dispatch` method of the superclass to continue with the usual view dispatching process.

        Args:
            self: object
                An instance of the class that defines the object.
            request: HttpRequest
                The request object sent by the client.
            *args: tuple
                Positional arguments passed to the view.
            **kwargs: dict
                Keyword arguments passed to the view.
        Returns:
            HttpResponse
                The HTTP response object returned by the view.
        '''
        if request.method == "POST":
            if "view" in request.POST:
                ticket = Ticket.objects.filter(id = request.POST["view"]).first()
                ticket.status = Ticket.Status.CLOSED
                ticket.save()
                SpecialistInbox.objects.filter(ticket = ticket).delete()
                return redirect(reverse("student_inbox"))
        allowed_ids = []
        # TODO move this to a helper class
        allowed_ids.append(
            getattr(
                getattr(Ticket.objects.get(id=self.kwargs['pk']), 'student'),
                'id',
            )
        )
        if self.request.user.id not in allowed_ids:
            return HttpResponseRedirect(reverse('student_dashboard'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        Called when a valid form is submitted. Creates a new `TicketResponse` object and associates it with a specific ticket
        based on the `pk` keyword argument in the URL. Sets the `responder` attribute of the response object to the current
        user and saves the object. Finally, redirects the user to the same page to display the newly added response.

        Args:
            self: object
                An instance of the class that defines the method.
            form : forms.Form
                The form object that was submitted by the user.
        Returns:
            HttpResponseRedirect
                The HTTP response object to redirect the user to the same page to display the newly added response.
        '''
        self.object = form.save(commit=False)
        self.object.ticket = Ticket.objects.get(id=self.kwargs['pk'])
        self.object.save()
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        '''
        Returns a dictionary of context data for rendering the template.

        Args:
            self: object 
                An instance of the class that defines the method.
            **kwargs: dict
                A dictionary of keyword arguments.
        Returns:
            context: dict
                A dictionary of context data.
        '''
        context = super().get_context_data(**kwargs)
        context['ticket'] = Ticket.objects.get(id=self.kwargs['pk'])
        student_message = StudentMessage.objects.filter(
            ticket=self.kwargs['pk']
        )
        specialist_message = SpecialistMessage.objects.filter(
            ticket=self.kwargs['pk']
        )
        context['message_list'] = sorted(
            chain(student_message, specialist_message),
            key=attrgetter('date_time'),
        )
        return context

    def get_form(self, form_class=None):
        '''
        Returns an instance of the form to be used in the view.
        
        Args:
            self: object
                An instance of the class that defines the method.
            form_class: class
                The form class can be used in the view (default: None).
        Returns:
            form: object
                An instance of the form to be used in the view, with modified
                label and widget attributes.  
        '''
        form = super().get_form(form_class=form_class)
        form.fields['content'].label = ''
        form.fields['content'].widget.attrs.update(
            {
                'class': 'form-control',
                'rows': 8,
                'style': 'resize: none;',
                'placeholder': 'Enter your message here',
            }
        )
        return form
