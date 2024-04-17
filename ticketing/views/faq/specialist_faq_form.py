from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.http import HttpResponseRedirect
from ticketing.forms.specialist_faq import FAQForm
from django.urls import reverse_lazy
from ticketing.models.specialist import SpecialistDepartment
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin


class FAQFormView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    template_name = 'faq/faq_specialist_form.html'
    required_roles = ['SP', 'DI']
    form_class = FAQForm
    success_url = reverse_lazy('check_faq')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        specialist_department = SpecialistDepartment.objects.get(
            specialist=self.request.user
        )
        kwargs['department'] = specialist_department.department
        return kwargs

    def form_valid(self, form):
        '''
        Overrides the form_valid method from Django's FormView to
        create and save a new FAQ  instance using the the data submitted
        in the previous form (Adding FAQ).
        
        Args:
            self: object
                An instance of the class that defines this method.
                This is used to get the logged in user.
            form: ModelForm
                A ModelForm instance containing the data submitted in the form.
        Returns:
            HttpResponseRedirect
                A HTTP response that redirects the user to the success
                URL specified by get_success_url()

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
        return HttpResponseRedirect(self.get_success_url())
