from django.test import TestCase, RequestFactory
from django.urls import reverse
from ticketing.models import FAQ, Department, User, SpecialistDepartment, Subsection
from django.utils.text import slugify
from ticketing.views.faq.specialist_department_faq import SpecialistDepartmentFaq
from django.http import Http404
from django.shortcuts import get_object_or_404



class SpecialistDepartmentFaqTestCase(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Health and Safety', slug=slugify('Health and Safety')
        )
        self.specialist = User.objects.create_specialist(
            email='john.doe@email.com',
            first_name='John',
            last_name='Doe',
            password='password@123',
        )
        self.specialist_dept = SpecialistDepartment.objects.create(
            department=self.department, specialist=self.specialist
        )

        self.subsection = Subsection.objects.create(
            department = self.department,
            name = "subsection_name"
        )
        self.faq = FAQ.objects.create(
            department=self.department,
            subsection=self.subsection,
            specialist=self.specialist,
            question='What is 9+10',
            answer='19',
        )
        self.slug_string = slugify('Health and Safety')
        self.url = reverse(
            'department_faq', kwargs={'department': self.department.slug}
        )
        self.factory = RequestFactory()

    def test_faq_slug(self):
        slugged_string = slugify('Mitigating Circumstances')
        department = Department.objects.create(
            name='Mitigating Circumstances',
            slug=slugify('Mitigating Circumstances'),
        )
        self.assertEquals(slugged_string, department.slug)
        self.assertEquals(self.slug_string, self.faq.department.slug)

    def test_specialist_department_faq_url_resolves(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_specialist_department_faq_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'faq/department_faq.html')
        self.assertTemplateUsed(response, 'partials/header.html')
        self.assertTemplateUsed(response, 'partials/footer.html')

    def test_specialist_department_faq_uses_correct_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.faq.question,
            [faq.question for faq in response.context['object_list']],
        )
        self.assertIn(
            self.faq.answer,
            [faq.answer for faq in response.context['object_list']],
        )

    def test_specialist_department_faq_view_contains_question_answer_text(
        self,
    ):
        response = self.client.get(self.url)
        self.assertContains(response, 'What is 9+10')
        self.assertContains(response, '19')

    def test_specialist_department_faq_view_contains_answer_text(self):
        response = self.client.get(self.url)
        self.assertContains(response, '19')

    def test_specialist_department_faq_view_no_pagination(self):
        url = reverse(
            'department_faq', kwargs={'department': self.department.slug}
        )
        response = self.client.get(url)
        self.assertEqual(len(response.context['object_list']), 1)
        FAQ.objects.create(
            department=self.department,
            subsection=self.subsection,
            specialist=self.specialist,
            question='Why am I tired?',
            answer='Get some sleep',
        )
        url = reverse(
            'department_faq', kwargs={'department': self.department.slug}
        )
        response = self.client.get(url)
        self.assertEqual(len(response.context['object_list']), 2)
        FAQ.objects.get(question='Why am I tired?').delete()
        url = reverse(
            'department_faq', kwargs={'department': self.department.slug}
        )
        response = self.client.get(url)
        self.assertEqual(len(response.context['object_list']), 1)

    def test_specialist_department_faq_view_get_queryset(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        queryset = response.context_data['object_list']
        self.assertQuerysetEqual(
            queryset,
            FAQ.objects.filter(department=self.department).order_by('id'),
        )

    def test_specialist_department_faq_view_returns_404_if_no_object_found(
        self,
    ):
        specialist_dept = SpecialistDepartment.objects.get(
            department=self.department
        ).department
        with self.assertRaises(Http404):
            get_object_or_404(Department, id=specialist_dept.id + 1)

    def test_specialist_department_faq_view_returns_404_if_object_found(self):
        object = get_object_or_404(Department, id=self.department.id)
        self.assertEqual(object, self.department)

    def test_get_context_data(self):
        request = self.factory.get(self.url)
        request.user = self.specialist
        response = SpecialistDepartmentFaq.as_view()(request)
        self.assertQuerysetEqual(
            response.context_data['object_list'],
            FAQ.objects.filter(specialist=self.specialist),
        )