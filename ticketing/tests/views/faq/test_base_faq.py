from django.test import TestCase
from django.urls import reverse
from ticketing.models import Department
from django.utils.text import slugify

class BaseFaqTestCase(TestCase):
    def setUp(self):
        self.url=reverse('faq')
        self.department_1=Department.objects.create(name='Health and Safety',slug=slugify('Health and Safety'))
        self.url_redirect_1=reverse('department_faq',kwargs={'department':self.department_1.slug})
        self.department_2=Department.objects.create(name='Technology Support',slug=slugify('Technology Support'))
        self.url_redirect_2=reverse('department_faq',kwargs={'department':self.department_2.slug})
        self.department_3=Department.objects.create(name='Mitigating Circumstances',slug=slugify('Mitigating Circumstances'))
        self.url_redirect_3=reverse('department_faq',kwargs={'department':self.department_3.slug})
    def test_base_faq_url_resolves(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_base_faq_uses_correct_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertIn(self.department_1.name, [department_1.name for department_1 in response.context['object_list']])
        self.assertIn(self.department_1.slug,[department_1.slug for department_1 in response.context['object_list']])
        self.assertIn(self.department_2.name, [department_2.name for department_2 in response.context['object_list']])
        self.assertIn(self.department_2.slug,[department_2.slug for department_2 in response.context['object_list']])
        self.assertIn(self.department_3.name, [department_3.name for department_3 in response.context['object_list']])
        self.assertIn(self.department_3.slug,[department_3.slug for department_3 in response.context['object_list']])
    
    def test_base_faq_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'faq/faq.html')
        self.assertTemplateUsed(response, 'partials/header.html')
        self.assertTemplateUsed(response,'partials/pagination.html')
        self.assertTemplateUsed(response, 'partials/footer.html')



        
       
    