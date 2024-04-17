"""Unit tests for Subsection model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.departments import *

class SubsectionModelTestCase(TestCase):
    """Unit tests for Subsection model"""

    def setUp(self):
        self.department = Department.objects.create(name='Accomodation')
        self.subsection = Subsection.objects.create(name='housing', department = self.department)
    
    def create_second_subsection(self):
        department_two = Department.objects.create(name='Science')
        return Subsection.objects.create(name='Physics', department = department_two)

    def _assert_subsection_is_valid(self):
        try:
            self.subsection.full_clean()
        except (ValidationError):
            self.fail('Test subsection should be valid')

    def _assert_subsection_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.subsection.full_clean()

    def test_valid_subsection(self):
        self._assert_subsection_is_valid()

    def test_name_cannot_be_blank(self):
        self.subsection.name = ''
        self._assert_subsection_is_invalid()

    def test_name_must_be_unique(self):
        second_subsection = self.create_second_subsection()
        self.subsection.name = second_subsection.name
        self._assert_subsection_is_invalid()

    def test__str__returns_name(self):
        self.assertEqual(self.subsection.__str__(), self.subsection.name)