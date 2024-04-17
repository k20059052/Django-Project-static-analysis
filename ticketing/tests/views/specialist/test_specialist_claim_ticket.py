from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models.users import User
from ticketing.models.specialist import SpecialistInbox, SpecialistDepartment
from ticketing.models.tickets import Ticket
from ticketing.tests.helpers import (
    FixtureHelpers,
    reverse_with_next,
    get_tickets,
)


class SpecialistClaimTicketViewTestCase(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):

        self.specialist = User.objects.get(
            email=(FixtureHelpers.get_specialist_from_fixture())['email']
        )
        self.student = FixtureHelpers.get_student_from_fixture()
        self.director = FixtureHelpers.get_director_from_fixture()

        specialist_department = SpecialistDepartment.objects.get(
            specialist=self.specialist
        ).department
        self.ticket = Ticket.objects.filter(
            department=specialist_department
        ).first()
        self.url = reverse(
            'specialist_claim_ticket', kwargs={'pk': self.ticket.id}
        )

    def test_specialist_claim_ticket_url(self):
        self.assertEqual(
            self.url, f'/specialist_claim_ticket/{self.ticket.id}'
        )

    def test_get_specialist_claim_ticket_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student['email'], password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_specialist_claim_ticket_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director['email'], password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_specialist_claim_ticket_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialist/specialist_claim_ticket.html')

    def test_get_specialist_dashboard_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_back_returns_to_dashboard(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url, follow=True)
        url = 'specialist_dashboard'
        self.assertIn(str.encode(url), response.content)

    def test_claim_ticket_works(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        before_count = SpecialistInbox.objects.filter(
            specialist=self.specialist
        ).count()
        response = self.client.post(
            self.url, data={'accept_ticket': self.ticket.id}, follow=True
        )
        after_count = SpecialistInbox.objects.filter(
            specialist=self.specialist
        ).count()
        self.assertEqual(before_count + 1, after_count)

    def test_claim_ticket_redirects_special_dashboard(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(
            self.url, data={'accept_ticket': self.ticket.id}, follow=True
        )
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    def test_claim_ticket_that_does_not_exist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        before_count = SpecialistInbox.objects.count()
        response = self.client.post(
            self.url, data={'accept_ticket': 9999}, follow=True
        )
        after_count = SpecialistInbox.objects.count()

        self.assertEqual(before_count, after_count)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    def test_claim_ticket_that_does_not_exist_redirects_specialist_dashboard(
        self,
    ):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.url = reverse('specialist_claim_ticket', kwargs={'pk': 9999})

        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    def test_specialist_claim_ticket_when_specialist_has_no_department(
        self,
    ):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        SpecialistDepartment.objects.get(specialist=self.specialist).delete()
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')