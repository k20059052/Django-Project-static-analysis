from ticketing.utility import form_fields
from ticketing.models import User
from ticketing.utility.department import get_department
from ticketing.forms.utility.mixins import (
    UserDepartmentFormMixin,
    ExtendedUserFormMixin,
)
from ticketing.models.specialist import SpecialistDepartment
from ticketing.forms.utility.base import FilterForm

from django import forms

import copy


class SpecialistInboxFilterForm(FilterForm):
    email = forms.CharField(label=form_fields.email.label, required=False)

    header = forms.CharField(label='Header', required=False)

    offer_filter_method = True
    filter_method = form_fields.filter_method
