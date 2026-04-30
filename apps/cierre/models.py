"""Cierre models — eventos que ajustan cabezas y costean el lote."""

from decimal import Decimal

from django.db import models

from simple_history.models import HistoricalRecords

from apps.core.models import AuditableModel
from apps.lotes.models import Lote


class Muerte(AuditableModel):
    """Mortalidad durante engorda."""

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="muertes")
    fecha = models.DateField()
    arete = models.CharField(max_length=20, blank=True, verbose_name="Arete")
    causa = models.CharField(
        max_length=80,
        blank=True,
        help_text="Ej: Neumonía, timpanismo, accidente.",
    )
    peso_estimado = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Muerte"
        verbose_name_plural = "Muertes"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.lote.folio} · {self.fecha} · {self.causa or 'sin causa'}"


class Venta(AuditableModel):
    """Salida (venta) total o parcial del lote."""

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="ventas")
    fecha = models.DateField()
    cliente = models.CharField(max_length=120, blank=True)
    cabezas = models.PositiveIntegerField()
    kilos = models.DecimalField(max_digits=10, decimal_places=2)
    precio_kg = models.DecimalField(max_digits=8, decimal_places=2)
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.lote.folio} · {self.fecha} · {self.cabezas} cab"

    @property
    def ingreso_total(self):
        return self.kilos * self.precio_kg

    @property
    def peso_promedio(self):
        if not self.cabezas:
            return Decimal("0")
        return self.kilos / self.cabezas

    @property
    def precio_cabeza(self):
        if not self.cabezas:
            return Decimal("0")
        return self.ingreso_total / self.cabezas
