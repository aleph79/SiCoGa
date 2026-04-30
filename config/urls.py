from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import include, path
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("catalogos/", include("apps.catalogos.urls", namespace="catalogos")),
    path("", HomeView.as_view(), name="dashboard-home-stub"),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
