from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User, Department
from ticketing.tests.helpers import reverse_with_next
from ticketing.tests.utility import test_data
from ticketing.utility.user import *


def make_department_filter_query(method, id, name):
    return {'filter_method': method, 'id': id, 'name': name}


def make_add_department_form_query(name):
    return {'add': 'Add', 'name': name}


class DepartmentManagerTestCase(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):
        self.url = reverse('department_manager')

        self.specialist = User.objects.filter(role='SP').first()
        self.student = User.objects.filter(role='ST').first()
        self.director = User.objects.filter(role='DI').first()

        self.non_login_director = (
            User.objects.all()
            .exclude(id=self.director.id)
            .filter(role='DI')
            .first()
        )

    def test_dm_dashboard_url(self):
        self.assertEqual(self.url, '/department_manager/')

    def test_get_dm_dashboard_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_dm_dashboard_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'director/department_manager.html')

    def test_get_dp_dashboard_as_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.specialist.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_dp_dashboard_when_logged_out(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'login.html')

    def test_add_department_good(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        departments = Department.objects.all()

        # Emails must be unique so only make as many users as emails to avoid looping on emails
        for i in range(len(test_data.valid_department_names)):

            before_count = Department.objects.all().count()

            query = make_add_department_form_query(
                test_data.valid_department_names[i]
            )

            response = self.client.post(self.url, query, follow=True)

            after_count = Department.objects.all().count()

            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.context['form'].errors) == 0)
            self.assertEquals(before_count + 1, after_count)

    def test_add_department_bad_one_by_one(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        departments = Department.objects.all()

        class Pointer:
            def __init__(self, value=None):
                self.value = value

        good_data_array = [test_data.valid_department_names[0]]

        name_ptr = Pointer(good_data_array[0])

        invalid_data_list_array = [test_data.invalid_department_names]

        pointers_array = [name_ptr]

        for h in range(len(pointers_array)):

            for i in range(len(invalid_data_list_array[h])):

                before_count = User.objects.all().count()

                pointers_array[h].value = invalid_data_list_array[h][i]

                query = make_add_department_form_query(name_ptr.value)

                response = self.client.post(self.url, query, follow=True)

                after_count = User.objects.all().count()

                self.assertEqual(response.status_code, 200)

                self.assertTrue(len(response.context['form'].errors) == 1)
                self.assertEquals(before_count, after_count)

            pointers_array[h].value = good_data_array[h]

    def test_filter(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        methods = ['filter', 'search']
        current_departments = Department.objects.all()

        for h in range(len(methods)):
            for i in range(len(current_departments)):

                query = make_department_filter_query(
                    methods[h],
                    current_departments[i].id,
                    current_departments[i].name,
                )

                response = self.client.get(self.url, data=query)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_filter_one_by_one(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        methods = ['filter', 'search']

        class Pointer:
            def __init__(self, value=None):
                self.value = value

        # ORDER: id, name
        data_array = [
            '7389027858979',
            "JKDFJG897'34%£HU80£$%jiogdjhioui653iuoj89&*(&)",
        ]

        id_ptr = Pointer(data_array[0])
        name_ptr = Pointer(data_array[1])

        pointers_array = [id_ptr, name_ptr]

        for g in range(len(methods)):
            for h in range(len(pointers_array)):

                query = make_department_filter_query(
                    methods[g], id_ptr.value, name_ptr.value
                )

                # First with no filter to get before count
                response = self.client.get(self.url)

                before_page_count = response.context[
                    'page_obj'
                ].paginator.num_pages

                response = self.client.get(
                    self.url, data={'page': before_page_count}
                )

                before_last_page_count = len(response.context['page_obj'])

                # Now with the filter to get after count
                response = self.client.get(self.url, data=query)

                after_page_count = response.context[
                    'page_obj'
                ].paginator.num_pages

                response = self.client.get(
                    self.url, data=query.update({'page': after_page_count})
                )

                after_last_page_count = len(response.context['page_obj'])

                self.assertEqual(response.status_code, 200)

                if before_page_count != after_page_count:
                    self.assertTrue(
                        after_last_page_count != before_last_page_count
                    )

                pointers_array[h].value = ''

    def test_edit_redirect(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        department_id = Department.objects.all()[0].id

        query = {'edit': str(department_id)}

        response = self.client.post(self.url, data=query)

        self.assertRedirects(
            response,
            reverse('edit_department', kwargs={'pk': str(department_id)}),
            status_code=302,
            target_status_code=200,
        )

    def test_good_delete(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        department_id = Department.objects.all()[0].id

        query = {'delete': str(department_id)}

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)

        department = get_department(department_id)

        self.assertEqual(department, None)

    def test_delete_bad_department_selected(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        query = query = {'delete': '75839758986'}

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['messages']) > 0)
