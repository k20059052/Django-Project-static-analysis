from django.test import Client, TestCase
from django.urls import reverse
from slugify import slugify
from ticketing.models.faq import FAQ
from ticketing.models.users import User
from ticketing.models.departments import Department, Subsection
from ticketing.models.specialist import SpecialistDepartment


class SpecialistFAQListViewTest(TestCase):
    def setUp(self):
        self.specialist = User.objects.create_specialist(
            email='test.specialist@email.com',
            first_name='test',
            last_name='specialist',
            password='Password@123',
        )
        self.department = Department.objects.create(
            name='Health and Safety', slug=slugify('Health and Safety')
        )
        self.specialist_dept = SpecialistDepartment.objects.create(
            specialist=self.specialist, department=self.department
        )
        self.subsection = Subsection.objects.create(
            department=self.department, name='Help needed'
        )
        self.faq = FAQ.objects.create(
            specialist=self.specialist,
            department=self.department,
            subsection=self.subsection,
            question='What is 9+10',
            answer='19',
        )

        self.url = reverse('check_faq')

    def test_individual_faq__specialist_view_uses_correct_template(self):
        # Test that the view uses the correct template
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'faq/individual_faq_list.html')

    def test_individual_faq_specialist_view_redirects_unauthorized_user(self):
        response = self.client.get(reverse('check_faq'))
        self.assertEqual(response.status_code, 302)

        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(reverse('check_faq'))
        self.assertEqual(response.status_code, 200)

    def test_individual_faq_view_specialist_view_uses_correct_queryset(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['object_list']), [self.faq])

    def test_individual_faq_specialist_view_displays_department_name(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Health and Safety')

    def test_individual_faq_specialist_view_pagination_is_set(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['paginator'].num_pages, 1)
        self.assertEqual(len(response.context['object_list']), 1)

    def test_individual_faq_specialist_view_redirects_unauthenticated_user(
        self,
    ):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/check_faq/')

    def test_individual_faq_specialist_view_searches_by_keyword(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url, {'search': '9+10'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['object_list']), [self.faq])

    def test_individual_faq_specialist_view_displays_faq_question(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'What is 9+10')

    def test_individual_faq_specialist_view_displays_faq_answer(self):
        self.client.login(
            email='test.specialist@email.com', password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertContains(response, '19')
