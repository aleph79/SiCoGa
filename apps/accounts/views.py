from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm
from .models import Profile


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/perfil.html"
    success_url = reverse_lazy("accounts:perfil")

    def get_object(self, queryset=None):
        return self.request.user.profile
