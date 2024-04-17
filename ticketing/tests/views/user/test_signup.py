from django.test import TestCase
from ticketing.forms import SignupForm
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from ticketing.models import User


class SignUpViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.com',
            'password1': 'Password123password',
            'password2': 'Password123password',
        }
        User.objects.create_user(
            email='johndoe@example.com',
            first_name='John',
            last_name='Doe',
            password='Password123',
        )

    def test_signup_url(self):
        self.assertEqual(self.url, '/signup/')

    def test_get_signup(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignupForm))
        self.assertFalse(form.is_bound)

    def test_get_signup_redirects_when_logged_in(self):
        form_input = {
            'username': 'johndoe@example.com',
            'password': 'Password123',
        }
        response = self.client.post(reverse('login'), form_input, follow=True)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url)
        self.assertTemplateUsed(response, 'index.html')

    def test_post_signup_redirects_when_logged_in(self):
        form_input = {
            'username': 'johndoe@example.com',
            'password': 'Password123',
        }
        response = self.client.post(reverse('login'), form_input, follow=True)
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url)
        self.assertTemplateUsed(response, 'index.html')

    def test_unsuccessful_signup(self):
        self.form_input['email'] = 'notvalidemail'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignupForm))
        self.assertTrue(form.is_bound)

    def test_successful_signup(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('login')
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')
        user = User.objects.get(email='janedoe@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        is_password_correct = check_password(
            'Password123password', user.password
        )
        self.assertTrue(is_password_correct)
