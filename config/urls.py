from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import include, path
from django.views.generic import RedirectView


class HomeView(LoginRequiredMixin, RedirectView):
    """`/` redirige a la pantalla operativa principal (Disponibilidad, Spec C)."""

    url = "/disponibilidad/"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("catalogos/", include("apps.catalogos.urls", namespace="catalogos")),
    path("lotes/", include("apps.lotes.urls", namespace="lotes")),
    path("disponibilidad/", include("apps.disponibilidad.urls", namespace="disponibilidad")),
    path("operacion/", include("apps.operacion.urls", namespace="operacion")),
    path("cierre/", include("apps.cierre.urls", namespace="cierre")),
    path("", HomeView.as_view(), name="dashboard-home-stub"),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
