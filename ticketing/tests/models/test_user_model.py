"""Unit tests for User model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from ticketing.models.users import User



class UserModelTestCase(TestCase):
    """Unit tests for user model"""

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
    ]

    def setUp(self):
        self.user = User.objects.filter(role='ST').first()

    def create_second_student(self):
        return User.objects.filter(role='ST').last()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_cannot_contain_numbers(self):
        self.user.first_name = 'John1'
        self._assert_user_is_invalid()

    def test_last_name_cannot_contain_numbers(self):
        self.user.last_name = 'Doe1'
        self._assert_user_is_invalid()

    def test_first_name_cannot_contain_symbols(self):
        self.user.first_name = 'John!'
        self._assert_user_is_invalid()

    def test_last_name_cannot_contain_symbols(self):
        self.user.last_name = 'Doe!'
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        secondStudent = self.create_second_student()
        self.user.email = secondStudent.email
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at(self):
        self.user.email = 'johndoeexample.com'
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.com'
        self._assert_user_is_invalid()

    def test_email_must_contain_only_one_at(self):
        self.user.email = 'johndoe@@example.com'
        self._assert_user_is_invalid()

    def test_role_can_be_student(self):
        self.user.role = 'ST'
        self._assert_user_is_valid()

    def test_role_can_be_specialist(self):
        self.user.role = 'SP'
        self._assert_user_is_valid()

    def test_role_can_be_director(self):
        self.user.role = 'DI'
        self._assert_user_is_valid()

    def test_role_cant_be_empty(self):
        self.user.role = ''
        self._assert_user_is_invalid()

    def test_role_cant_be_random(self):
        self.user.role = 'AS'
        self._assert_user_is_invalid()

    def test_pre_save_does_not_change_existing_role_on_save(self):
        self.user.last_name = 'test'
        old_role = self.user.role
        self.user.save()
        new_user = User.objects.get(email=self.user.email)
        self.assertEquals(old_role, new_user.role)

    def test_pre_save_does_not_set_user_to_director_on_creation(self):
        user = User.objects.create_user(
            first_name='test',
            last_name='save',
            email='test.save@example.org',
            password='Password@123',
        )

        self.assertEquals(user.role, User.Role.STUDENT)

    def test_pre_save_does_set_user_to_specialist_on_creation(self):
        user = User.objects.create_specialist(
            first_name='test',
            last_name='save',
            email='test.save@example.org',
            password='Password@123',
        )

        self.assertEquals(user.role, User.Role.SPECIALIST)

    def test_pre_save_does_set_superuser_to_director_on_creation(self):
        user = User.objects.create_director(
            first_name='test',
            last_name='save',
            email='test.save@example.org',
            password='Password@123',
        )

        self.assertEquals(user.role, User.Role.DIRECTOR)

    def test_create_student_with_invalid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                first_name='test',
                last_name='save',
                email='',
                password='Password@123',
            )

    def test_create_student_with_invalid_first_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                first_name='',
                last_name='save',
                email='test.save@example.org',
                password='Password@123',
            )

    def test_create_student_with_invalid_last_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                first_name='test',
                last_name='',
                email='test.save@example.org',
                password='Password@123',
            )

    ###

    def test_create_specialist_with_invalid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_specialist(
                first_name='test',
                last_name='save',
                email='',
                password='Password@123',
            )

    def test_create_specialist_with_invalid_first_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_specialist(
                first_name='',
                last_name='save',
                email='test.save@example.org',
                password='Password@123',
            )

    def test_create_specialist_with_invalid_last_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_specialist(
                first_name='test',
                last_name='',
                email='test.save@example.org',
                password='Password@123',
            )

    ####

    def test_create_director_with_invalid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_director(
                first_name='test',
                last_name='save',
                email='',
                password='Password@123',
            )

    def test_create_director_with_invalid_first_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_director(
                first_name='',
                last_name='save',
                email='test.save@example.org',
                password='Password@123',
            )

    def test_create_director_with_invalid_last_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_director(
                first_name='test',
                last_name='',
                email='test.save@example.org',
                password='Password@123',
            )

    def test_create_valid_superuser(self):
        self.user = User.objects.create_superuser(
            first_name='test',
            last_name='save',
            email='test.save@example.org',
            password='Password@123',
        )

        self._assert_user_is_valid()
