from ticketing.tests.utility import test_data

from ticketing.models import User

from django.test import TestCase


class SeededTestCase(TestCase):
    def setUp(self):

        self.user_list = []

        # Emails must be unique so only make as many users as emails to avoid looping on emails
        # ID will
        for i in range(len(test_data.valid_emails)):
            user = User.objects.create_custom_user(
                test_data.valid_emails[i % len(test_data.valid_emails)],
                test_data.valid_passwords[i % len(test_data.valid_passwords)],
                test_data.valid_first_names[
                    i % len(test_data.valid_first_names)
                ],
                test_data.valid_last_names[
                    i % len(test_data.valid_last_names)
                ],
                test_data.valid_roles[i % len(test_data.valid_roles)],
            )

            self.user_list.append(user)

        # print("USER_LIST IS:", self.user_list)
