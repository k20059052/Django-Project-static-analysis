from django.urls import reverse
import json
from ticketing.views.specialist.specialist_inbox import SpecialistInboxView
from ticketing.models.tickets import Ticket


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f'?next={next_url}'
    return url

def get_tickets(user, ticket_type):
    dummy_object = SpecialistInboxView()
    return dummy_object.get_tickets(user, ticket_type, Ticket.objects.all())

class FixtureHelpers:
    @staticmethod
    def get_all_users_from_fixture():
        f = open('ticketing/tests/fixtures/user_fixtures.json')
        data = json.load(f)
        return data

    @staticmethod
    def get_all_departments_from_fixture():
        f = open('ticketing/tests/fixtures/department_fixtures.json')
        data = json.load(f)
        return data

    @staticmethod
    def get_all_tickets_from_fixture():
        f = open('ticketing/tests/fixtures/message_fixtures.json')
        data = json.load(f)
        return data

    @staticmethod
    def get_all_messages_from_fixture():
        f = open('ticketing/tests/fixtures/message_fixtures.json')
        data = json.load(f)
        return data

    @staticmethod 
    def get_all_faqs_from_fixture():
        f = open('ticketing/tests/fixtures/faq_fixtures.json')
        data = json.load(f)
        return data
    
    @staticmethod
    def get_all_subsection_from_fixture():
        f = open('ticketing/tests/fixtures/subsection_fixtures.json')
        data = json.load(f)
        return data
    
    @staticmethod
    def get_students_from_fixture():
        students = []
        all_data = FixtureHelpers.get_all_users_from_fixture()
        for user in all_data:
            if user['fields']['role'] == 'ST':
                students.append(user['fields'])

        return students

    @staticmethod
    def get_student_from_fixture():
        students = FixtureHelpers.get_students_from_fixture()
        return students[0]

    @staticmethod
    def get_specialists_from_fixture():
        specialists = []
        all_data = FixtureHelpers.get_all_users_from_fixture()
        for user in all_data:
            if user['fields']['role'] == 'SP':
                specialists.append(user['fields'])

        return specialists

    @staticmethod
    def get_specialist_from_fixture():
        specialists = FixtureHelpers.get_specialists_from_fixture()
        return specialists[0]

    @staticmethod
    def get_directors_from_fixture():
        directors = []
        all_data = FixtureHelpers.get_all_users_from_fixture()
        for user in all_data:
            if user['fields']['role'] == 'DI':
                directors.append(user['fields'])

        return directors

    @staticmethod
    def get_director_from_fixture():
        directors = FixtureHelpers.get_directors_from_fixture()
        return directors[0]

    @staticmethod
    def get_departments_from_fixture():
        departments = []
        all_departments = FixtureHelpers.get_all_departments_from_fixture()
        for department in all_departments:
            departments.append(department['fields'])

        return departments

    @staticmethod
    def get_department_from_fixture():
        departments = FixtureHelpers.get_departments_from_fixture()
        return departments[0]

    @staticmethod
    def get_tickets_from_fixture():
        tickets = []
        all_tickets = FixtureHelpers.get_all_tickets_from_fixture()
        for ticket in all_tickets:
            tickets.append(ticket['fields'])

        return tickets

    @staticmethod
    def get_ticket_from_fixture():
        tickets = FixtureHelpers.get_tickets_from_fixture()
        return tickets[0]

    @staticmethod
    def get_messages_from_fixture():
        messages = []
        all_messages = FixtureHelpers.get_all_messages_from_fixture()
        for message in all_messages:
            messages.append(message['fields'])

        return message

    @staticmethod
    def get_message_from_fixture():
        messages = FixtureHelpers.get_messages_from_fixture()
        return messages[0]

    