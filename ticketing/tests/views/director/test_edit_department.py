from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User, Department
from ticketing.tests.helpers import reverse_with_next
from ticketing.tests.utility import test_data
from ticketing.utility.user import *


def make_edit_department_query(name):
    return {'save': 'Save', 'name': name}


class EditDepartmentTestCase(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):

        self.specialist = User.objects.filter(role='SP').first()
        self.student = User.objects.filter(role='ST').first()
        self.director = User.objects.filter(role='DI').first()

        self.url = reverse(
            'edit_department',
            kwargs={'pk': Department.objects.all().first().id},
        )

        self.non_login_director = (
            User.objects.all()
            .exclude(id=self.director.id)
            .filter(role='DI')
            .first()
        )

    def test_get_edit_department_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_edit_department_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'director/edit_department.html')

    def test_get_edit_department_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_edit_department_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_get_edit_department_unused_pk(self):
        url = '587435983478/edit_department/'

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_get_edit_department_bad_pk(self):
        redirect_url = reverse_with_next('login', self.url)

        url = 'jhgudfhguudfsighihiu/edit_department/'

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_edit_department_good(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        department_id = Department.objects.all().first().id

        url = reverse('edit_department', kwargs={'pk': str(department_id)})

        query = make_edit_department_query(test_data.valid_department_names[0])

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('department_manager'),
            status_code=302,
            target_status_code=200,
        )

        department = get_department(department_id)

        self.assertEqual(department.name, test_data.valid_department_names[0])

    def test_edit_department_good_no_change(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        department_id = Department.objects.all().first().id

        url = reverse('edit_department', kwargs={'pk': str(department_id)})

        name = Department.objects.all().first().name

        query = make_edit_department_query(name)

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('department_manager'),
            status_code=302,
            target_status_code=200,
        )

        # print("ERRORS: ", response.context["form"].errors)

        department = get_department(department_id)

        self.assertEqual(department.name, name)

    def test_edit_department_bad_all(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        department = Department.objects.all().first()

        url = reverse('edit_department', kwargs={'pk': str(department.id)})

        name = department.name

        query = make_edit_department_query(
            test_data.invalid_department_names[0]
        )

        response = self.client.post(url, data=query)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(len(response.context['form'].errors) == 1)

        department = get_department(department.id)

        self.assertEqual(department.name, name)

    def test_cancel(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        query = {'cancel': 'Cancel'}

        response = self.client.post(self.url, data=query)

        self.assertRedirects(
            response,
            reverse('department_manager'),
            status_code=302,
            target_status_code=200,
        )
