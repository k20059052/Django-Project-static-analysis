"""Unit tests for Department model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.departments import *


class DepartmentModelTestCase(TestCase):
    """Unit tests for Department model"""

    def setUp(self):
        self.department = Department.objects.create(name='Accomodation')

    def create_second_department(self):
        return Department.objects.create(name='Science')

    def _assert_department_is_valid(self):
        try:
            self.department.full_clean()
        except (ValidationError):
            self.fail('Test department should be valid')

    def _assert_department_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.department.full_clean()

    def test_valid_department(self):
        self._assert_department_is_valid()

    def test_name_cannot_be_blank(self):
        self.department.name = ''
        self._assert_department_is_invalid()

    def test_name_must_be_unique(self):
        secondDepartment = self.create_second_department()
        self.department.name = secondDepartment.name
        self._assert_department_is_invalid()

    def test__str__returns_name(self):
        self.assertEqual(self.department.__str__(), self.department.name)
