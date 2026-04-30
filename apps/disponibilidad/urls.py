from django.urls import path

from . import views

app_name = "disponibilidad"

urlpatterns = [
    path("", views.DisponibilidadView.as_view(), name="home"),
    path("export.csv", views.ExportCsvView.as_view(), name="export_csv"),
]
