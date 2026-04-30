from django.urls import path

from . import views

app_name = "lotes"

urlpatterns = [
    path("", views.LoteListView.as_view(), name="lote_list"),
    path("nuevo/", views.LoteCreateView.as_view(), name="lote_create"),
    path(
        "preview-proyeccion/",
        views.PreviewProyeccionView.as_view(),
        name="lote_preview",
    ),
    path("<int:pk>/", views.LoteDetailView.as_view(), name="lote_detail"),
    path("<int:pk>/editar/", views.LoteUpdateView.as_view(), name="lote_update"),
    path("<int:pk>/eliminar/", views.LoteDeleteView.as_view(), name="lote_delete"),
]
