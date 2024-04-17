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
        self.url = reverse('edit_subsection', kwargs={'pk':self.subsection_id})
        self.data = {
            'name' : 'RAndomasdf'
        }

    def test_edit_subsection_url(self):
        self.assertEqual(self.url, f'/edit_subsection/{self.subsection_id}/')

    def test_get(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialist/edit_subsection.html')

    def test_valid_subsection_form(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        name_before = Subsection.objects.get(id = self.subsection_id).name
        response = self.client.post(self.url, data=self.data, follow=True)
        name_after = Subsection.objects.get(id = self.subsection_id).name
        self.assertNotEqual(name_before, name_after)


    def test_invalid_subsection_form(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        self.data['name'] = 234
        name_before = Subsection.objects.get(id = self.subsection_id).name
        response = self.client.post(self.url, data=self.data, follow=True)
        name_after = Subsection.objects.get(id = self.subsection_id).name
        self.assertEqual(name_before, name_after)
        self.assertTemplateUsed(response, 'specialist/edit_subsection.html')

    def test_redirects_successfully_to_correct_page(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(self.url, data=self.data, follow=True)
        self.assertTemplateUsed(response, 'specialist/subsection_manager.html')
        self.assertTemplateNotUsed(response, 'specialist/edit_subsection.html')

    def test_post_when_cancel_redirects(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(self.url, {'cancel' : True}, follow=True)
        self.assertTemplateUsed(response, 'specialist/subsection_manager.html')
        self.assertTemplateNotUsed(response, 'specialist/edit_subsection.html')