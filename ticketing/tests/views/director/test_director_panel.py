from django.test import TestCase, Client
from django.urls import reverse
from ticketing.models import User, Department
from ticketing.tests.helpers import reverse_with_next
from ticketing.tests.utility import test_data
from ticketing.utility.user import *


def make_director_command_query(role, department, selected):
    return {
        'set_role': 'Set Account Role',
        'commands_role': role,
        'commands_department': department,
        'select': selected,
    }


def make_director_filter_query(
    method, id, first_name, last_name, email, role, department
):
    return {
        'filter_method': method,
        'id': id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'role': role,
        'filter_department': department,
    }


def make_add_user_form_query(
    email, first_name, last_name, password, confirm_password, role, department
):
    return {
        'add': 'Add',
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password1': password,
        'password2': confirm_password,
        'add_role': role,
        'add_department': department,
    }


class DirectorPanelTestCase(TestCase):

    fixtures = [
        'ticketing/tests/fixtures/user_fixtures.json',
        'ticketing/tests/fixtures/message_fixtures.json',
        'ticketing/tests/fixtures/ticket_fixtures.json',
        'ticketing/tests/fixtures/department_fixtures.json',
        'ticketing/tests/fixtures/specialist_inbox_fixtures.json',
        'ticketing/tests/fixtures/specialist_department_fixtures.json',
    ]

    def setUp(self):
        self.url = reverse('director_panel')

        self.specialist = User.objects.filter(role='SP').first()
        self.student = User.objects.filter(role='ST').first()
        self.director = User.objects.filter(role='DI').first()

        self.non_login_director = (
            User.objects.all()
            .exclude(id=self.director.id)
            .filter(role='DI')
            .first()
        )

    def test_dp_dashboard_url(self):
        self.assertEqual(self.url, '/director_panel/')

    def test_get_dp_dashboard_as_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.student.email, password='Password@123'
        )

        self.assertTrue(loggedin)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_dp_dashboard_as_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )
        self.assertTrue(loggedin)

        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'director/director_panel.html')

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

    def test_add_user_good(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        departments = Department.objects.all()

        # Emails must be unique so only make as many users as emails to avoid looping on emails
        for i in range(len(test_data.valid_emails)):

            before_count = User.objects.all().count()

            email = test_data.valid_emails[i % len(test_data.valid_emails)]
            first_name = test_data.valid_first_names[
                i % len(test_data.valid_first_names)
            ]
            last_name = test_data.valid_last_names[
                i % len(test_data.valid_last_names)
            ]
            password = test_data.valid_passwords[
                i % len(test_data.valid_passwords)
            ]
            confirm_password = password
            role = test_data.valid_roles[i % len(test_data.valid_roles)]

            if role == User.Role.SPECIALIST:
                department = str(departments[i % len(departments)].id)
            else:
                department = ''

            query = make_add_user_form_query(
                email,
                first_name,
                last_name,
                password,
                confirm_password,
                role,
                department,
            )

            # print("EMAIL IS: ", email)
            # print("PASSWORD IS: ", password)
            response = self.client.post(self.url, query, follow=True)

            # print("FORM ERRORS: ", response.context["form"].errors)

            after_count = User.objects.all().count()

            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.context['form'].errors) == 0)
            self.assertEquals(before_count + 1, after_count)

    def test_add_user_bad_one_by_one(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        departments = Department.objects.all()

        class Pointer:
            def __init__(self, value=None):
                self.value = value

        # ORDER: email, first_name, last_name, password, confirm_password, role, department
        good_data_array = [
            test_data.valid_emails[0],
            test_data.valid_first_names[0],
            test_data.valid_last_names[0],
            test_data.valid_passwords[0],
            test_data.valid_passwords[0],
            User.Role.STUDENT,
            '',
        ]

        email_ptr = Pointer(good_data_array[0])
        first_name_ptr = Pointer(good_data_array[1])
        last_name_ptr = Pointer(good_data_array[2])
        password_ptr = Pointer(good_data_array[3])
        confirm_password_ptr = Pointer(good_data_array[4])
        role_ptr = Pointer(good_data_array[5])
        department_ptr = Pointer(good_data_array[6])

        invalid_data_list_array = [
            test_data.invalid_emails,
            test_data.invalid_first_names,
            test_data.invalid_last_names,
            test_data.invalid_passwords,
            test_data.invalid_passwords,
            test_data.invalid_roles,
            [
                'JOIDFJGIODFJIOJEOIGUOIhiojhiohioue8957895u38o4579843^@$%^$%£^£$%^£%$'
            ],
        ]

        pointers_array = [
            email_ptr,
            first_name_ptr,
            last_name_ptr,
            password_ptr,
            confirm_password_ptr,
            role_ptr,
            department_ptr,
        ]

        def department_special_action_before():
            role_ptr.value = User.Role.SPECIALIST

        def department_special_action_after():
            role_ptr.value = good_data_array[5]

        special_action_before_array = [
            None,
            None,
            None,
            None,
            None,
            None,
            department_special_action_before,
        ]
        special_action_after_array = [
            None,
            None,
            None,
            None,
            None,
            None,
            department_special_action_after,
        ]

        for h in range(len(pointers_array)):

            if special_action_before_array[h] != None:
                special_action_before_array[h]()

            for i in range(len(invalid_data_list_array[h])):

                before_count = User.objects.all().count()

                # print("ORIGINAL PTR VALUE: ", pointers_array[h].value)
                pointers_array[h].value = invalid_data_list_array[h][i]
                # print("AFTER PTR VALUE: ", pointers_array[h].value)

                query = make_add_user_form_query(
                    email_ptr.value,
                    first_name_ptr.value,
                    last_name_ptr.value,
                    password_ptr.value,
                    confirm_password_ptr.value,
                    role_ptr.value,
                    department_ptr.value,
                )

                response = self.client.post(self.url, query, follow=True)

                # print("FORM ERRORS: ", response.context["form"].errors)

                after_count = User.objects.all().count()

                self.assertEqual(response.status_code, 200)

                # print("FORM ERRORS IS: ", len(response.context["form"].errors))
                # print("FORM ERRORS: ", response.context["form"].errors)
                # print("QUERY IS: ", query)
                self.assertTrue(len(response.context['form'].errors) == 1)
                self.assertEquals(before_count, after_count)

                # if special_action_before_array[h] != None:
                #     special_action_before_array[h]()

            pointers_array[h].value = good_data_array[h]

            if special_action_after_array[h] != None:
                special_action_after_array[h]()

    def test_add_user_bad_all(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        departments = Department.objects.all()

        before_count = User.objects.all().count()

        email = test_data.invalid_emails[0]
        first_name = test_data.invalid_first_names[0]
        last_name = test_data.invalid_last_names[0]
        password = test_data.invalid_passwords[0]
        # Make confirm password different
        confirm_password = test_data.invalid_passwords[1]
        role = test_data.invalid_roles[0]
        department = ['iogjhieojgiodfshgiouiouo7*&*(65786)']

        query = make_add_user_form_query(
            email,
            first_name,
            last_name,
            password,
            confirm_password,
            role,
            department,
        )

        response = self.client.post(self.url, query, follow=True)

        after_count = User.objects.all().count()

        self.assertEqual(response.status_code, 200)
        # print("FORM ERRORS IS ", response.context["form"].errors)
        # print("***** ERRRO COUNT IS: ", len(response.context["form"].errors))
        self.assertTrue(len(response.context['form'].errors) == 5)
        self.assertEquals(before_count, after_count)

    def test_filter(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        methods = ['filter', 'search']
        current_users = User.objects.all()

        for h in range(len(methods)):
            for i in range(len(current_users)):
                department = get_user_department(current_users[i].id)

                if department == None:
                    department = ''

                query = make_director_filter_query(
                    methods[h],
                    current_users[i].id,
                    current_users[i].first_name,
                    current_users[i].last_name,
                    current_users[i].email,
                    current_users[i].role,
                    department,
                )

                response = self.client.get(self.url, data=query)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_filter_one_by_one(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        # departments = Department.objects.all()

        methods = ['filter', 'search']

        class Pointer:
            def __init__(self, value=None):
                self.value = value

        # ORDER: id, first_name, last_name, email, role, department
        data_array = [
            '7389027858979',
            'JDFGIOUO43%£834598V',
            'kldfgjkli3u45£$gs34',
            'dfgj@£$fssgildj@dg789.co.uk',
            User.Role.DIRECTOR,
            Department.objects.all()[1],
        ]

        id_ptr = Pointer(data_array[0])
        first_name_ptr = Pointer(data_array[1])
        last_name_ptr = Pointer(data_array[2])
        email_ptr = Pointer(data_array[3])
        role_ptr = Pointer(data_array[4])
        department_ptr = Pointer(data_array[5])

        pointers_array = [
            id_ptr,
            first_name_ptr,
            last_name_ptr,
            email_ptr,
            role_ptr,
            department_ptr,
        ]

        for g in range(len(methods)):
            for h in range(len(pointers_array)):

                query = make_director_filter_query(
                    methods[g],
                    id_ptr.value,
                    first_name_ptr.value,
                    last_name_ptr.value,
                    email_ptr.value,
                    role_ptr.value,
                    department_ptr.value,
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

    def test_commands_good_student(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        query = make_director_command_query(User.Role.STUDENT, '', selected)

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)

        for id in selected:
            user = get_user(int(id))

            self.assertEqual(user.role, User.Role.STUDENT)
            self.assertEqual(get_user_department(user), None)

    def test_commands_good_director(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        query = make_director_command_query(User.Role.DIRECTOR, '', selected)

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)

        for id in selected:
            user = get_user(int(id))

            self.assertEqual(user.role, User.Role.DIRECTOR)
            self.assertEqual(get_user_department(user), None)

    def test_commands_good_specialist(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        department = Department.objects.all().first()

        query = make_director_command_query(
            User.Role.SPECIALIST, str(department.id), selected
        )

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)

        for id in selected:
            user = get_user(int(id))

            self.assertEqual(user.role, User.Role.SPECIALIST)
            self.assertTrue(get_user_department(user).id == department.id)

    def test_commands_bad_role(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        department = Department.objects.all().first()

        query = make_director_command_query(
            'iduhugiuoh', str(department.id), selected
        )

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['commands_form'].errors) > 0)

    def test_commands_no_role(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        department = Department.objects.all().first()

        query = make_director_command_query('', str(department.id), selected)
        query.pop('commands_role')

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['messages']) > 0)

    def test_commands_no_users_selected(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        department = Department.objects.all().first()

        query = make_director_command_query(User.Role.STUDENT, '', [])

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['messages']) > 0)

    def test_commands_bad_user_selected(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
            '758937563487658',
            'jidfogjjoi',
        ]

        department = Department.objects.all().first()

        query = make_director_command_query(User.Role.STUDENT, '', selected)

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['messages']) > 0)

    def test_commands_bad_department(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        current_users = User.objects.all()

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        department = Department.objects.all().first()

        query = make_director_command_query(
            User.Role.SPECIALIST, '89345787534', selected
        )

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['commands_form'].errors) > 0)

    def test_edit_redirect(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        query = {'edit': str(self.student.id)}

        response = self.client.post(self.url, data=query)

        self.assertRedirects(
            response,
            reverse('edit_user', kwargs={'pk': str(self.student.id)}),
            status_code=302,
            target_status_code=200,
        )

    def test_password_redirect(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        query = {'password': str(self.student.id)}

        response = self.client.post(self.url, data=query)

        self.assertRedirects(
            response,
            reverse('change_password', kwargs={'pk': str(self.student.id)}),
            status_code=302,
            target_status_code=200,
        )

    def test_commands_good_delete(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
        ]

        query = {'delete': 'Delete', 'select': selected}

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)

        for id in selected:
            user = get_user(int(id))

            self.assertEqual(user, None)

    def test_commands_delete_bad_user_selected(self):
        self.client = Client()
        loggedin = self.client.login(
            email=self.director.email, password='Password@123'
        )

        selected = [
            str(self.student.id),
            str(self.specialist.id),
            str(self.non_login_director.id),
            '758937563487658',
            'jidfogjjoi',
        ]

        query = query = {'delete': 'Delete', 'select': selected}

        response = self.client.post(self.url, data=query)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['messages']) > 0)
