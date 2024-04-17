from django.test import Client, TestCase
from django.urls import reverse
from ticketing.models import User, Ticket, Message, SpecialistInbox, SpecialistMessage, SpecialistDepartment, Department

class SpecialistMessageViewTestCase(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
    ]
    def setUp(self):
        self.specialist = User.objects.filter(role='SP').first()
        self.ticket = SpecialistInbox.objects.filter(specialist = self.specialist).first().ticket
        self.url = reverse('specialist_message', kwargs={'pk' : self.ticket.id})
        self.specialist_department = SpecialistDepartment.objects.filter(specialist = self.specialist).first().department
        self.ticket_from_different_department = Ticket.objects.exclude(department = self.specialist_department).first()
    
    def test_specialist_message_url(self):
         self.assertEqual(self.url, "/specialist_message/" + str(self.ticket.id) )

    def test_specialist_message_post(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
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
        specialist_message = SpecialistMessage.objects.filter(
            ticket=self.ticket,
            content='Test message content'
        ).first()
        self.assertIsNotNone(specialist_message)
    
    def test_wrong_ticket_type_when_post(self): 
        self.client = Client()
        self.url = reverse('specialist_dashboard', kwargs={'ticket_type' : 'se'})
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')
    
    def test_getting_personal_dashboard(self):
        self.client = Client()
        self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        self.url = reverse('specialist_dashboard', kwargs={'ticket_type': 'personal'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_close_ticket_archives_ticket(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.post(self.url, {"view": self.ticket.pk})
        self.ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEquals(self.ticket.status, Ticket.Status.CLOSED)
        self.assertEqual(response.status_code, 302)
    
    def test_close_ticket_redirects_to_specialist_dashboard(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
     
        response = self.client.post(self.url, {"view": self.ticket.pk}, follow=True)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')
        self.assertEqual(response.status_code, 200)

    def test_wrong_pk_when_post(self):
        self.client = Client()
        self.url = reverse('specialist_message', kwargs={'pk' :  self.ticket_from_different_department.id})
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')
        
        