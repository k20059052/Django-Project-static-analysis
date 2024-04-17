from django.test import TestCase
from django.urls import reverse
from ticketing.models import User, Department


class StudentDashboardViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('student_dashboard')
        self.user = User.objects.create_user(
            email='johndoe@example.com',
            first_name='John',
            last_name='Doe',
            password='Password@123',
        )
        self.department = Department.objects.create(name='Accommodation')
        self.client.login(email='johndoe@example.com', password='Password@123')

    def test_student_dashboard_url(self):
        self.assertEqual(self.url, '/student_dashboard/')

    def test_get_student_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')
