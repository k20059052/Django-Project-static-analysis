from ticketing.models.departments import Subsection
from ticketing.models.specialist import SpecialistDepartment
from ticketing.models.users import User
from ticketing.forms.subsection import SubsectionForm
from ticketing.mixins import RoleRequiredMixin

from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin


class EditSubsectionView(LoginRequiredMixin, RoleRequiredMixin, UpdateView): 
    model = Subsection
    required_roles = [User.Role.SPECIALIST]
    template_name = "specialist/edit_subsection.html"
    form_class = SubsectionForm
    success_url = reverse_lazy('subsection_manager')
    
    def post(self, request, *args, **kwargs):
        """
        Handles HTTP POST requests for updating a subsection object. If the user clicks the cancel button,
        it redirects back to the subsection manager page. Otherwise, it calls the superclass `post()` 
        method to handle the form submission and update the subsection object.

        Args:
            self (EditSubsectionView): An instance of the `EditSubsectionView` class that defines the method.
            request (HttpRequest): The HTTP request object containing the form data.
            *args: Any additional positional arguments passed to the method.
            **kwargs: Any additional keyword arguments passed to the method.

        Returns:
            HttpResponseRedirect: A redirect to the subsection manager page if the user clicked the cancel 
                button, or the result of the superclass `post()` method if the form was submitted successfully.
        """
        if request.POST.get('cancel'):
            return redirect('subsection_manager')
        return super().post(request, *args, **kwargs)
    
