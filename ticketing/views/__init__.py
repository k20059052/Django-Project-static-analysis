# base views
from . import auth
from . import home
from . import ticket_view
from . import message_list
from . import change_password
# director views
from . director import edit_user
from . director import director_panel
from . director import edit_department
from . director import department_manager
# faq views
from . faq import base_faq
from . faq import update_faq
from . faq import delete_faq
from . faq import department_faq
from . faq import specialist_faq_form
from . faq import individual_specialist_faq
from . faq import specialist_department_faq
# student views
from . student import student_inbox
from . student import student_ticket
from . student import student_message
# specialist views
from . specialist import specialist_inbox
from . specialist import specialist_message
from . specialist import specialist_claim_ticket               
from . specialist import specialist_subsection_create
from . specialist import subsection_manager
from . specialist import specialist_create_faq_from_ticket

from .student import student_ticket
from .faq import department_faq
from .faq import base_faq
from .faq import specialist_faq_form
from .faq import individual_specialist_faq
from .faq import update_faq
from .faq import delete_faq
from .faq import specialist_department_faq
from . import archived_ticket
from . specialist import edit_subsection