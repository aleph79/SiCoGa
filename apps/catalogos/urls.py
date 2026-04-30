from django.urls import path

from . import views

app_name = "catalogos"

urlpatterns = [
    # TipoCorral
    path("tipos-corral/", views.TipoCorralListView.as_view(), name="tipocorral_list"),
    path(
        "tipos-corral/nuevo/",
        views.TipoCorralCreateView.as_view(),
        name="tipocorral_create",
    ),
    path(
        "tipos-corral/<int:pk>/",
        views.TipoCorralDetailView.as_view(),
        name="tipocorral_detail",
    ),
    path(
        "tipos-corral/<int:pk>/editar/",
        views.TipoCorralUpdateView.as_view(),
        name="tipocorral_update",
    ),
    path(
        "tipos-corral/<int:pk>/eliminar/",
        views.TipoCorralDeleteView.as_view(),
        name="tipocorral_delete",
    ),
]
