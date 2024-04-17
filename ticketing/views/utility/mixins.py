from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
import copy


class ExtendableFormViewMixin:
    def custom_get_form_kwargs(self):
        _kwargs = super().get_form_kwargs()

        # print("GOT KWARGS: THE DATA IS: ", _kwargs)

        _kwargs.pop('data', None)
        _kwargs.pop('files', None)

        # print("GOT KWARGS: THE DATA AFTERRRRR IS: ", _kwargs)

        return _kwargs

    def fixed_post(self, request, *args, **kwargs):
        # The class that uses this Mixin will be inheriting from FormView. Therefore, every time that super().post is
        # run, the form that FormView manages for us is automatically validated and submitted. This happens
        # regardless of what keys the post data dictionary contains. This is a problem because
        # if, for example, we make a POST request to delete a department, then, as a side effect, the create department
        # form will be validated even though the user
        # did not interact with it, and it will display an error (since the user would not have input anything into it).
        # To fix this we need to dynamically change the function pointer of get_form_kwargs for all post types
        # that do not concern the creation form (e.g. edit, delete), so that we can stop the POST data being
        # passed to the form and hence stop the form from trying to validate and submit. We can't statically override
        # get_form_kwargs in the current class because then we will always be removing the POST data from the form,
        # even when we want to actually use the form.

        old_get_form_kwargs = self.get_form_kwargs
        self.get_form_kwargs = self.custom_get_form_kwargs
        result = super().post(request, *args, **kwargs)
        self.get_form_kwargs = old_get_form_kwargs
        return result


class DynamicCustomFormClassMixin:
    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        # self.form_class_maker is bound to pass self automatically so use __func__ to just get the pure
        # function pointer
        _class = self.form_class_maker.__func__(form_class)
        form = _class(**self.get_form_kwargs())
        return form


class FilterView:
    def setup(self, request):
        super().setup(request)
        self.filter_form = self.filter_form_class(request.GET)
        initial = copy.copy(request.GET)
        get_filter_method = initial.get('filter_method', None)
        if (
            get_filter_method == None
            and self.filter_form_class.offer_filter_method == True
        ):
            get_filter_method = 'filter'
            initial['filter_method'] = get_filter_method

        self.filter_form = self.filter_form_class(initial)
        self.filter_data = {}
        # We need to run is_valid so that we can get the cleaned data
        self.result = self.filter_form.is_valid()
        self.filter_method = self.filter_form.cleaned_data.get(
            'filter_method', 'filter'
        )
        for field_name in self.filter_form.base_fields:
            self.filter_data.update(
                {
                    field_name: self.filter_form.cleaned_data.get(
                        field_name, None
                    )
                }
            )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'filter_form': self.filter_form})
        return context
