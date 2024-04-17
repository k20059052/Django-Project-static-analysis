from ticketing.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'email',
                'placeholder': 'Email',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password',
                'placeholder': 'Password',
            }
        )
    )


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        labels = {'email': 'Email'}
