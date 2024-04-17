"""Unit tests for Specialist Department model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.departments import *
from ticketing.models.users import User
from ticketing.models.specialist import *
from ticketing.models.tickets import *


class DepartmentModelTestCase(TestCase):
    """Unit tests for Specialist Department model"""

    def setUp(self):

        self.department = Department.objects.create(name='Accomodation')

        self.specialist = User.objects.create_specialist(
            first_name='John',
            last_name='Doe',
            email='John.Doe@example.com',
            password='Password@123',
        )

        self.student = User.objects.create_user(
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

        self.specialist_department = SpecialistDepartment.objects.create(
            specialist=self.specialist, department=self.department
        )

        self.ticket = Ticket.objects.create(
            student=self.student,
            department=self.department,
            header='test ticket',
        )

        self.specialist_inbox = SpecialistInbox.objects.create(
            specialist=self.specialist, ticket=self.ticket
        )

    def _assert_specialist_department_is_valid(self):
        try:
            self.specialist_department.full_clean()
        except (ValidationError):
            self.fail('Test specialist department should be valid')

    def _assert_specialist_department_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.specialist_department.full_clean()

    def _assert_specialist_inbox_is_valid(self):
        try:
            self.specialist_inbox.full_clean()
        except (ValidationError):
            self.fail('Test specialist department should be valid')

    def _assert_specialist_inbox_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.specialist_inbox.full_clean()

    def test_valid_specialist_department(self):
        self._assert_specialist_department_is_valid()

    def test_valid_specialist_inbox(self):
        self._assert_specialist_inbox_is_valid()

    def test_specialist_department_specialist_can_not_be_none(self):
        self.specialist_department.specialist = None
        self._assert_specialist_department_is_invalid()

    def test_specialist_department_department_can_not_be_none(self):
        self.specialist_department.department = None
        self._assert_specialist_department_is_invalid()

    def test_specialist_department_specialist_can_not_be_student(self):
        self.specialist_department.specialist = self.student
        self._assert_specialist_department_is_invalid()

    def test_specialist_department_specialist_can_not_be_director(self):
        self.specialist_department.specialist = self.director
        self._assert_specialist_department_is_invalid()

    #####

    def test_specialist_inbox_specialist_can_not_be_none(self):
        self.specialist_inbox.specialist = None
        self._assert_specialist_inbox_is_invalid()

    def test_specialist_inbox_ticket_can_not_be_none(self):
        self.specialist_inbox.ticket = None
        self._assert_specialist_inbox_is_invalid()

    def test_specialist_inbox_specialist_can_not_be_student(self):
        self.specialist_inbox.specialist = self.student
        self._assert_specialist_inbox_is_invalid()

    def test_specialist_inbox_specialist_can_not_be_director(self):
        self.specialist_inbox.specialist = self.director
        self._assert_specialist_inbox_is_invalid()
