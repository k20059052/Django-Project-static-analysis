from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User, Department
from ticketing.tests.helpers import reverse_with_next
from ticketing.tests.utility import test_data
from ticketing.utility.user import *


def make_edit_user_query(email, first_name, last_name, role, department):
    return {
        'save': 'Save',
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'edit_role': role,
        'edit_department': department,
    }


class EditUserTestCase(TestCase):

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

        self.url = reverse('edit_user', kwargs={'pk': str(self.student.id)})

        self.non_login_director = (
            User.objects.all()
            .exclude(id=self.director.id)
            .filter(role='DI')
            .first()
        )

    def test_get_edit_user_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_edit_user_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'director/edit_user.html')

    def test_get_edit_user_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_edit_user_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_get_edit_user_unused_pk(self):

        url = '587435983478/edit_user/'

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_get_edit_user_bad_pk(self):

        url = 'jhgudfhguudfsighihiu/edit_user/'

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_edit_user_good(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.student.id)})

        query = make_edit_user_query(
            test_data.valid_emails[0],
            test_data.valid_first_names[0],
            test_data.valid_last_names[0],
            User.Role.DIRECTOR,
            '',
        )

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('director_panel'),
            status_code=302,
            target_status_code=200,
        )

        user = get_user(self.student.id)

        self.assertEqual(user.email, test_data.valid_emails[0])
        self.assertEqual(user.first_name, test_data.valid_first_names[0])
        self.assertEqual(user.last_name, test_data.valid_last_names[0])
        self.assertEqual(user.role, User.Role.DIRECTOR)
        self.assertEqual(get_user_department(user), None)

    def test_edit_user_good_no_change(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.specialist.id)})

        email = self.specialist.email
        first_name = self.specialist.first_name
        last_name = self.specialist.last_name
        role = self.specialist.role
        department = get_user_department(self.specialist)

        query = make_edit_user_query(
            email, first_name, last_name, role, str(department.id)
        )

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('director_panel'),
            status_code=302,
            target_status_code=200,
        )

        # print("ERRORS: ", response.context["form"].errors)

        user = get_user(self.specialist.id)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.role, role)
        self.assertEqual(get_user_department(user), department)

    def test_edit_user_good_department(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.student.id)})

        query = make_edit_user_query(
            test_data.valid_emails[0],
            test_data.valid_first_names[0],
            test_data.valid_last_names[0],
            User.Role.SPECIALIST,
            str(Department.objects.all().first().id),
        )

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('director_panel'),
            status_code=302,
            target_status_code=200,
        )

        # print("ERRORS: ", response.context["form"].errors)

        user = get_user(self.student.id)

        self.assertEqual(user.email, test_data.valid_emails[0])
        self.assertEqual(user.first_name, test_data.valid_first_names[0])
        self.assertEqual(user.last_name, test_data.valid_last_names[0])
        self.assertEqual(user.role, User.Role.SPECIALIST)
        self.assertEqual(
            get_user_department(user), Department.objects.all().first()
        )

    def test_edit_user_change_department(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.specialist.id)})

        email = self.specialist.email
        first_name = self.specialist.first_name
        last_name = self.specialist.last_name
        role = self.specialist.role
        department = get_user_department(self.specialist)

        added_department = Department.objects.create(
            name='u489789789fyrehiogjhreaiuog8o'
        )

        query = make_edit_user_query(
            email, first_name, last_name, role, str(added_department.id)
        )

        response = self.client.post(url, data=query)

        self.assertRedirects(
            response,
            reverse('director_panel'),
            status_code=302,
            target_status_code=200,
        )

        # print("ERRORS: ", response.context["form"].errors)

        user = get_user(self.specialist.id)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.role, role)
        self.assertEqual(get_user_department(user), added_department)

    def test_edit_user_bad_all(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.student.id)})

        email = self.student.email
        first_name = self.student.first_name
        last_name = self.student.last_name
        role = self.student.role
        department = get_user_department(self.student)

        added_department = Department.objects.create(
            name='u489789789fyrehiogjhreaiuog8o'
        )

        query = make_edit_user_query(
            test_data.invalid_emails[0],
            test_data.invalid_first_names[0],
            test_data.invalid_last_names[0],
            test_data.invalid_roles[0],
            'jfisofjiosfuioufoisuio5u874583979uopks£%',
        )

        response = self.client.post(url, data=query)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(len(response.context['form'].errors) == 4)

        user = get_user(self.student.id)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.role, role)
        self.assertEqual(get_user_department(user), department)

    def test_edit_user_bad_department(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('edit_user', kwargs={'pk': str(self.specialist.id)})

        email = self.specialist.email
        first_name = self.specialist.first_name
        last_name = self.specialist.last_name
        role = self.specialist.role
        department = get_user_department(self.specialist)

        added_department = Department.objects.create(
            name='u489789789fyrehiogjhreaiuog8o'
        )

        query = make_edit_user_query(
            email,
            first_name,
            last_name,
            role,
            'jfisofjiosfuioufoisuio5u874583979uopks£%',
        )

        response = self.client.post(url, data=query)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(len(response.context['form'].errors) == 1)

        user = get_user(self.specialist.id)

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.role, role)
        self.assertEqual(get_user_department(user), department)

    def test_cancel(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        query = {'cancel': 'Cancel'}

        response = self.client.post(self.url, data=query)

        self.assertRedirects(
            response,
            reverse('director_panel'),
            status_code=302,
            target_status_code=200,
        )
