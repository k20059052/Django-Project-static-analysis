from ticketing.forms.edit_user import make_edit_user_form_class
from ticketing.models import User, Department
from ticketing import utility
from ticketing.utility import get
from ticketing.utility.get import get_user_from_id_param
from ticketing.utility import form_fields
from ticketing.views.utility.mixins import DynamicCustomFormClassMixin
from ticketing.models.users import User
from ticketing.mixins import RoleRequiredMixin

from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin


class EditUserView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    DynamicCustomFormClassMixin,
    UpdateView,
):
    required_roles = [User.Role.DIRECTOR]
    model = User
    # We will dynamically add the other fields (role, department) later, so they are missing from this list
    fields = ['email', 'first_name', 'last_name']
    success_url = reverse_lazy('director_panel')
    form_class_maker = make_edit_user_form_class

    def get_template_names(self):
        return ['director/edit_user.html']

    def post(self, request, *args, **kwargs):
        '''
        Process the post request
        
        Args:
            self: object
                An instance of the class that defines this method. 
            request: HttpRequest
                The request object sent by the client.
            *args: tuple
                Optional positional arguments passed to the parent method.
            **kwargs: dict
                Optional keyword arguments passed to the parent method.
        
        Returns:
            HttpResponse
                The response returned by the parent method for all other cases.     
        '''
        if request.POST.get('cancel'):
            return get.redirect_to_director_panel_with_saved_params(request)
        return super().post(request, *args, **kwargs)
