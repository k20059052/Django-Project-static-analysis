from ticketing.models import User, Department
from ticketing.utility import custom_widgets
from ticketing.forms import SignupForm
from django import forms
import copy

id = forms.IntegerField(label='ID')

first_name = User._meta.get_field('first_name').formfield()
first_name.label = 'First Name'

last_name = User._meta.get_field('last_name').formfield()
last_name.label = 'Last Name'

email_unique = User._meta.get_field('email').formfield()

email = copy.copy(email_unique)
email.unique = False

password = SignupForm().fields['password1']
confirm_password = SignupForm().fields['password2']


base_role = forms.ChoiceField(
    choices=[
        (User.Role.STUDENT, 'Student'),
        (User.Role.SPECIALIST, 'Specialist'),
        (User.Role.DIRECTOR, 'Director'),
    ],
    widget=custom_widgets.RoleRadioSelect(department_select_name=''),
    label='Account Role:',
    required=True,
)


def make_role_radio_select(linked, department_select_name=''):
    role = copy.deepcopy(base_role)
    role.widget.department_select_name = department_select_name
    role.widget.linked_to_select = linked
    return role


department = forms.ModelChoiceField(
    queryset=Department.objects.all(),
    widget=custom_widgets.StyledSelect,
    required=False,
)
department.label = 'Department'
department.disabled = True

department_name = Department._meta.get_field('name').formfield()

filter_method = forms.ChoiceField(
    choices=[('filter', 'Filter'), ('search', 'Search')],
    widget=custom_widgets.NoLabelStyledRadioSelect(),
    label='',
    required=True,
)