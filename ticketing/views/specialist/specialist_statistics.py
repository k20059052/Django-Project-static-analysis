from django.contrib.auth.decorators import login_required
from ticketing.decorators import roles_allowed
from django.views.generic import View, ListView
from django.shortcuts import get_object_or_404
from ticketing.models import *
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from ticketing.mixins import RoleRequiredMixin

class SpecialistStatisticsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'specialist_statistics.html'
    required_roles = ['SP']
    

    def get_queryset(self):
        user = self.request.user
        facts = [{"title": "Ticket Counts",
                  "data": [{
                        "name": "Total tickets",
                        "value": self.get_number_of_total_tickets_per_department()
                    },
                    {
                        "name": "Open tickets",
                        "value": self.get_number_of_open_tickets()
                    },
                    {   
                        "name": "Closed tickets",
                        "value": self.get_number_of_closed_tickets()
            
                    },
                    ]
                   },
                   {
                        "title": "Ticket Responsiveness",
                        "data": [
                            {
                                "name": "Most Recent Response",
                                "value": self.get_time_of_most_recent_response()
                            },
                            {
                                "name": "Average Messages per Ticket",
                                "value": self.get_average_messages_per_ticket()
                            }
                        ]

                   }
                   ]
        
        return facts
    
    def get_number_of_total_tickets_per_department(self):
        user = self.request.user
        department = self.get_department()
        return Ticket.objects.filter(department= department).count()
               
        
    def get_department(self):
        user = self.request.user
        department = (
                SpecialistDepartment.objects.filter(specialist=user).first()
            ).department
        return department
    
    def get_number_of_open_tickets(self):
        user = self.request.user
        department = self.get_department()
        return Ticket.objects.filter(department= department, status = Ticket.Status.OPEN).count()
    
    def get_number_of_closed_tickets(self):
        user = self.request.user
        department = self.get_department()
        return Ticket.objects.filter(department= department, status = Ticket.Status.CLOSED).count()
    
    def get_time_of_most_recent_response(self):
        user = self.request.user
        department = self.get_department()
        tickets = Ticket.objects.filter(department = department)
        if Message.objects.count() > 0:
            message = Message.objects.filter(ticket__in = tickets).latest("date_time")
            return message.date_time
        
        return "N/A"
    
    def get_average_messages_per_ticket(self):
        user = self.request.user
        department = self.get_department()
        tickets = Ticket.objects.filter(department = department)

        total_messages = 0

        for ticket in tickets:
            total_messages += Message.objects.filter(ticket = ticket).count()

        if len(tickets) != 0:
            return round(total_messages / len(tickets),2)
        else:
            return 0

