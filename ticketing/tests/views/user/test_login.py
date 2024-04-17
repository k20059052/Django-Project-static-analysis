from django.test import TestCase
from ticketing.forms import LoginForm
from django.urls import reverse
from ticketing.models import User
from ticketing.tests.helpers import LogInTester


class LoginViewTestCase(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse('login')
        User.objects.create_user(
            email='johndoe@example.com',
            first_name='John',
            last_name='Doe',
            password='Password123',
        )
        User.objects.create_specialist(
            email='janedoe@example.com',
            first_name='Jane',
            last_name='Doe',
            password='Password123',
        )
        User.objects.create_director(
            email='director@example.com',
            first_name='Director',
            last_name='Doe',
            password='Password123',
        )

    def test_log_in_url(self):
        self.assertEqual(self.url, '/login/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_log_in(self):
        form_input = {
            'email': 'johndoe@example.com',
            'password': '123Password',
        }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_email(self):
        form_input = {'email': '', 'password': 'Password1234'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_password(self):
        form_input = {'username': 'johndoe@example.com', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LoginForm))
        self.assertFalse(self._is_logged_in())

    def test_successful_student_log_in(self):
        form_input = {
            'username': 'johndoe@example.com',
            'password': 'Password123',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('student_dashboard')
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'student/student_dashboard.html')

    def test_successful_specialist_log_in(self):
        form_input = {
            'username': 'janedoe@example.com',
            'password': 'Password123',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse(
            'specialist_dashboard', kwargs={'ticket_type': 'personal'}
        )
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    def test_successful_director_log_in(self):
        form_input = {
            'username': 'director@example.com',
            'password': 'Password123',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('director_panel')
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'director/director_panel.html')

    def test_get_log_in_redirects_when_logged_in(self):
        form_input = {
            'username': 'director@example.com',
            'password': 'Password123',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('director_panel')
        response2 = self.client.get(self.url)
        self.assertRedirects(response, response_url)

    def test_post_log_in_redirects_when_logged_in(self):
        form_input = {
            'username': 'director@example.com',
            'password': 'Password123',
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('director_panel')
        response2 = self.client.post(self.url, form_input, follow=True)
        self.assertRedirects(response, response_url)
