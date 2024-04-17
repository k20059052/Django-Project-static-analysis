from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User
from ticketing.tests.helpers import reverse_with_next
from ticketing.tests.utility import test_data
from ticketing.utility.user import *
from django.contrib.auth import authenticate


def make_change_password_query(password, confirm_password):
    return {
        'change': 'Change',
        'password': password,
        'confirm_password': confirm_password,
    }


class ChangePasswordTestCase(TestCase):

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

        self.second_student = (
            User.objects.all()
            .exclude(id=self.student.id)
            .filter(role='DI')
            .first()
        )

        self.url = reverse(
            'change_password', kwargs={'pk': str(self.second_student.id)}
        )

        self.non_login_director = (
            User.objects.all()
            .exclude(id=self.director.id)
            .filter(role='DI')
            .first()
        )

    def test_get_change_password_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_change_password_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/change_password.html')

    def test_get_change_password_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_change_password_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_get_change_password_unused_pk(self):
        redirect_url = reverse_with_next('login', self.url)

        url = reverse('change_password', kwargs={'pk': '587435983478'})

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_get_change_password_bad_pk(self):
        redirect_url = reverse_with_next('login', self.url)

        url = reverse('change_password', kwargs={'pk': 'jhgudfhguudfsighihiu'})

        response = self.client.get(url, follow=True)

        self.assertEquals(response.status_code, 404)

    def test_get_change_password_non_director_same_user(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        url = reverse('change_password', kwargs={'pk': str(self.student.id)})

        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/change_password.html')

    def test_change_password_good(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('change_password', kwargs={'pk': str(self.student.id)})

        query = make_change_password_query(
            test_data.valid_passwords[0], test_data.valid_passwords[0]
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
        authenticated_user = authenticate(
            email=user.email, password=test_data.valid_passwords[0]
        )

        self.assertEqual(authenticated_user, user)

    def test_change_password_bad_all(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('change_password', kwargs={'pk': str(self.student.id)})

        query = make_change_password_query(
            test_data.invalid_passwords[2], test_data.invalid_passwords[2]
        )

        response = self.client.post(url, data=query)

        # print("ERRORS: ", response.context["form"].errors)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(len(response.context['form'].errors) == 1)

    def test_change_passwords_no_match(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        url = reverse('change_password', kwargs={'pk': str(self.student.id)})

        query = make_change_password_query(
            test_data.valid_passwords[0], test_data.valid_passwords[1]
        )

        response = self.client.post(url, data=query)

        self.assertEquals(response.status_code, 200)

        self.assertTrue(len(response.context['form'].errors) == 1)

    def test_bad_post(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        response = self.client.post(self.url, data={'gjdifiojd': 'jgijhjoi'})

        self.assertEquals(response.status_code, 200)

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
