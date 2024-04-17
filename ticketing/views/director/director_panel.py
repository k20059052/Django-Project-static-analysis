from ticketing.forms.director_panel import (
    DirectorFilterForm,
    DirectorCommandsForm,
    make_add_user_form_class,
)
from ticketing.models import User, Department, SpecialistDepartment
from ticketing.utility.error_messages import *
from ticketing.forms import SignupForm
from ticketing.views.utility.mixins import (
    ExtendableFormViewMixin,
    DynamicCustomFormClassMixin,
    FilterView,
)

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView
from ticketing.mixins import RoleRequiredMixin
from ticketing.utility.model import *
from ticketing.utility.user import *
from django.contrib.auth.mixins import LoginRequiredMixin


def set_multiple_users_role(users, user_role, department_id):
    '''
    Sets the role of multiple users for the specific department.
    
    Args:
        users: list of str
            A list of user IDs as strings to update the role for.
        user_role: str
            The new role to assign to the users.
        department_id: int 
            The ID of the department to update the users' roles for 
            
    Returns:
        bool
            True if all users' roles were successfully updated, False otherwise.
    '''
    problem_occured = False
    for user in users:
        try:
            id = int(user)
            user = User.objects.get(id=id)
            department = get_model_object(Department, id=department_id)
            update_specialist_department(
                user, user.role, user_role, department
            )
            # print("OLD ROLE: ", user.role, " NEW ROLE: ", user_role)
            user.role = user_role
            user.save()
        except User.DoesNotExist:
            problem_occured = True
        except ValueError:
            problem_occured = True
    return not problem_occured


def delete_users(user_id_strings):
    '''
    Deletes multiple users from the database.
    
    Args:
        user_id_strings: list of str
            A list of user IDs as strings to delete.
    
    Returns:
        bool 
            True if all users were successfully deleted, False otherwise
            
    '''
    problem_occured = False
    for id_str in user_id_strings:
        try:
            id = int(id_str)
            user = User.objects.get(id=id)
            if user.role == User.Role.SPECIALIST:
                delete_model_object(SpecialistDepartment, specialist=id)
            user.delete()
        except User.DoesNotExist:
            problem_occured = True
        except ValueError:
            problem_occured = True
    return not problem_occured


class DirectorPanelView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    ExtendableFormViewMixin,
    DynamicCustomFormClassMixin,
    FilterView,
    CreateView,
    ListView,
):

    required_roles = [User.Role.DIRECTOR]
    paginate_by = 10
    model = User
    form_class = SignupForm
    success_url = reverse_lazy('director_panel')
    form_class_maker = make_add_user_form_class
    filter_form_class = DirectorFilterForm
    filter_reset_url = 'director_panel'

    def setup(self, request):
        '''
        Initialises the view before processing the request.
        
        Args:
            self: object
                    An instance of the class that defines this method.
            request: HttpRequest
                The request object containing information about the request.
        
        Returns:
            None
        '''

        super().setup(request)
        self.error = False
        self.commands_form = None
        self.selected = []

    def get_queryset(self):
        '''
        Returns a filtered queryset of User objects filtered by a search criteria.
        
        Args:
            self: object
                An instance of the class that defines this method.
        
        Returns:
            users: QuerySet
                A quersyset of User objects filtered by the specific search criteria.

        '''

        if self.filter_method == 'filter':
            users = User.objects.filter(
                email__istartswith=self.filter_data['email'],
                first_name__istartswith=self.filter_data['first_name'],
                last_name__istartswith=self.filter_data['last_name'],
            )
        else:   # 'search'
            users = User.objects.filter(
                email__icontains=self.filter_data['email'],
                first_name__icontains=self.filter_data['first_name'],
                last_name__icontains=self.filter_data['last_name'],
            )

        if self.filter_data['id']:
            users = users.filter(id__exact=self.filter_data['id'])

        if self.filter_data['filter_role']:
            users = users.filter(role__exact=self.filter_data['filter_role'])

        if self.filter_data['filter_department']:
            users = users.filter(
                id__in=SpecialistDepartment.objects.filter(
                    department=self.filter_data['filter_department']
                ).values_list('specialist', flat=True)
            )

        return users

    def get_template_names(self):
        return ['director/director_panel.html']

    def get_context_data(self, *args, **kwargs):
        '''
        Returns a context dictionary for rendering the template.
        
        Args:
            self: object
                An instance of the class that defines this method.
            *args : tuple
                Positional arguments passed to the superclass's method.
            **kwargs : dict
                Keyword arguments passed to the superclass's method.
        
        Return:
            context: dict
                A dictionary of values to be used when rendering the template.
                
            
        '''
        context = super().get_context_data(*args, **kwargs)
        if self.commands_form == None:
            self.commands_form = DirectorCommandsForm()
        if self.error == False:
            self.selected = []
        context.update(
            {
                'commands_form': self.commands_form,
                'selected': self.selected,
                'departments': Department.objects.all(),
            }
        )
        return context

    def post(self, request):
        '''
        Process POST requests to perform actions on selected users.
        
        Args:
            self: object
                An instance of the class that defines this method.
            request: HttpRequest
                A HttpRequest object containg the user's request data.
            
        Returns:
            HttpResponse 
        
        Methods:
                - Call the parent class's `get` method using the request object.
                - Get the list of selected users from the request data.
                - Get the value of the `edit` key from the request data.
                - If `edit` is not None, redirect to the `edit_user` URL with the `edit_id` parameter set to the value of `edit`.
                - If the `add` key is present in the request data, call the parent class's `post` method and return its result.
                - If the `password` key is present in the request data, redirect to the `change_password` URL with the `change_id` parameter set to the value of `password`.
                - If no users are selected, set `self.error` to True, add an error message to the request's message framework, and call `self.fixed_post` with the request object.
                - If the `set_role` key is present in the request data, get the values of the `commands_role` and `commands_department` keys from the request data, and call `set_multiple_users_role` with the list of selected users, the role value, and the department value.
                - If `set_multiple_users_role` returns False, set `self.error` to True, add an error message to the request's message framework, and call `self.fixed_post` with the request object.
                - If the `delete` key is present in the request data, call `delete_users` with the list of selected users.
                - If `delete_users` returns False, set `self.error` to True, add an error message to the request's message framework, and call `self.fixed_post` with the request object.
                - Call `self.fixed_post` with the request object.
        '''

        super().get(request)
        self.selected = request.POST.getlist('select')
        edit_id = request.POST.get('edit')
        if edit_id:
            request.session['director_panel_query'] = request.GET.urlencode()
            response = redirect('edit_user', pk=edit_id)
            return response
        elif request.POST.get('add'):
            return super().post(request)
        elif request.POST.get('password'):
            change_id = request.POST.get('password')
            request.session['director_panel_query'] = request.GET.urlencode()
            response = redirect('change_password', pk=change_id)
            return response
        if len(self.selected) == 0:
            # Remaining possible POST requests rely on there being users selected
            self.error = True
            messages.add_message(
                request, messages.ERROR, 'No users have been selected'
            )
            return self.fixed_post(request)
        if request.POST.get('set_role'):
            role = request.POST.get('commands_role')
            department = request.POST.get('commands_department')
            self.commands_form = DirectorCommandsForm(request.POST)
            if not self.commands_form.is_valid():
                self.error = True
                messages.add_message(
                    request, messages.ERROR, 'Your command failed'
                )
                return self.fixed_post(request)
            elif not role:
                self.error = True
                messages.add_message(
                    request,
                    messages.ERROR,
                    'You have not selected a role for the user',
                )
                return self.fixed_post(request)
            if role != User.Role.SPECIALIST:
                department = None
            result = set_multiple_users_role(self.selected, role, department)
            if result == False:
                self.error = True
                messages.add_message(
                    request, messages.ERROR, USER_NO_EXIST_MESSAGE
                )
        elif request.POST.get('delete'):
            result = delete_users(self.selected)
            if result == False:
                self.error = True
                messages.add_message(
                    request, messages.ERROR, USER_NO_EXIST_MESSAGE
                )
        return self.fixed_post(request)
