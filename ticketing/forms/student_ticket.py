from ticketing.models import Ticket, StudentMessage
from django import forms


class StudentTicketForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, max_length=500)

    def custom_save(self, student, department, header, content):
        ticket = Ticket.objects.create(
            student=student, department=department, header=header
        )
        StudentMessage.objects.create(ticket=ticket, content=content)

    class Meta:
        model = Ticket
        fields = ['header', 'department']
