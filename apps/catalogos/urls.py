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
    # TipoGanado
    path("tipos-ganado/", views.TipoGanadoListView.as_view(), name="tipoganado_list"),
    path(
        "tipos-ganado/nuevo/",
        views.TipoGanadoCreateView.as_view(),
        name="tipoganado_create",
    ),
    path(
        "tipos-ganado/<int:pk>/",
        views.TipoGanadoDetailView.as_view(),
        name="tipoganado_detail",
    ),
    path(
        "tipos-ganado/<int:pk>/editar/",
        views.TipoGanadoUpdateView.as_view(),
        name="tipoganado_update",
    ),
    path(
        "tipos-ganado/<int:pk>/eliminar/",
        views.TipoGanadoDeleteView.as_view(),
        name="tipoganado_delete",
    ),
]
