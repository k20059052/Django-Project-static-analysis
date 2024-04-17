from django import forms
from ticketing.models.faq import FAQ
from ticketing.models.departments import Subsection

# TODO create a choice fields.
class FAQForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super(FAQForm, self).__init__(*args, **kwargs)
        if department:
            self.department = department
            subsections = Subsection.objects.filter(department=self.department)
            self.fields['subsection'] = forms.ChoiceField(
                choices=[(s.id, s.name) for s in subsections],
                label='Select the Subsection',
            )
        

    def custom_save(
        self, specialist, department, question, subsection, answer
    ):
        FAQ.objects.create(
            specialist=specialist,
            department=department,
            subsection=subsection,
            question=question,
            answer=answer,
        )

    def clean(self):
        cleaned_data = super().clean()
        subsection_id = cleaned_data.get('subsection')
        if isinstance(subsection_id, str):
            try:
                subsection_obj = Subsection.objects.get(id=int(subsection_id))
                cleaned_data['subsection'] = subsection_obj
            except Subsection.DoesNotExist:
                self.add_error('subsection', 'Invalid subsection selected')
        elif isinstance(subsection_id, Subsection):
            try:
                subsection_obj = subsection_id
                cleaned_data['subsection'] = subsection_obj
            except Subsection.DoesNotExist:
                self.add_error('subsection', 'Invalid subsection selected')
        return cleaned_data

    class Meta:
        model = FAQ
        fields = ['question', 'subsection', 'answer']
        widgets = {
            'question': forms.TextInput(),
            'answer': forms.Textarea(),
        }
