from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    required_roles = []

    def test_func(self):
        return self.request.user.role in self.required_roles

