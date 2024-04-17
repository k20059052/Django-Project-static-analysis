from django.contrib.auth.decorators import login_required
from ticketing.decorators import roles_allowed
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from ticketing.models.faq import FAQ
from ticketing.models.departments import Department


class DepartmentFAQ(ListView):
    model = FAQ
    template_name = 'faq/department_faq.html'
    paginate_by = 25

    def get_queryset(self):
        '''
        Gets a QuerySet of FAQ objects filtered by department slug.
        
        Args:
            self: object
                An instance of the class that defines this method. 
        
        Returns:
            queryset: QuerySet
                A QuerySet of FAQ objects sorted by question in ascending order.
        
        '''
        queryset = FAQ.objects.filter(
            department__slug=self.kwargs['department']
        )
        queryset = queryset.order_by('question')
        return queryset

    def get_context_data(self, **kwargs):
        '''
        Adds additional context data to the template context.
        
        Args:
            self: object
                An instance of the class that defines this method.
            **kwargs: dict
                A dictionary of keyword arguments:
                    -context['department_name']=department.name.
                    -context['faq_dict']=faq_dict where faq_dict[{subsection}]=[faq].
        Returns:
            context: dict
                A dictionary of context data.
        '''
        context = super().get_context_data(**kwargs)
        department = get_object_or_404(
            Department, slug=self.kwargs['department']
        )
        if department:
             context['department_name'] = department.name
        else:
            context['department_name']=''
        faqs=FAQ.objects.filter(department=department)
        faq_dict={}
        for faq in faqs:
            if faq.subsection not in faq_dict:
                faq_dict[faq.subsection]=[]
            faq_dict[faq.subsection].append(faq)
        context['faq_dict']=faq_dict
        return context
