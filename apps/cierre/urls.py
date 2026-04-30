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
    path(
        "lotes/<int:pk>/compra/",
        views.CompraLoteView.as_view(),
        name="compra_lote",
    ),
    path("alimentaciones/", views.AlimentacionListView.as_view(), name="alimentaciones"),
    path(
        "alimentaciones/registrar/",
        views.RegistrarAlimentacionView.as_view(),
        name="registrar_alimentacion",
    ),
    path("medicaciones/", views.MedicacionListView.as_view(), name="medicaciones"),
    path(
        "medicaciones/registrar/",
        views.RegistrarMedicacionView.as_view(),
        name="registrar_medicacion",
    ),
    path(
        "costo-hotel/",
        views.CostoHotelConfigView.as_view(),
        name="costo_hotel_config",
    ),
    path(
        "costo-hotel/nuevo/",
        views.RegistrarCostoHotelComponenteView.as_view(),
        name="registrar_costo_hotel",
    ),
    path(
        "costo-hotel/<int:pk>/editar/",
        views.EditarCostoHotelComponenteView.as_view(),
        name="editar_costo_hotel",
    ),
    path(
        "lotes/<int:pk>/costo-hotel/",
        views.CostoHotelLoteView.as_view(),
        name="costo_hotel_lote",
    ),
]
