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
        self.ticket = Ticket.objects.filter(student = self.student).first()
        self.url = reverse('student_message', kwargs={'pk' : self.ticket.id})
        self.not_student_ticket = Ticket.objects.exclude(student = self.student).first()
    def test_student_message_url(self):
         self.assertEqual(self.url, "/ticket/" + str(self.ticket.id) + "/")

    def test_student_message_post(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        response = self.client.get(self.url, follow=True)
        data = {
            'content': 'Test message content'
        }
        before_count = Message.objects.count()
        self.client.post(self.url, data=data)
        after_count = Message.objects.count()

        self.assertEquals(before_count + 1 , after_count)
        # Check that the message was saved to the database
        student_message = StudentMessage.objects.filter(
            ticket=self.ticket,
            content='Test message content'
        ).first()
        self.assertIsNotNone(student_message)
    
    def test_wrong_pk_when_post(self): 
        self.client = Client()
        self.url = reverse('student_message', kwargs={'pk' : self.not_student_ticket.pk})
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')

    def test_close_ticket_archives_ticket(self):
        self.client = Client()
        self.url = reverse('student_message', kwargs={'pk' : self.ticket.pk})
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )
        response = self.client.post(self.url,{"view":self.ticket.pk})
        self.assertEquals(self.ticket.status, Ticket.Status.CLOSED)


    def test_close_ticket_redirects_to_student_dashboard(self):
        self.client = Client()
        self.url = reverse('student_message', kwargs={'pk' : self.ticket.pk})
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )
        response = self.client.post(self.url,{"view":self.ticket.pk}, follow=True)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')
        self.assertEqual(response.status_code, 200)


    


 
    