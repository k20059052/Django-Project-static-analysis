from ticketing.utility.user import *
from ticketing.models import User
from ticketing.forms.utility.mixins import (
    UserDepartmentFormMixin,
    ExtendedUserFormMixin,
)
from ticketing.utility.model import *


def make_edit_user_form_class(generated_form_class):
    class EditUserForm(
        ExtendedUserFormMixin, UserDepartmentFormMixin, generated_form_class
    ):
        department_field_name = 'edit_department'
        role_field_name = 'edit_role'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            user = self.instance

            if user.role == User.Role.SPECIALIST:
                self.fields[self.department_field_name].disabled = False

                self.initial.update(
                    {self.department_field_name: get_user_department(user)}
                )

            self.initial.update({self.role_field_name: user.role})

        def save(self, commit=True):

            update_specialist_department(
                self.instance,
                self.instance.role,
                self.cleaned_data[self.role_field_name],
                self.cleaned_data[self.department_field_name],
            )

            return super().save(commit=commit)

    return EditUserForm
