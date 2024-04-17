from django import forms
from ticketing.models.departments import Subsection
 
class SubsectionForm(forms.ModelForm): 
    """A form used to create or update subsections.

    This form is a ModelForm for the Subsection model and contains a single
    field for the subsection name. It also adds a custom widget to the form
    field to provide a Bootstrap-styled text input.

    Attributes:
        Meta: A nested class that defines metadata about the form, such as the
            model it is associated with and the form fields to include.
        
    Methods:
        custom_save: A custom method that creates a new Subsection instance with
            the provided department and subsection name.
    """
    class Meta:
        model = Subsection
        fields = ['name']
        widgets = {
            'subsection':forms.TextInput(attrs={'class':'form-control'})
        }
    def custom_save(self, department, subsection_name): 
        """
        Creates a new `Subsection` object with the given `department` and `subsection_name`.

        Args:
            department (Department): The `Department` object to which the new `Subsection` object belongs.
            subsection_name (str): The name of the new `Subsection`.

        Returns:
            None
        """
        Subsection.objects.create(
            department = department, 
            name = subsection_name
        )
