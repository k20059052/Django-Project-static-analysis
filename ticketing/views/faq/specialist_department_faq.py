from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from ticketing.models.faq import FAQ
from ticketing.models.departments import Department
from ticketing.models.specialist import SpecialistDepartment
from ticketing.models.users import User
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin


class SpecialistDepartmentFaq(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = FAQ
    template_name = 'faq/specialist_department_faq.html'
    required_roles = ['SP', 'DI']
    paginate_by = 6
    context_object_name = 'faq_list'

    def get_queryset(self):
        '''
        Gets the QuerySet of FAQs of the currently logged in users Department.
        
        Args:
            self: object
                An instance of the class that defines this method.
                This is used to get the logged in user.
        Returns:
            queryset: QuerySet
                A queryset of all the FAQ objects that are of the logged in users Department.
        
        '''
        user = self.request.user
        department = SpecialistDepartment.objects.get(
            specialist=user
        ).department
        return FAQ.objects.filter(department=department)

    def get_context_data(self, **kwargs):
        '''
        Returns context dictionary for the template to be used.
        
        Args:
            self: object
                An instance of the class that defines this method.
                This is used to get the logged in user.
            **kwargs: dict
                Dictionary of keyword arguments:
                    -context['department_name']=department.name
        
        Returns:
            context: dict
                Context dictionery for the use of the template.
                
        '''
        context = super().get_context_data(**kwargs)
        user = self.request.user
        specialist_dept = SpecialistDepartment.objects.get(
            specialist=user
        ).department
        department = get_object_or_404(Department, name=specialist_dept)
        context['department_name'] = department.name
        return context
