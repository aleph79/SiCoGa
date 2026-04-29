"""View mixins shared across catalog apps."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class CatalogoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Login + permission required. Returns 403 (raise_exception) instead of redirect."""

    raise_exception = True
    paginate_by = 25
