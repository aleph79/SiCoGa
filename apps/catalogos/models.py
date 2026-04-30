"""Catálogos de SiCoGa."""

from django.db import models

from simple_history.models import HistoricalRecords

from apps.core.models import AuditableModel


class TipoCorral(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de corral"
        verbose_name_plural = "Tipos de corral"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoOrigen(AuditableModel):
    nombre = models.CharField(max_length=20, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de origen"
        verbose_name_plural = "Tipos de origen"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoGanado(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True, verbose_name="Nombre")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de ganado"
        verbose_name_plural = "Tipos de ganado"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(AuditableModel):
    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    rfc = models.CharField(max_length=13, blank=True, verbose_name="RFC")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    contacto = models.CharField(max_length=80, blank=True, verbose_name="Contacto")
    notas = models.TextField(blank=True, verbose_name="Notas")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
