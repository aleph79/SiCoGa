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
]
