from django.urls import path

from . import views

app_name = "operacion"

urlpatterns = [
    path("reimplantes/", views.ReimplantesCalendarioView.as_view(), name="reimplantes"),
    path(
        "reimplantes/registrar/",
        views.RegistrarReimplanteView.as_view(),
        name="registrar_reimplante",
    ),
    path("transiciones/", views.TransicionesCalendarioView.as_view(), name="transiciones"),
    path(
        "transiciones/registrar/",
        views.RegistrarTransicionView.as_view(),
        name="registrar_transicion",
    ),
    path("zilpaterol/", views.ZilpaterolCalendarioView.as_view(), name="zilpaterol"),
    path(
        "zilpaterol/registrar/",
        views.RegistrarEntradaZilpaterolView.as_view(),
        name="registrar_zilpaterol",
    ),
    path("pesajes/", views.PesajesListView.as_view(), name="pesajes"),
    path(
        "pesajes/registrar/",
        views.RegistrarPesajeView.as_view(),
        name="registrar_pesaje",
    ),
]
