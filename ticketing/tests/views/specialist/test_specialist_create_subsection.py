from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from django.urls import reverse
from ticketing.forms.subsection import SubsectionForm
from ticketing.models.users import User
from ticketing.models.departments import Department, Subsection
from ticketing.models.specialist import SpecialistDepartment
from ticketing.views.specialist.specialist_subsection_create import SpecialistSubSectionView

class SpecialistSubSectionViewTest(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]
    def setUp(self):
        self.url = reverse('create_subsection')
        self.factory = RequestFactory()

        self.specialist = User.objects.filter(role='SP').first()
        self.student = User.objects.filter(role='ST').first()
        self.director = User.objects.filter(role='DI').first()
        
        self.department = SpecialistDepartment.objects.filter(
            specialist=self.specialist
        ).first().department
        
        self.subsection = Subsection.objects.create(
            name='Updated Pain', department=self.department
        )
        self.data = {
            'name' : 'Science'
        }

    def test_valid_url(self):
        self.assertEqual(self.url, '/create_subsection/')
    
    def test_invalid_loging(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_valid_post(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url, follow=True)
        before_count = Subsection.objects.filter(department = self.department).count()
        response = self.client.post(
            self.url, 
            data=self.data,
            follow=True
        )
        self.assertEquals(Subsection.objects.filter(department = self.department).count(), before_count + 1)
        self.assertTemplateUsed(response, 'specialist/subsection_manager.html')