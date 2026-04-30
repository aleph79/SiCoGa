"""Lotes admin."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import Lote


@admin.register(Lote)
class LoteAdmin(SimpleHistoryAdmin):
    list_display = (
        "folio",
        "corral",
        "tipo_ganado",
        "tipo_origen",
        "cabezas_iniciales",
        "fecha_inicio",
        "peso_inicial_promedio",
        "activo",
    )
    list_filter = ("activo", "tipo_ganado", "tipo_origen", "corral")
    search_fields = ("folio",)
