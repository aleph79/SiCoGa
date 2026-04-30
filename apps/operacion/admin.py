"""Operación admin."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import EntradaZilpaterol, Pesaje, Reimplante, Transicion


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


@admin.register(Transicion)
class TransicionAdmin(SimpleHistoryAdmin):
    list_display = ("lote", "fecha", "de_fase", "a_fase", "proporcion", "activo")
    list_filter = ("activo", "de_fase", "a_fase")
    search_fields = ("lote__folio",)


@admin.register(EntradaZilpaterol)
class EntradaZilpaterolAdmin(SimpleHistoryAdmin):
    list_display = ("lote", "fecha_entrada", "activo")
    list_filter = ("activo",)
    search_fields = ("lote__folio",)


@admin.register(Pesaje)
class PesajeAdmin(SimpleHistoryAdmin):
    list_display = ("lote", "fecha", "peso_promedio", "cabezas_pesadas", "activo")
    list_filter = ("activo",)
    search_fields = ("lote__folio",)
