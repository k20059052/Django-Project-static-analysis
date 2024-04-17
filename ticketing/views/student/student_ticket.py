from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from django.urls import reverse_lazy, reverse
from ticketing.forms import StudentTicketForm
from ticketing.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin


class StudentTicketView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    template_name = 'student/student_ticket_form.html'
    required_roles = ['ST']
    form_class = StudentTicketForm
    success_url = reverse_lazy('student_dashboard')

    def form_valid(self, form):
        '''
        Override the form_valid method to create a new ticket object
        and save it to the database with the data submitted through the form.
        Redirect to the success URL on successful form submission.

        Args:
            self: object
                An instance of the class where the method is defined.
            form : forms.Form
                A form instance that is validated by Django's form validation system.
        Returns:
            HttpResponseRedirect
                A redirection response to the success URL.
        '''
        student = User.objects.get(id=self.request.user.id)
        form.custom_save(
            student=student,
            department=form.cleaned_data['department'],
            header=form.cleaned_data['header'],
            content=form.cleaned_data['content'],
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, **kwargs):
        return self.render_to_response(self.get_context_data())
