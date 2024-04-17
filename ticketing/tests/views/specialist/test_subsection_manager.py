from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from django.urls import reverse

from ticketing.models import SpecialistDepartment, User, Subsection
from ticketing.views.specialist import subsection_manager


class SubsectionManagerViewTest(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
        'ticketing/tests/fixtures/subsection_fixtures.json',
    ]

    def setUp(self):
        self.specialist = User.objects.filter(role = 'SP').first()
        self.department = SpecialistDepartment.objects.get(specialist = self.specialist).department
        self.subsection_names = Subsection.objects.filter(department = self.department).values_list('name', flat=True)
        self.subsection_id = Subsection.objects.filter(department = self.department).first().id 
        self.url = reverse('subsection_manager')

    def test_subsection_manager_url(self):
        self.assertEqual(self.url, '/subsection_manager/')

    def test_get_is_successful(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialist/subsection_manager.html')

    def test_get_contains_subsections(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url)
        subsection_queryset = response.context['subsections'].values_list('name', flat = True)
        self.assertTrue(set(self.subsection_names)  <= set(subsection_queryset))

    def test_post_with_delete_id(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        before_count_of_subsection = Subsection.objects.count()
        response = self.client.post(self.url, {'delete': self.subsection_id})
        after_count_of_subestion = Subsection.objects.count()
        self.assertEqual(before_count_of_subsection, after_count_of_subestion + 1)

    def test_post_redirect_when_edit_id(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(self.url, {'edit' : self.subsection_id}, follow=True)
        self.assertTemplateUsed(response, 'specialist/edit_subsection.html')
        self.assertTemplateNotUsed(response, 'specialist/subsection_manager.html')
        

    def test_port_redirect_when_adding_subsection(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(self.url, {'add' : True}, follow=True)
        self.assertTemplateUsed(response, 'specialist/create_subsection.html')
        self.assertTemplateNotUsed(response, 'specialist/subsection_manager.html')