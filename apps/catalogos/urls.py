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
    # TipoOrigen
    path("tipos-origen/", views.TipoOrigenListView.as_view(), name="tipoorigen_list"),
    path(
        "tipos-origen/nuevo/",
        views.TipoOrigenCreateView.as_view(),
        name="tipoorigen_create",
    ),
    path(
        "tipos-origen/<int:pk>/",
        views.TipoOrigenDetailView.as_view(),
        name="tipoorigen_detail",
    ),
    path(
        "tipos-origen/<int:pk>/editar/",
        views.TipoOrigenUpdateView.as_view(),
        name="tipoorigen_update",
    ),
    path(
        "tipos-origen/<int:pk>/eliminar/",
        views.TipoOrigenDeleteView.as_view(),
        name="tipoorigen_delete",
    ),
    # Proveedor
    path("proveedores/", views.ProveedorListView.as_view(), name="proveedor_list"),
    path(
        "proveedores/nuevo/",
        views.ProveedorCreateView.as_view(),
        name="proveedor_create",
    ),
    path(
        "proveedores/<int:pk>/",
        views.ProveedorDetailView.as_view(),
        name="proveedor_detail",
    ),
    path(
        "proveedores/<int:pk>/editar/",
        views.ProveedorUpdateView.as_view(),
        name="proveedor_update",
    ),
    path(
        "proveedores/<int:pk>/eliminar/",
        views.ProveedorDeleteView.as_view(),
        name="proveedor_delete",
    ),
]
