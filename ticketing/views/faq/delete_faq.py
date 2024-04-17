from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import DeleteView
from ticketing.models.faq import FAQ
from django.http import HttpResponseRedirect


class FAQDeleteView(DeleteView):
    model = FAQ
    success_url = reverse_lazy('specialist_department_faq')
