from ticketing.utility import form_fields
from ticketing.models import User

from django import forms

import copy


class UserDepartmentFormMixin:
    def __init__(self, data=None, *args, **kwargs):

        super().__init__(data=data, *args, **kwargs)

        if data != None:
            if data.get(self.role_field_name) == User.Role.SPECIALIST:
                self.fields[self.department_field_name].disabled = False

    def clean(self):

        super().clean()

        if self.cleaned_data.get(self.role_field_name) == User.Role.SPECIALIST:
            if self.cleaned_data.get(self.department_field_name) == None:
                self.add_error(
                    self.department_field_name,
                    'You have not selected a user department',
                )


class ExtendedUserFormMixin:
    def __init__(self, *args, **kwargs):

        self.base_fields.update(
            {
                # Role field
                self.role_field_name: form_fields.make_role_radio_select(
                    True, self.department_field_name
                ),
                # Department field
                self.department_field_name: form_fields.department,
            }
        )

        super().__init__(*args, **kwargs)

        # user = self.instance

        # self.initial.update({self.role_field_name: user.role})

    def save(self, commit=True):
        self.instance.role = self.cleaned_data[self.role_field_name]

        return super().save(commit)
