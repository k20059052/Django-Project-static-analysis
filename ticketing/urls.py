from django.urls import path
from django.contrib.auth import views
from .views import *
from .views.specialist import specialist_statistics
from .views.director import director_statistics
from .forms import LoginForm, FAQForm
from student_query_system import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home.SearchBarView.as_view(), name='home'),
    path(
        'login/',
        auth.CustomLoginView.as_view(
            template_name='login.html',
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path(
        'logout/',
        views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL),
        name='logout',
    ),
    path('signup/', auth.SignupView.as_view(), name='signup'),
    path('faq/', base_faq.BaseFaq.as_view(), name='faq'),
    path(
        'add_faq/',
        specialist_faq_form.FAQFormView.as_view(),
        name='faq_form_view',
    ),
    path(
        'faq/<slug:department>/',
        department_faq.DepartmentFAQ.as_view(),
        name='department_faq',
    ),
    path(
        'specialist_dashboard/<slug:ticket_type>/',
        specialist_inbox.SpecialistInboxView.as_view(),
        name='specialist_dashboard',
    ),
    path(
        'inbox/',
        student_inbox.StudentInboxView.as_view(),
        name='student_inbox',
    ),
    path(
        'specialist_claim_ticket/<int:pk>',
        specialist_claim_ticket.SpecialistClaimTicketView.as_view(),
        name='specialist_claim_ticket',
    ),
    path(
        'specialist_message/<int:pk>',
        specialist_message.SpecialistMessageView.as_view(),
        name='specialist_message',
    ),
    path(
        'create_ticket/',
        student_ticket.StudentTicketView.as_view(),
        name='create_ticket',
    ),
    path(
        'check_faq/',
        individual_specialist_faq.SpecialistFAQListView.as_view(),
        name='check_faq',
    ),
    path(
        'check_department_faq/',
        specialist_department_faq.SpecialistDepartmentFaq.as_view(),
        name='specialist_department_faq',
    ),
    path(
        '<int:pk>/edit/',
        update_faq.FAQUpdateFormView.as_view(),
        name='faq_update',
    ),
    path(
        '<int:pk>/delete/',
        delete_faq.FAQDeleteView.as_view(),
        name='faq_delete',
    ),
    path('signup/', auth.SignupView.as_view(), name='signup'),
    path(
        'student_dashboard/',
        student_inbox.StudentInboxView.as_view(),
        name='student_dashboard',
    ),
    path('ticket/', ticket_view.TicketView.as_view(), name='ticket'),
    path(
        'ticket/<int:pk>/',
        student_message.StudentMessageView.as_view(),
        name='student_message',
    ),
    path(
        'specialist_message/<int:pk>',
        specialist_message.SpecialistMessageView.as_view(),
        name='specialist_message',
    ),
    path(
        'message_list/<int:pk>',
        message_list.MessageListView.as_view(),
        name='message_list',
    ),
    path(
        'director_panel/',
        director_panel.DirectorPanelView.as_view(),
        name='director_panel',
    ),
    path(
        '<pk>/edit_user/', edit_user.EditUserView.as_view(), name='edit_user'
    ),
    path(
        '<pk>/change_password/',
        change_password.ChangePasswordView.as_view(),
        name='change_password',
    ),
    path(
        'department_manager/',
        department_manager.DepartmentManagerView.as_view(),
        name='department_manager',
    ),
    path(
        '<pk>/edit_department/',
        edit_department.EditDepartmentView.as_view(),
        name='edit_department',
    ),
    path( 
        'create_subsection/', 
        specialist_subsection_create.SpecialistSubSectionView.as_view(), 
        name='create_subsection',
    ),
    path(
        'specialist_create_faq_from_ticket/<int:pk>',
        specialist_create_faq_from_ticket.SpecialistCreateFAQFromTicketView.as_view(),
        name='specialist_create_faq_from_ticket',
    ),
    path(
        'specialist_statistics',
        specialist_statistics.SpecialistStatisticsView.as_view(),
        name='specialist_statistics'
    ),
    path('director_statistics',
         director_statistics.DirectorStatisticsView.as_view(),
         name = 'director_statistics'
    ),
    path(
        'archived_ticket/<int:pk>',
        archived_ticket.ArchivedTicketView.as_view(),
        name="archived_ticket",
    ),
    path(
        'subsection_manager/',
        subsection_manager.SubsectionManagerView.as_view(),
        name='subsection_manager',
    ),
    path(
        'edit_subsection/<pk>/',
        edit_subsection.EditSubsectionView.as_view(),
        name='edit_subsection',
    ),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

handler404 = 'ticketing.views.errors.error_404'
