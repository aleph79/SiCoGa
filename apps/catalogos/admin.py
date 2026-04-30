"""Catálogos admin registrations."""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import TipoCorral


@admin.register(TipoCorral)
class TipoCorralAdmin(SimpleHistoryAdmin):
    list_display = ("nombre", "activo", "updated_at")
    list_filter = ("activo",)
    search_fields = ("nombre",)
