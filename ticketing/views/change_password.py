from ticketing.forms.change_password import ChangePasswordForm
from ticketing.models.users import User
from ticketing.utility import get
from ticketing.mixins import RoleRequiredMixin
from django.http import Http404
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import  FormView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


def change_password(user, new_password):
    user.password = make_password(new_password)
    user.save()


class ChangePasswordView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    required_roles = [
        User.Role.DIRECTOR,
        User.Role.SPECIALIST,
        User.Role.STUDENT,
    ]
    PERMISSION_MESSAGE = (
        "You must be a director to change other user's passwords"
    )
    error = ''
    form_class = ChangePasswordForm

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        
        Args:
            self: object
                An instance of the class that defines the method.
        Returns:
            _kwargs: dict
                A dictionary of keyword arguments.
        '''
        _kwargs = super().get_form_kwargs()
        _kwargs.update({'user': self.user})
        return _kwargs

    def get_template_names(self):
        return ['user/change_password.html']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'user': self.user})
        return context

    def setup(self, request, pk):
        '''
        Set up the view with the given user ID and request.
        
        Args:
            self: object
                An instance of the class that defines the method.
            request: HttpRequest
                The HTTP request object.
            pk: int
                The ID of the user to set up the view for.
        Returns:
            Http404
                If no user is found matching the query or if an unauthorised user ID
                is provided.
            PermissionDenied
                If the logged-in user is not the director and is not the user being viewed.
        '''
        try:
            self.user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404('No user found matching the query')
        except ValueError:
            raise Http404('Bad user id provided')
        if not request.user.is_anonymous:
            if (
                request.user.role != User.Role.DIRECTOR
                and self.user.id != request.user.id
            ):
                raise PermissionDenied
        super().setup(request, pk=pk)

    def post(self, request, pk):
        '''
        Handles the HTTP POST request for changing the user's password or cancelling the request.
        
        Args:
            self: object
                An instance of the class that defines the method.
            request: HttpRequest
                The HTTP request object.
            pk: int
                The primary key of the user whose password is being changed.
        '''
        if request.POST.get('change'):
            self.form = ChangePasswordForm(request.POST, user=self.user)
            if not self.form.is_valid():
                return super().post(request, pk=pk)
            password = self.form.cleaned_data['password']
            change_password(self.user, password)
            if request.user.role == User.Role.DIRECTOR:
                return get.redirect_to_director_panel_with_saved_params(
                    request
                )
            else:
                return redirect('login')
        elif request.POST.get('cancel'):
            if request.user.role == User.Role.DIRECTOR:
                return get.redirect_to_director_panel_with_saved_params(
                    request
                )
            else:
                return redirect('login')
        return super().post(request, pk=pk)
