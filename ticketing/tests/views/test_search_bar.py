from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from django.urls import reverse
from ticketing.models.users import User
from ticketing.models.departments import Department, Subsection
from ticketing.models.tickets import Ticket
from ticketing.models.faq import FAQ
from ticketing.models.specialist import SpecialistDepartment
from ticketing.views.specialist.specialist_subsection_create import SpecialistSubSectionView
from ticketing.tests.helpers import (
    FixtureHelpers,
    reverse_with_next,
    get_tickets,
)

class SerachBarViewTestCase(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
        'ticketing/tests/fixtures/subsection_fixtures.json',
        'ticketing/tests/fixtures/faq_fixtures.json'
    ]

    def setUp(self):
        self.specialist = FixtureHelpers.get_specialist_from_fixture()
        self.student = FixtureHelpers.get_student_from_fixture()
        self.director = FixtureHelpers.get_director_from_fixture()
        
        self.departments = FixtureHelpers.get_all_departments_from_fixture()
        self.subsectipns = FixtureHelpers.get_all_subsection_from_fixture()
        self.faqs = FixtureHelpers.get_all_faqs_from_fixture() 

        self.url = reverse(
            'home'
        )

        self.query = "Hello there"
    
    def test_search_bar_url(self):
        self.assertEqual(self.url, '/')

    def test_query(self):
        response = self.client.get(self.url, {'query' : self.query})
        department_list = response.context['top_departments'].keys()
        self.assertTrue(len(department_list) > 0)

    def test_top_departments_subset_all_departments(self):
        response = self.client.get(self.url, {'query' : self.query})
        department_list = response.context['top_departments'].keys()
        self.assertTrue(set(department_list) <= set(Department.objects.all().values_list('name', flat = True)))

    def test_top_subsection_subset_of_subsection_from_current_department(self):
        response = self.client.get(self.url, {'query' : self.query})
        department_id = list(response.context['top_departments'].values())[0]
        response = self.client.get(self.url, {'query' : self.query, 'department' : department_id})
        current_department = Department.objects.get(id = department_id)
        subections_from_current_department = Subsection.objects.filter(department=current_department).values_list('name', flat=True)
        subsection_list = response.context['top_subsections'].keys()
        self.assertTrue(set(subsection_list) <= set(subections_from_current_department))
        
    def test_top_FAQs_subset_of_FAQs_from_current_subsection(self):
        response = self.client.get(self.url, {'query' : self.query})
        department_id = list(response.context['top_departments'].values())[0]
        response = self.client.get(self.url, {'query' : self.query, 'department' : department_id})
        subsection_id = list(response.context['top_subsections'].values())[0]
        response = self.client.get(self.url, {'query' : self.query, 'subsection' : subsection_id})
        current_subsection = Subsection.objects.get(id=subsection_id)
        FAQ_from_current_subsection = FAQ.objects.filter(subsection=current_subsection).values_list('question', flat=True)
        questions_from_FAQ = response.context['top_FAQs'].keys()
        self.assertTrue(set(questions_from_FAQ) <= set(FAQ_from_current_subsection))

    """Run this to benchmark!"""
    # def test_is_department_present_in_top_three_department_score(self): 
    #     true_pos = 0
    #     num_of_question = 30
    #     question_department_dict = {}
    #     # true pos check
    #     for faq in FAQ.objects.all()[:num_of_question]:
    #         question_department_dict[faq.question] = faq.department 
    #     for question, department in question_department_dict.items(): 
    #         response = self.client.get(self.url, {'query' : question})
    #         department_ids = list(response.context['top_departments'].values())
    #         if department.id in department_ids: 
    #             true_pos = true_pos + 1
    #     print(f" Department present score : {true_pos/num_of_question}")