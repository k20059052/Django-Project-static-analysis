"""Unit tests for Ticket model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.users import User
from ticketing.models.departments import Department
from ticketing.models.tickets import Ticket


class TicketModelTestCase(TestCase):
    """Unit tests for Message model"""

    def setUp(self):
        self.student = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='John.Doe@example.com',
            password='Password@123',
        )

        self.specialist = User.objects.create_specialist(
            first_name='Jane',
            last_name='Doe',
            email='Jane.Doe@example.com',
            password='Password@123',
        )

        self.director = User.objects.create_director(
            first_name='Bob',
            last_name='Doe',
            email='Bob.Doe@example.com',
            password='Password@123',
        )

        self.department = Department.objects.create(name='Accomodation')
        self.ticket = Ticket.objects.create(
            student=self.student,
            department=self.department,
            header='test ticket',
        )

    def _assert_ticket_is_valid(self):
        try:
            self.ticket.full_clean()
        except (ValidationError):
            self.fail('Test ticket should be valid')

    def _assert_ticket_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_valid_ticket(self):
        self._assert_ticket_is_valid()

    def test_header_cannot_be_blank(self):
        self.ticket.header = ''
        self._assert_ticket_is_invalid()

    def test_student_cannot_be_none(self):
        self.ticket.student = None
        self._assert_ticket_is_invalid()

    def test_user_cannot_be_specialist(self):
        self.ticket.student = self.specialist
        self._assert_ticket_is_invalid()

    def test_user_cannot_be_director(self):
        self.ticket.student = self.director
        self._assert_ticket_is_invalid()

    def test_department_cannot_be_none(self):
        self.ticket.department = None
        self._assert_ticket_is_invalid()
