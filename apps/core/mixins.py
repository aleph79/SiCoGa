"""View mixins shared across catalog apps."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class CatalogoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Login + permission required.

    - Anonymous users are redirected to login (302).
    - Authenticated users without the required permission get 403.
    """

    raise_exception = True
    paginate_by = 25

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Authenticated but lacks permission → 403
            return super().handle_no_permission()
        # Not logged in → redirect to login
        self.raise_exception = False
        return super().handle_no_permission()
