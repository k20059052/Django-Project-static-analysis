from django.contrib.auth.decorators import user_passes_test


def roles_allowed(view_func=None, login_url='/login', allowed_roles=[]):
    """
    Decorator checking if the user accessing a view has one of the allowed roles
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active
        and u.is_authenticated
        and u.role in allowed_roles,
        login_url=login_url,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
