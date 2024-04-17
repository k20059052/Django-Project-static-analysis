from django.views.generic import TemplateView, ListView
from ticketing.nlp import ml_api
from ticketing.models import Department, FAQ
from ticketing.models.departments import Subsection
from django.contrib import messages 

class SearchBarView(TemplateView):
    template_name = 'index.html' 
    
    # handles the data
    def get_context_data(self, **kwargs):
        """
        Returns a dictionary of context data to be used in the template rendering process.

        Keyword Arguments:
        **kwargs -- additional keyword arguments that may be passed to the function.

        Returns:
        context -- a dictionary containing the context data for the template.
        """
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        department_id = self.request.GET.get('department')
        subsection_id = self.request.GET.get('subsection')
        
        # will return the top departments
        if query and not subsection_id and not department_id:
            department_dict = self.rank_departments(self.request, query, result_size=3)
            context['top_departments'] = department_dict
            context['query'] = query

        # will return the top subsections
        if department_id and not subsection_id:
            subsection_dict = self.rank_subsections(self.request, query, department_id, result_size=3)
            context['top_subsections'] = subsection_dict
            context['query'] = query

        # will return the top FAQs
        if subsection_id and not department_id:
            faqs = self.rank_faqs(self.request, query, subsection_id, result_size=8)
            context['top_FAQs'] = faqs
        return context
    
    def rank_items(self, request, query, model, queryset, result_size, faq_rank = False):
        """
        Ranks the items in the given queryset based on their similarity to the given query
        using the ML model provided. Returns a dictionary containing the names of the top
        ranking items and their corresponding IDs (if not FAQ items) or answers (if FAQ items).

        Args:
            request (HttpRequest): The HTTP request object.
            query (str): The search query string.
            model (object): The machine learning model to use for ranking items.
            queryset (QuerySet): The queryset containing the items to rank.
            result_size (int): The maximum number of top ranking items to return.
            faq_rank (bool, optional): Indicates whether the queryset contains FAQ items or not.
                Defaults to False.

        Returns:
            dict: A dictionary containing the names of the top ranking items and their
                corresponding IDs or answers.
        """
        items = queryset.all()
        if(not faq_rank):
            item_names = [item.name for item in items]
        else: 
            item_names = [item.question for item in items]
        item_dict = {}
        item_name_chunks = [item_names[i:i+10] for i in range(0, len(item_names), 10)]
        
        # try the api call!
        try:
            for item_name_chunk in item_name_chunks:
                data = model.get_data(query, item_name_chunk)
                for i in range(0, len(data['scores'])):
                    item_name = data['labels'][i]
                    item_dict[item_name] = data['scores'][i]
        except Exception as e:
                messages.error(request, "Please use FAQs or open a ticket, currently this service is down.")

        item_dict = dict(sorted(item_dict.items(), key=lambda x: x[1], reverse=True)[:result_size])
        if(not faq_rank):
            item_dict = {key: items.get(name=key).id for key in item_dict.keys()}
        else:
            item_dict = {key: items.get(question=key).answer for key in item_dict.keys()}
        return item_dict

    def rank_departments(self,request, query, result_size: int):
        """
        Ranks the departments in the database based on their similarity to the given query.
        Returns a dictionary containing the names of the top ranking departments and their IDs.

        Args:
            request (HttpRequest): The HTTP request object.
            query (str): The search query string.
            result_size (int): The maximum number of top ranking departments to return.

        Returns:
            dict: A dictionary containing the names of the top ranking departments and their IDs.
        """
        departments = Department.objects.all()
        return self.rank_items(request, query, ml_api, departments, result_size)

    def rank_subsections(self,request, query, department_id: int, result_size: int):
        """
        Ranks the subsections in the given department based on their similarity to the given query.
        Returns a dictionary containing the names of the top ranking subsections and their IDs.

        Args:
            request (HttpRequest): The HTTP request object.
            query (str): The search query string.
            department_id (int): The ID of the department to search within.
            result_size (int): The maximum number of top ranking subsections to return.

        Returns:
            dict: A dictionary containing the names of the top ranking subsections and their IDs.
        """
        
        department_obj = Department.objects.get(id=department_id)
        subsections = Subsection.objects.filter(department=department_obj)
        return self.rank_items(request, query, ml_api, subsections, result_size)

    def rank_faqs(self,request, query, subsection_id: int, result_size: int):
        """
        Ranks the FAQs in the given subsection based on their similarity to the given query.
        Returns a dictionary containing the questions of the top ranking FAQs and their answers.

        Args:
            request (HttpRequest): The HTTP request object.
            query (str): The search query string.
            subsection_id (int): The ID of the subsection to search within.
            result_size (int): The maximum number of top ranking FAQs to return.

        Returns:
            dict: A dictionary containing the questions of the top ranking FAQs and their answers.
        """
        faqs = FAQ.objects.filter(subsection_id=subsection_id)
        faq_questions = [faq.question for faq in faqs]
        return self.rank_items(request, query, ml_api, faqs, result_size, faq_rank=True)



