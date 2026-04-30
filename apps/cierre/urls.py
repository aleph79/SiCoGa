from django.urls import path

from . import views

app_name = "cierre"

urlpatterns = [
    path("muertes/", views.MuertesListView.as_view(), name="muertes"),
    path(
        "muertes/registrar/",
        views.RegistrarMuerteView.as_view(),
        name="registrar_muerte",
    ),
    path("ventas/", views.VentasListView.as_view(), name="ventas"),
    path(
        "ventas/registrar/",
        views.RegistrarVentaView.as_view(),
        name="registrar_venta",
    ),
]
