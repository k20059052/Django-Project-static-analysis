"""Unit tests for Message model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.users import User
from ticketing.models.departments import Department
from ticketing.models.tickets import *


class DepartmentModelTestCase(TestCase):
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

        self.department = Department.objects.create(name='Accomodation')
        self.ticket = Ticket.objects.create(
            student=self.student,
            department=self.department,
            header='test ticket',
        )

        self.message = Message.objects.create(
            ticket=self.ticket, content='test content'
        )

        self.student_message = StudentMessage.objects.create(
            ticket=self.message.ticket,
            content=self.message.content,
            date_time=self.message.date_time,
        )

        self.specialist_message = SpecialistMessage.objects.create(
            ticket=self.message.ticket,
            content=self.message.content,
            date_time=self.message.date_time,
            responder=self.specialist,
        )

    def _assert_message_is_valid(self):
        try:
            self.message.full_clean()
        except (ValidationError):
            self.fail('Test message should be valid')

    def _assert_message_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.message.full_clean()

    def _assert_student_message_is_valid(self):
        try:
            self.student_message.full_clean()
        except (ValidationError):
            self.fail('Test student message should be valid')

    def _assert_student_message_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student_message.full_clean()

    def _assert_specialist_message_is_valid(self):
        try:
            self.specialist_message.full_clean()
        except (ValidationError):
            self.fail('Test specialist message should be valid')

    def _assert_specialist_message_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.specialist_message.full_clean()

    def test_valid_message(self):
        self._assert_message_is_valid()

    def test_message_ticket_can_not_be_empty(self):
        self.message.ticket = None
        self._assert_message_is_invalid()

    def test_message_content_can_not_be_empty(self):
        self.message.content = ''
        self._assert_message_is_invalid()

    def test_student_message_ticket_can_not_be_empty(self):
        self.student_message.ticket = None
        self._assert_student_message_is_invalid()

    def test_student_message_content_can_not_be_empty(self):
        self.student_message.content = ''
        self._assert_student_message_is_invalid()

    def test_specialist_message_ticket_can_not_be_empty(self):
        self.specialist_message.ticket = None
        self._assert_specialist_message_is_invalid()

    def test_specialist_message_content_can_not_be_empty(self):
        self.specialist_message.content = ''
        self._assert_specialist_message_is_invalid()

    def test_specialist_message_responder_is_not_specialist(self):
        self.specialist_message.responder = self.student
        self._assert_specialist_message_is_invalid()
