"""Operación admin."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import Reimplante


@admin.register(Reimplante)
class ReimplanteAdmin(SimpleHistoryAdmin):
    list_display = (
        "lote",
        "numero",
        "fecha_aplicada",
        "implante",
        "cabezas_aplicadas",
        "activo",
    )
    list_filter = ("activo", "numero", "implante")
    search_fields = ("lote__folio",)
    autocomplete_fields = ("lote", "implante")
