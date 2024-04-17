from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.http import HttpResponseRedirect
from ticketing.forms.specialist_faq import FAQForm
from django.urls import reverse, reverse_lazy
from ticketing.models.faq import FAQ
from ticketing.models.specialist import SpecialistDepartment
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
from django.views.generic.edit import UpdateView


class FAQUpdateFormView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    template_name = 'faq/faq_update.html'
    required_roles = ['SP', 'DI']
    form_class = FAQForm
    success_url = reverse_lazy('home')
    model = FAQ

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        specialist_department = SpecialistDepartment.objects.get(specialist=self.request.user)
        kwargs['department'] = specialist_department.department
        return kwargs
    
    def form_valid(self, form):
        '''
        Update a specific FAQ object that has already been 
        created (Updating FAQ).
        
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
        form.save()
        return redirect('specialist_department_faq')
