from django.test import Client, TestCase
from django.urls import reverse
from ticketing.models import User, Department, Ticket, Message, StudentMessage

class StudentMessageViewTestCase(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]
    def setUp(self):
        self.student = User.objects.filter(role='ST').first()
        self.specialist = User.objects.filter(role='SP').first()
        self.ticket = Ticket.objects.filter(student = self.student).first()
        self.url = reverse('archived_ticket', kwargs={'pk' : self.ticket.id})
        self.not_student_ticket = Ticket.objects.exclude(student = self.student).first()
        
    def test_student_message_url(self):
         self.assertEqual(self.url, "/archived_ticket/" + str(self.ticket.id))

    def test_student_get(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        response = self.client.get(self.url, {"pk": self.ticket.id})
        self.assertTemplateUsed(response, 'archived_ticket.html')
        self.assertEqual(response.status_code, 200)
    
    def test_specialist_get(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        response = self.client.get(self.url, {"pk": self.ticket.id})
        self.assertTemplateUsed(response, 'archived_ticket.html')
        self.assertEqual(response.status_code, 200)