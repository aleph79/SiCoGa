"""Catálogos admin registrations."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Corral,
    Formula,
    Implante,
    Medicamento,
    ProgramaReimplante,
    Proveedor,
    TipoCorral,
    TipoGanado,
    TipoOrigen,
)


@admin.register(TipoCorral)
class TipoCorralAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(TipoGanado)
class TipoGanadoAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(TipoOrigen)
class TipoOrigenAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Proveedor)
class ProveedorAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "contacto", "telefono", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre", "contacto", "rfc")


@admin.register(Corral)
class CorralAdmin(SimpleHistoryAdmin):
    list_display = ("clave", "nombre", "tipo_corral", "capacidad_maxima", "activo")
    list_filter = ("activo", "tipo_corral")
    search_fields = ("clave", "nombre")


@admin.register(Implante)
class ImplanteAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(ProgramaReimplante)
class ProgramaReimplanteAdmin(SimpleHistoryAdmin):
    list_display = (
        "tipo_ganado",
        "tipo_origen",
        "peso_min",
        "peso_max",
        "gdp_esperada",
        "peso_objetivo_salida",
        "activo",
    )
    list_filter = ("tipo_ganado", "tipo_origen", "activo")
    search_fields = ("implante_inicial", "reimplante_1")


@admin.register(Formula)
class FormulaAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "costo_kg", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Medicamento)
class MedicamentoAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "principio_activo", "unidad_dosis", "costo_unitario", "activo")
    list_filter = ("activo", "unidad_dosis")
    search_fields = ("nombre", "principio_activo")
