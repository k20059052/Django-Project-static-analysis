from ticketing.models import Ticket,User,Department
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from student_query_system import settings

class StudentInboxViewTest(TestCase):
    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):
        self.student=User.objects.create_user(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        self.department=Department.objects.create(
            name='Health and Safety',
            slug=slugify('Health and Safety')
        )
       
        self.ticket1 = Ticket.objects.create(
            student=self.student,                                 
            department=self.department, 
            header='Ticket 1',
            status=Ticket.Status.OPEN,
        )
        self.ticket2 = Ticket.objects.create(
            student=self.student,
            department=self.department,
            header='Ticket 2',
            status=Ticket.Status.CLOSED,
        )
        self.url=reverse('student_inbox')

    def test_student_inbox_view_get_request(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        response= self.client.get(reverse('student_inbox'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,self.ticket1.header)       
        
    def test_student_inbox_view_contains_correct_template(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        response=self.client.get(reverse('student_inbox'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'student/student_dashboard.html')
        self.assertTemplateUsed(response,'base.html')
        self.assertTemplateUsed(response,'partials/header.html')
        self.assertTemplateUsed(response,'inbox.html')
        self.assertTemplateUsed(response,'partials/pagination.html')
        self.assertTemplateUsed(response,'partials/footer.html')
    
    def test_student_inbox_view_redirects_if_not_logged_in(self):
        response=self.client.get(reverse('student_inbox'))
        self.assertRedirects(response,f'/{settings.LOGIN_URL}/?next={self.url}',fetch_redirect_response=False)
    
    def test_student_inbox_view_context(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        response=self.client.get(reverse('student_inbox'))
        self.assertEqual(response.context['type_of_ticket'],'')
    
    def test_student_inbox_view_post_open(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        response = self.client.post(reverse('student_inbox'), {'type_of_ticket': 'Open'})
        self.assertQuerysetEqual(
            response.context['page_obj'],Ticket.objects.filter(student=self.student, status='Open'), ordered=False)
        self.assertEqual(response.context['type_of_ticket'], 'Open')

    def test_student_inbox_view_post_close(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )

        response = self.client.post(reverse('student_inbox'), {'type_of_ticket': 'Closed'})
        self.assertQuerysetEqual(
            response.context['page_obj'],Ticket.objects.filter(student=self.student, status='Closed'), ordered=False)
        self.assertEqual(response.context['type_of_ticket'], 'Closed')
    
    def test_student_inbox_view_post_invalid(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        response = self.client.post(reverse('student_inbox'), {'type_of_ticket': 'Invalid'})
        self.assertQuerysetEqual(
            response.context['page_obj'],Ticket.objects.none(), ordered=False)
        self.assertEqual(response.context['type_of_ticket'], 'Invalid')
    
    def test_student_inbox_view_pagination(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        for i in range(6):
            Ticket.objects.create(
                student=self.student, department=self.department, header=f'Test Ticket {i+3}')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['page_obj']), 5)

        response = self.client.get(f'{self.url}?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['object_list']), 3)

    def test_student_inbox_view_post_pagination(self):
        self.client.login(
            email='student.user@email.com',
            first_name='Joseph',
            last_name='Joestar',
            password='Password@123'
        )
        for i in range(6):
            Ticket.objects.create(
                student=self.student, department=self.department, header=f'Test Ticket {i+3}')

        response = self.client.post(self.url, {'type_of_ticket': 'Open'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['page_obj']), 5)

        response = self.client.post(self.url, {'type_of_ticket': 'Closed'})
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertFalse(response.context['is_paginated'])
       
        response = self.client.post(self.url, {'type_of_ticket': 'Invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_paginated'])
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_student_inbox_redirects_to_student_message(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        response = self.client.get(self.url)
        tickets = response.context['object_list']
        
        current_ticket = None
        for ticket in tickets:
            if ticket.status == Ticket.Status.OPEN:
                current_ticket = ticket
                break

        self.client.post(self.url, {"view": current_ticket.id}, follow=True)
        self.assertTemplateUsed(response,'student/student_dashboard.html')

    def test_student_inbox_redirects_to_message_list(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        response = self.client.get(self.url)
        tickets = response.context['object_list']
        
        current_ticket = None
        for ticket in tickets:
            if ticket.status == Ticket.Status.CLOSED:
                current_ticket = ticket
                break

        self.client.post(self.url, {"view": current_ticket.id}, follow=True)
        self.assertTemplateUsed(response,'student/student_dashboard.html')

    

        
    