from ticketing.utility.user import *
from ticketing.utility.error_messages import *
from ticketing.models import User, Subsection, SpecialistDepartment
from ticketing.mixins import RoleRequiredMixin
from ticketing.forms.subsection import SubsectionForm

from django.shortcuts import  redirect, render
from django.urls import reverse_lazy
from ticketing.views.utility.mixins import ExtendableFormViewMixin
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class SubsectionManagerView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    ExtendableFormViewMixin,
    ListView, 
    CreateView
):
    template_name = 'specialist/subsection_manager.html'
    required_roles = [User.Role.SPECIALIST]
    model = Subsection
    fields = ['name']
    
    def get_context_data(self, **kwargs):
        """
        Adds extra context data to the template context for rendering the subsection manager page. 
        This method retrieves the department associated with the logged-in specialist user and 
        filters the subsections to only include those belonging to that department.

        Args:
            self (SubsectionManagerView): An instance of the `SubsectionManagerView` class that defines 
                the method.
            **kwargs: Additional keyword arguments to be passed to the superclass method.

        Returns:
            dict: A dictionary containing the extra context data to be passed to the template, including 
                a filtered list of subsections for the logged-in specialist user's department.
        """
        context = {}
        specialist_department = SpecialistDepartment.objects.get(
            specialist=self.request.user
        ).department
        context['subsections'] = Subsection.objects.filter(
            department = specialist_department
        )
        return context
    
    def post(self, request, *args, **kwargs):
        '''
        Handles HTTP POST requests for creating,editing, and deleting the Subsections objects.
        Args:
            self: object
                An instance of the class that defines the method
            request: HttpRequest
                The HTTP request object containing the form data
            *args: tuple
                Positional arguments passed to method
            **kwargs: dict
                Keyword arguments passed to the method
        Returns:
            HttpResponse
                The HTTP response object to return to the client
        '''
        super().get(request)
        edit_id = request.POST.get('edit')
        delete_id = request.POST.get('delete')
        if request.POST.get('add'):
            return redirect("create_subsection")
        elif edit_id:
            response = redirect('edit_subsection', pk=edit_id)
            return response
        elif delete_id:
            Subsection.objects.filter(id = delete_id).delete()
        context = self.get_context_data()
        return render(request, self.template_name, context)