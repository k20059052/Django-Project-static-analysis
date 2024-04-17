from ticketing.utility import form_fields
from ticketing.models import User
from ticketing.utility.department import get_department
from ticketing.forms.utility.mixins import (
    UserDepartmentFormMixin,
    ExtendedUserFormMixin,
)
from ticketing.forms.utility.base import FilterForm
from ticketing.models.specialist import SpecialistDepartment

from django import forms

import copy


class DepartmentFilterForm(FilterForm):
    id = copy.copy(form_fields.id)
    id.required = False

    name = copy.copy(form_fields.department_name)
    name.required = False

    offer_filter_method = True
    filter_method = form_fields.filter_method
