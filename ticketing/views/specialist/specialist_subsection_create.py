from django.shortcuts import redirect, render
from django.views.generic import FormView
from ticketing.models.departments import Subsection
from ticketing.models.specialist import SpecialistDepartment
from ticketing.forms.subsection import SubsectionForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin
from django.urls import reverse, reverse_lazy

class SpecialistSubSectionView(LoginRequiredMixin, RoleRequiredMixin, FormView): 
    model = Subsection
    required_roles = ['SP']
    template_name = "specialist/create_subsection.html"
    form_class = SubsectionForm
    
    def form_valid(self, form):
        """
        Handles the form submission for creating a new subsection and performs additional logic to 
        associate the subsection with the department of the logged-in specialist user. If the form is 
        valid, it calls the `custom_save()` method of the form to save the new subsection and associate 
        it with the correct department. Finally, it redirects the user to the subsection manager view.

        Args:
            self (SpecialistSubSectionView): An instance of the `SpecialistSubSectionView` class that 
                defines the method.
            form (SubsectionForm): An instance of the form that was submitted.

        Returns:
            HttpResponseRedirect: A redirect to the subsection manager view if the form is valid and 
                the subsection is saved successfully.
        """
        form.custom_save(
            department=SpecialistDepartment.objects.get(
                specialist=self.request.user
            ).department,
            subsection_name=form.cleaned_data['name'],
        )
        return redirect('subsection_manager')