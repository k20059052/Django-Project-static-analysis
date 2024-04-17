from ticketing.models import User, Department
from ticketing.utility.error_messages import *
from ticketing.views.utility.mixins import ExtendableFormViewMixin, FilterView
from ticketing.forms.department import DepartmentFilterForm
from django.shortcuts import  redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.contrib import messages
from ticketing.forms import *
from django.views.generic.edit import CreateView
from ticketing.mixins import RoleRequiredMixin
from ticketing.utility.user import *
from django.contrib.auth.mixins import LoginRequiredMixin


def delete_department(id):
    """
    Delete a department object with the specified ID.

    Args:
       id:int
          The ID of the department you want to delete

    Returns:
        bool:
          Returns True if the department exists and is deleted successfully.
          Returns False if department  does not exist 
    """
    try:
        department = Department.objects.get(id=id)
        department.delete()
        return True
    except Department.DoesNotExist:
        return False


class DepartmentManagerView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    ExtendableFormViewMixin,
    FilterView,
    CreateView,
    ListView,
):
    required_roles = [User.Role.DIRECTOR]
    paginate_by = 10
    model = Department
    fields = ['name']
    success_url = reverse_lazy('department_manager')
    filter_form_class = DepartmentFilterForm
    filter_reset_url = 'department_manager'

    def get_queryset(self):
        '''
        Returns a filtered queryset of the Department Objects based on the provided filter
        
        Args:
            self: object
                An instance of the class that defines this method
            filter_data: dict
                A dictionary containing filter parameters for the queryset.
                The dictionary must contain the following:
                    -name: A string to filter the department by name (case-insensitive)
                    -id: An integer to filter departments by id
        Returns:
            departments: QuerySet
                A queryset of Department Objects that match the filter criteria.
                The queryset may be empty if no departments match the filter criteria.
        
        '''
        if self.filter_method == 'filter':
            departments = Department.objects.filter(
                name__istartswith=self.filter_data['name']
            )
        else:
            departments = Department.objects.filter(
                name__icontains=self.filter_data['name']
            )
        if self.filter_data['id']:
            departments = departments.filter(id__exact=self.filter_data['id'])
        return departments

    def post(self, request, *args, **kwargs):
        '''
        Handles HTTP POST requests for creating,editing, and deleting the Department objects.
        
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
            return super().post(request, *args, **kwargs)
        elif edit_id:
            response = redirect('edit_department', pk=edit_id)
            return response
        elif delete_id:
            result = delete_department(delete_id)
            if result == False:
                messages.add_message(
                    request, messages.ERROR, USER_NO_EXIST_MESSAGE
                )
        return self.fixed_post(request, *args, **kwargs)

    def get_template_names(self):
        return ['director/department_manager.html']
