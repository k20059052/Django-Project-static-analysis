from ticketing.models import User, Department

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ticketing.forms import *
from django.views.generic.edit import UpdateView
from ticketing.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class EditDepartmentView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    required_roles = [User.Role.DIRECTOR]
    model = Department
    fields = ['name']
    success_url = reverse_lazy('department_manager')

    def get_template_names(self):
        return ['director/edit_department.html']

    def post(self, request, *args, **kwargs):
        '''
        Handling the Http POST requests
        
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
            HttpResponseRedirect
                A redirect response to the 'department_manager' view if the 'cancel' button is pressed.
            HttpResponse
                The response returned by the parent method for all other cases.
        '''
        if request.POST.get('cancel'):
            return redirect('department_manager')
        return super().post(request, *args, **kwargs)
