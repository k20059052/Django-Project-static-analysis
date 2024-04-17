from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from ticketing.models.departments import Subsection
from ticketing.models import *
from datetime import *
from faker import Faker
import random
import json
from random import shuffle


class Command(BaseCommand):
    # constant
    SUBSECTIONS = [
        'Contact',
        'What to do',
    ]
    STUDENT_COUNT = 100
    SPECIALIST_COUNT = 0
    DEPARTMENT_COUNT = 0
    # can configure this
    SPECIALIST_PER_DEPARTMENT_COUNT = 3
    DIRECTOR_COUNT = 3
    PASSWORD = 'Password@123'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        User.objects.all().delete()
        Department.objects.all().delete()
        SpecialistDepartment.objects.all().delete()
        SpecialistInbox.objects.all().delete()
        Subsection.objects.all().delete()
        SpecialistMessage.objects.all().delete()
        FAQ.objects.all().delete()

        self.create_student()
        print('students done')

        self.create_director()
        print('directors done')

        self.create_fixed_users()
        print('fixed users done')

        self.create_department()
        print('department done')

        self.create_specialist()
        print('specialist done')
        self.create_subsections()
        print('subsections done')

        self.create_specialist_department()
        print('specialist set to department')

        self.create_FAQs()
        print('create FAQs')

        self.create_student_ticket()
        print('student ticket done')

        self.create_specialist_inbox()
        print('specialist inbox done')

        self.create_open_department_ticket()
        print('open department tickets done')

        self.create_closed_department_ticket()
        print('closed department tickets done')
        


    def set_up(self):
        first_name = self.faker.unique.first_name()
        last_name = self.faker.unique.last_name()
        email = (f'{first_name}.{last_name}@example.com').lower()
        return [first_name, last_name, email]

    def create_fixed_users(self):
        self.create_fixed_student()
        self.create_fixed_specialist()
        self.create_fixed_director()

    def create_fixed_student(self):
        student_first_name = 'test'
        student_last_name = 'student'
        student_email = 'test.student@example.com'

        student = User.objects.create_user(
            email=student_email,
            password=self.PASSWORD,
            first_name=student_first_name,
            last_name=student_last_name,
        )

    def create_fixed_specialist(self):
        specialist_first_name = 'test'
        specialist_last_name = 'specialist'
        specialist_email = 'test.specialist@example.com'

        specialist = User.objects.create_specialist(
            email=specialist_email,
            password=self.PASSWORD,
            first_name=specialist_first_name,
            last_name=specialist_last_name,
        )

    def create_fixed_director(self):
        director_first_name = 'test'
        director_last_name = 'director'
        director_email = 'test.director@example.com'

        director = User.objects.create_director(
            email=director_email,
            password=self.PASSWORD,
            first_name=director_first_name,
            last_name=director_last_name,
        )

    def create_department(self):
        with open('ticketing/management/commands/faqs.json') as json_file:
            data = json.load(json_file)
            for dept in data['departments']:
                department_name = dept['department']
                department, _ = Department.objects.get_or_create(
                    name=department_name
                )
        self.DEPARTMENT_COUNT = Department.objects.count()

    def create_subsections(self):
        with open('ticketing/management/commands/faqs.json') as json_file:
            data = json.load(json_file)
            for dept in data['departments']:
                department_name = dept['department']
                department, _ = Department.objects.get_or_create(
                    name=department_name
                )
                for sub_sec in dept['sub_sections']:
                    subsection_name = sub_sec['sub_section']
                    Subsection.objects.get_or_create(
                        name=subsection_name, department=department
                    )

    def create_student(self):
        for _ in range(self.STUDENT_COUNT):
            info = self.set_up()
            User.objects.create_user(
                email=info[2],
                password=self.PASSWORD,
                first_name=info[0],
                last_name=info[1],
            )

    def create_specialist(self):
        self.SPECIALIST_COUNT = (
            self.SPECIALIST_PER_DEPARTMENT_COUNT * self.DEPARTMENT_COUNT
        )
        for _ in range(self.SPECIALIST_COUNT):
            info = self.set_up()
            User.objects.create_specialist(
                email=info[2],
                password=self.PASSWORD,
                first_name=info[0],
                last_name=info[1],
            )

    def create_director(self):
        for i in range(self.DIRECTOR_COUNT):
            info = self.set_up()
            User.objects.create_superuser(
                email=info[2],
                password=self.PASSWORD,
                first_name=info[0],
                last_name=info[1],
            )

    def create_student_ticket(self):
        for i in range(0,3): # WE WANT 3 TIMES THE TICKET FOR MANUAL TESTING PURPOSES
            for student in User.objects.filter(role=User.Role.STUDENT):
                self.create_ticket_for_student(student)

    def create_student_message(self, ticket):
        StudentMessage.objects.create(
            ticket=ticket, content=self.faker.text()[0:500]
        )

    def create_specialist_department(self):
        specialist_ids = list(
            User.objects.filter(role=User.Role.SPECIALIST).values_list(
                'id', flat=True
            )
        )
        assignments = []
        for department in Department.objects.all():
            # Assign the chunk of specialists
            chunk_size = self.SPECIALIST_COUNT // self.DEPARTMENT_COUNT
            chunk_ids = specialist_ids[:chunk_size]
            specialist_ids = specialist_ids[3:]
            # Create the specialist department assignments
            for spe_id in chunk_ids:
                specialist = User.objects.get(id=spe_id)
                assignments.append(
                    {
                        'specialist': specialist,
                        'department': department,
                    }
                )
        # Create the SpecialistDepartment instances
        for assignment in assignments:
            specialist_department = SpecialistDepartment(**assignment)
            specialist_department.save()

    def create_FAQs(self):
        with open('ticketing/management/commands/faqs.json') as json_file:
            data = json.load(json_file)
            for dept in data['departments']:
                department_name = dept['department']
                department = Department.objects.get(name=department_name)
                for sub_sec in dept['sub_sections']:
                    subsection_name = sub_sec['sub_section']
                    subsection = Subsection.objects.get(name=subsection_name)
                    for faq in sub_sec['faq']:
                        question = faq['question']
                        answer = faq['answer']
                        specialist = (
                            SpecialistDepartment.objects.filter(
                                department=department
                            )
                            .first()
                            .specialist
                        )
                        FAQ.objects.get_or_create(
                            specialist=specialist,
                            department=department,
                            subsection=subsection,
                            question=question,
                            answer=answer,
                        )

    def create_specialist_inbox(self):
        for department in Department.objects.all():
            specialists = User.objects.filter(
                id__in = SpecialistDepartment.objects.filter(
                    department=department
                ).values_list('specialist', flat=True)
            )
            tickets = Ticket.objects.filter(department=department)
            for ticket in tickets:
                rand_specialist = specialists[
                    random.randint(0, len(specialists) - 1)
                ]
                specialist_ticket = SpecialistInbox.objects.create(
                    specialist=rand_specialist, ticket=ticket
                )
                self.create_specialist_message(specialist_ticket)

    def create_specialist_message(self, specialist_ticket):
        SpecialistMessage.objects.create(
            ticket=specialist_ticket.ticket,
            content=self.faker.text()[0:500],
            responder=specialist_ticket.specialist,
        )

    def create_ticket_for_student(self, student):
        department_obj_list = Department.objects.all()
        rand_dep = department_obj_list[
            random.randint(0, self.DEPARTMENT_COUNT - 1)
        ]
        ticket = Ticket.objects.create(
            student=student,
            department=rand_dep,
            header=self.faker.sentence()[0:100],
        )
        self.create_student_message(ticket)

    def create_open_department_ticket(self):
        self.create_student_ticket()

    def create_closed_department_ticket(self):
        for student in User.objects.filter(role=User.Role.STUDENT):
            department_obj_list = Department.objects.all()
            rand_dep = department_obj_list[
                random.randint(0, self.DEPARTMENT_COUNT - 1)
            ]
            ticket = Ticket.objects.create(
                student=student,
                department=rand_dep,
                header=self.faker.sentence()[0:100],
                status=Ticket.Status.CLOSED,
            )
            self.create_student_message(ticket)