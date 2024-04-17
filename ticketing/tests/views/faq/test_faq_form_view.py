from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from django.urls import reverse
from ticketing.models.users import User
from ticketing.models.departments import Department, Subsection
from ticketing.models.specialist import SpecialistDepartment
from ticketing.models.faq import FAQ
from ticketing.views.faq.specialist_faq_form import FAQFormView


class SpecialistCreateFAQFormViewTest(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
        'ticketing/tests/fixtures/subsection_fixtures.json'
    ]

    def setUp(self):
        self.url = reverse('faq_form_view')
        self.factory = RequestFactory()
        self.specialist = User.objects.filter(role = 'SP').first()
        self.department = SpecialistDepartment.objects.get(specialist = self.specialist).department
        self.subsection = Subsection.objects.filter(department = self.department).first()
        self.faq = FAQ.objects.create(
            specialist=self.specialist,
            department=self.department,
            subsection=self.subsection,
            question='What is the meaning of existence',
            answer='This question cannot be computed... error',
        )
        self.form_data = {
            'question': 'What is Django?',
            'subsection':str(self.subsection.id),
            'answer': 'Django is a high-level Python web framework.',
        }

    def test_faq_form_url(self):
        self.assertEqual(self.url, reverse('faq_form_view'))

    def test_get_faq_form(self):
        request = self.factory.get(reverse('faq_form_view'))
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_post_valid_faq_form(self):
        request = self.factory.post(
            reverse('faq_form_view'), data=self.form_data
        )
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FAQ.objects.count(), 2)

    def test_post_invalid_faq_form(self):
        request = self.factory.post(reverse('faq_form_view'), data={})
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_log_in_required_to_access_faq_form(self):
        request = self.factory.get(reverse('faq_form_view'))
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('login') + '?next=' + reverse('faq_form_view'),
        )

    def test_role_required_to_access_faq_form(self):
        request = self.factory.get(reverse('faq_form_view'))
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_faq_form_view_uses_correct_template(self):
        request = self.factory.get(reverse('faq_form_view'))
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertTemplateUsed('faq_specialist_form.html')

    def test_faq_form_has_context_data(self):
        request = self.factory.get(reverse('faq_form_view'))
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertTrue('form' in response.context_data)

    def test_faq_form_submission_is_limited_to_specialists(self):
        request = self.factory.post(
            reverse('faq_form_view'), data=self.form_data
        )
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FAQ.objects.count(), 1)
