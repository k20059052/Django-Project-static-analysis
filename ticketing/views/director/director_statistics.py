from django.contrib.auth.decorators import login_required
from ticketing.decorators import roles_allowed
from django.views.generic import View, ListView
from django.shortcuts import get_object_or_404
from ticketing.models import *
from django.shortcuts import render, redirect
import sys
import datetime
import time
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin


class DirectorStatisticsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'director_statistics.html'
    required_roles = ['DI']
    def get_queryset(self):
        user = self.request.user
        facts = [{
                    "title": "Department Information",
                    "data": [
                            {
                                "name": "Number of departments",
                                "value": self.get_number_of_departments()
                            },
                            {
                                "name": "Number of tickets",
                                "value": self.get_total_number_of_tickets()
                            },
                            {   
                                "name": "Department with most answered tickets",
                                "value": self.get_name_of_department_with_most_answered_tickets()
                    
                            },
                            {
                                "name": "Department with most unanswered tickets",
                                "value": self.get_name_of_department_with_least_answered_tickets()
                            }   
                        ]
                   },
                   {
                        "title": "Specialist Information",
                        "data": [
                            {
                                "name": "Average response time",
                                "value": self.get_average_response_time()
                            },
                            {
                                "name": "Average Messages per Ticket",
                                "value": self.get_average_number_of_messages_per_ticket()
                            }
                        ]

                   }
                   ]
        
        return facts
    def get_number_of_departments(self):
        return Department.objects.count()
    
    def get_name_of_department_with_most_answered_tickets(self):
        current_max_department = None
        max_count = 0
        for department in Department.objects.all():
            ticket_count = Ticket.objects.filter(department = department, status = Ticket.Status.CLOSED).count() 
            if(ticket_count > max_count):
                max_count = ticket_count
                current_max_department = department
        return current_max_department
    
    def get_total_number_of_tickets(self):
        return Ticket.objects.all().count()
    
    def get_name_of_department_with_least_answered_tickets(self):
        current_min_department = None
        min_count = sys.maxsize
        for department in Department.objects.all():
            ticket_count = Ticket.objects.filter(department = department, status = Ticket.Status.OPEN).count() 
            if(ticket_count < min_count):
                min_count = ticket_count
                current_min_department = department
        return current_min_department
    
    def get_average_response_time(self):
        total_time = datetime.timedelta()
        counter = 0
        for ticket in Ticket.objects.all():
            messages = SpecialistMessage.objects.filter(ticket=ticket).order_by('-date_time')
            specialist_message = None
            if messages:
                counter += 1
                specialist_message = messages[0]
                student_message = StudentMessage.objects.filter(ticket=ticket).order_by('-date_time')[0]
                total_time += specialist_message.date_time - student_message.date_time
        if counter == 0:
            return "N/A"
        else:
            # return total_time / counter
            time = total_time / counter
            hours = time.total_seconds() // (60*60)
            mins = (time.total_seconds() - (hours*60*60) ) // 60
            secs = (time.total_seconds() - (hours*60*60) - (mins*60)) 
            return f"{hours} hours {mins} mins { round(secs, 1)} secs"
           
    
    def get_average_number_of_messages_per_ticket(self):
        number_of_tickets = Ticket.objects.count()
        number_of_messages = Message.objects.count()
        if number_of_tickets == 0:
            return 0
        else:
            return round(number_of_messages / number_of_tickets,2)
        
   
        