"""Cierre admin."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import Muerte, Venta


@admin.register(Muerte)
class MuerteAdmin(SimpleHistoryAdmin):
    list_display = ("lote", "fecha", "arete", "causa", "peso_estimado", "activo")
    list_filter = ("activo", "causa")
    search_fields = ("lote__folio", "arete")


@admin.register(Venta)
class VentaAdmin(SimpleHistoryAdmin):
    list_display = ("lote", "fecha", "cliente", "cabezas", "kilos", "precio_kg", "activo")
    list_filter = ("activo",)
    search_fields = ("lote__folio", "cliente")
