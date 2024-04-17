from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from django.urls import reverse

from ticketing.models import SpecialistDepartment, Ticket, User, Subsection
from ticketing.models.faq import FAQ
from ticketing.views.faq.specialist_faq_form import FAQFormView


class FAQFormViewTest(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
        'ticketing/tests/fixtures/subsection_fixtures.json',
    ]

    def setUp(self):
        
        self.factory = RequestFactory()
        self.specialist = User.objects.filter(role = 'SP').first()
        self.department = SpecialistDepartment.objects.get(specialist = self.specialist).department
        self.subsection = Subsection.objects.filter(department = self.department).first()
        self.ticket = Ticket.objects.filter(department = self.department).first()
        self.ticket.status = Ticket.Status.CLOSED
        self.ticket.save()
        self.url = reverse('specialist_create_faq_from_ticket',kwargs={"pk":self.ticket.id})
        self.ticket_id = self.ticket.id

        self.faq = FAQ.objects.create(
            specialist=self.specialist,
            subsection=self.subsection,
            department=self.department,
            question='What is the meaning of existence',
            answer='This question cannot be computed... error',
        )
        self.form_data = {
            'question': 'What is Django?',
            'subsection':str(self.subsection.id),
            'answer': 'Django is a high-level Python web framework.',
        }

    def test_faq_form_url(self):
        self.assertEqual(self.url, '/specialist_create_faq_from_ticket/'+str(self.ticket_id))

    def test_get_faq_form(self):
        request = self.factory.get(self.url)
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_post_valid_faq_form(self):
        request = self.factory.post(
            self.url, data=self.form_data
        )
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FAQ.objects.count(), 2)

    def test_post_invalid_faq_form(self):
        request = self.factory.post(self.url, data={})
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_log_in_required_to_access_faq_form(self):
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('login') + '?next=' + self.url,
        )

    def test_role_required_to_access_faq_form(self):
        request = self.factory.get(self.url)
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_faq_form_view_uses_correct_template(self):
        request = self.factory.get(self.url)
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertTemplateUsed('specialist_create_faq_from_ticket.html')

    def test_faq_form_has_context_data(self):
        request = self.factory.get(self.url)
        request.user = self.specialist
        response = FAQFormView.as_view()(request)
        self.assertTrue('form' in response.context_data)

    def test_faq_form_submission_is_limited_to_specialists(self):
        request = self.factory.post(
            self.url, data=self.form_data
        )
        request.user = AnonymousUser()
        response = FAQFormView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FAQ.objects.count(), 1)

    def test_redirect_to_specialist_dashboard(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'faq/specialist_create_faq_from_ticket.html')

    def test_create_faq_from_archived_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

     
        response = self.client.post(self.url, data = self.form_data)
        self.assertEquals(response.status_code, 302)

    def test_create_faq_from_archived_as_specialist_redirects_correctly(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

     
        response = self.client.post(self.url, data = self.form_data, follow = True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    

    
