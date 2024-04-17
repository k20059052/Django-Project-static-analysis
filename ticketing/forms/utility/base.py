from ticketing.utility import form_fields
from ticketing.models import User

from django import forms

import copy


class FilterForm(forms.Form):
    offer_filter_method = False
