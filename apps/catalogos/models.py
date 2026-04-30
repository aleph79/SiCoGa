"""Catálogos de SiCoGa."""

from django.core.validators import MinValueValidator
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


class Corral(AuditableModel):
    clave = models.CharField(max_length=15, unique=True, verbose_name="Clave")
    nombre = models.CharField(max_length=80, verbose_name="Nombre")
    tipo_corral = models.ForeignKey(
        TipoCorral,
        on_delete=models.PROTECT,
        related_name="corrales",
        verbose_name="Tipo de corral",
    )
    capacidad_maxima = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Capacidad máxima"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Corral"
        verbose_name_plural = "Corrales"
        ordering = ["clave"]

    def __str__(self):
        return f"{self.clave} — {self.nombre}"

    @property
    def ocupacion_actual(self) -> int:
        # Spec A: placeholder. Spec B sustituye por suma de inventarios de lotes activos.
        return 0

    @property
    def disponibilidad(self) -> int:
        return self.capacidad_maxima - self.ocupacion_actual
