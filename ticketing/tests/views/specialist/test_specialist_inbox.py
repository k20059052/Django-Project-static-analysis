from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User, Department
from ticketing.models.specialist import SpecialistInbox, SpecialistDepartment
from ticketing.models.tickets import Ticket
from ticketing.tests.helpers import (
    FixtureHelpers,
    reverse_with_next,
    get_tickets,
)


class SpecialistInboxViewTestCase(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):
        self.url = reverse(
            'specialist_dashboard', kwargs={'ticket_type': 'personal'}
        )
        self.specialist = User.objects.filter(role='SP').first()
        self.student = User.objects.filter(role='ST').first()
        self.director = User.objects.filter(role='DI').first()

    def make_ticket_filter_query(self, email, header, filter_method):
        return {'email': email, 'header': header, 'filter_method': filter_method}

    def test_specialist_dashboard_url(self):
        self.assertEqual(self.url, '/specialist_dashboard/personal/')

    def test_get_specialist_dashboard_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_specialist_dashboard_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_specialist_dashboard_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'specialist/specialist_dashboard.html')

    def test_get_specialist_dashboard_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_initial_inbox_is_personal(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context['ticket_type'], 'personal')

    def test_wrong_slug_goes_to_personal(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        self.url = reverse(
            'specialist_dashboard', kwargs={'ticket_type': 'nonsense'}
        )
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.context['ticket_type'], 'personal')

    def test_personal_inbox_shows_correct_tickets(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        view_table = []

        response = self.client.get(
            reverse('specialist_dashboard', kwargs={'ticket_type': 'personal'})
        )

        num_pages = response.context['page_obj'].paginator.num_pages

        for i in range(1, num_pages + 1):
            response = self.client.get(
                reverse(
                    'specialist_dashboard', kwargs={'ticket_type': 'personal'}
                ),
                {'page': i},
            )

            for ticket in response.context['object_list']:
                view_table.append(ticket)

        right_ticket_list = get_tickets(self.specialist, 'personal')

        for ticket in right_ticket_list:
            self.assertTrue(ticket in view_table)

    def test_department_inbox_shows_correct_tickets(self):
        SpecialistInbox.objects.all().delete()
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        view_table = []

        response = self.client.get(
            reverse(
                'specialist_dashboard', kwargs={'ticket_type': 'department'}
            )
        )

        num_pages = response.context['page_obj'].paginator.num_pages

        for i in range(1, num_pages + 1):
            response = self.client.get(
                reverse(
                    'specialist_dashboard',
                    kwargs={'ticket_type': 'department'},
                ),
                {'page': i},
            )

            for ticket in response.context['object_list']:
                view_table.append(ticket)

        right_ticket_list = get_tickets(self.specialist, 'department')

        for ticket in right_ticket_list:
            self.assertTrue(ticket in view_table)

    def test_archived_inbox_shows_correct_tickets(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        view_table = []

        response = self.client.get(
            reverse('specialist_dashboard', kwargs={'ticket_type': 'archived'})
        )

        num_pages = response.context['page_obj'].paginator.num_pages

        for i in range(1, num_pages + 1):
            response = self.client.get(
                reverse(
                    'specialist_dashboard', kwargs={'ticket_type': 'archived'}
                ),
                {'page': i},
            )

            for ticket in response.context['object_list']:
                view_table.append(ticket)

        right_ticket_list = get_tickets(self.specialist, 'archived')

        for ticket in right_ticket_list:
            self.assertTrue(ticket in view_table)

    def test_view_ticket_info_redirect(self):
        SpecialistInbox.objects.all().delete()
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        self.url = reverse(
            'specialist_dashboard', kwargs={'ticket_type': 'department'}
        )
        response = self.client.get(self.url)
        view_table = response.context['object_list']
        ticket_id = view_table[0].id
        url = f'specialist_claim_ticket/{ticket_id}'
        self.assertIn(str.encode(url), response.content)

    def test_unclaim_button_works(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )
        response = self.client.get(self.url)
        tickets = response.context['object_list']
        before_count = len(tickets)

        response = self.client.post(
            self.url,
            {'unclaim': tickets[0].id},
        )
        after_count = len(response.context['object_list'])

        self.assertEquals(before_count, after_count + 1)

    def test_reroute_ticket_works(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        response = self.client.get(self.url)
        tickets = response.context['object_list']
        first_ticket_id = tickets[0].id
        first_ticket = Ticket.objects.get(id=first_ticket_id)
        before_count = len(tickets)

        previous_department = first_ticket.department.name

        specialist_department = SpecialistDepartment.objects.get(
            specialist=self.specialist
        ).department
        departments = Department.objects.exclude(
            name=specialist_department.name
        )

        response = self.client.post(
            self.url,
            {'reroute': departments.first().name + ' ' + str(first_ticket.id)},
        )

        first_ticket = Ticket.objects.get(id=first_ticket_id)
        current_department = first_ticket.department.name

        after_count = len(response.context['object_list'])

        self.assertEquals(before_count, after_count + 1)
        self.assertNotEquals(previous_department, current_department)
        self.assertEquals(departments.first().name, current_department)

    def test_reroute_no_department_selected(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        response = self.client.get(self.url)
        response = self.client.post(
            self.url,
            {'reroute': '0'},
        )

        error_message = list(response.context['messages'])[0]
        self.assertEqual('Select a valid option!', str(error_message))

    def test_personal_inbox_filtering(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        response = self.client.get(self.url)
        view_table = response.context['object_list']
        before_count = len(view_table)

        input_email = view_table[0].student.email
        input_header = view_table[0].header

        response = self.client.get(
            reverse(
                'specialist_dashboard', kwargs={'ticket_type': 'personal'}
            ),
            data=self.make_ticket_filter_query(input_email, input_header, 'filter'),
        )

        view_table = response.context['object_list']
        after_count = len(view_table)
        self.assertNotEquals(before_count, after_count)
        self.assertEqual(after_count, 1)

        ticket = view_table[0]
        self.assertEqual(ticket.student.email, input_email)
        self.assertEqual(ticket.header, input_header)

    def test_order_of_ticket_is_descending_in_inbox(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        response = self.client.get(self.url)
        tickets = response.context['object_list']

        if (len(tickets) >= 2):
            for i in range(1, len(tickets)):
                self.assertLess(tickets[i-1].id, tickets[i].id)

    def test_personal_inbox_searching(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        response = self.client.get(self.url)
        view_table = response.context['object_list']
        before_count = len(view_table)

        input_email = view_table[0].student.email
        input_header = view_table[0].header

        response = self.client.get(
            reverse(
                'specialist_dashboard', kwargs={'ticket_type': 'personal'}
            ),
            data=self.make_ticket_filter_query(input_email, input_header, 'search'),
        )

        view_table = response.context['object_list']
        after_count = len(view_table)
        self.assertNotEquals(before_count, after_count)
        self.assertEqual(after_count, 1)

        ticket = view_table[0]
        self.assertEqual(ticket.student.email, input_email)
        self.assertEqual(ticket.header, input_header)
