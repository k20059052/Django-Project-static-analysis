from ticketing.utility.user import get_user
from django.shortcuts import  redirect


def get_user_from_id_param(end):
    def decorator(function):
        INVALID_ID_MESSAGE = "The given ID is invalid"
        UNASSIGNED_ID_MESSAGE = "There is no user with the given ID"
        def inner(ptr, request):
            error_str = ""
            if not request.GET.get("id"):
                error_str = INVALID_ID_MESSAGE
                return end(ptr, request, error_str)
            try:
                id = int(request.GET.get("id"))
            except ValueError:
                error_str = INVALID_ID_MESSAGE
                return end(ptr, request, error_str)
            if id < 0:
                error_str = INVALID_ID_MESSAGE
                return end(ptr, request, error_str)
            user = get_user(id)
            if not user:
                error_str = UNASSIGNED_ID_MESSAGE
                return end(ptr, request, error_str)
            return function(ptr, request, user)
        return inner
    return decorator


def redirect_to_director_panel_with_saved_params(request):
    response = redirect("director_panel")
    get_query = request.session.get("director_panel_query")
    if get_query:
        response['Location'] += "?" + get_query
    return response