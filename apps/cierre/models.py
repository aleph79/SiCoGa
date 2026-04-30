"""Cierre models — eventos que ajustan cabezas y costean el lote."""

from decimal import Decimal

from django.db import models

from simple_history.models import HistoricalRecords

from apps.catalogos.models import Formula, Medicamento
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


class Alimentacion(AuditableModel):
    """Consumo de alimento por fórmula y periodo en un lote."""

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="alimentaciones")
    formula = models.ForeignKey(Formula, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    kg_consumidos = models.DecimalField(max_digits=10, decimal_places=2)
    costo_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override del costo por kg. Si vacío, usa formula.costo_kg.",
    )
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Alimentación"
        verbose_name_plural = "Alimentaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.lote.folio} · {self.formula.nombre} · {self.fecha_inicio}"

    @property
    def dias(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1

    @property
    def costo_kg_efectivo(self):
        if self.costo_kg is not None:
            return self.costo_kg
        return self.formula.costo_kg

    @property
    def costo_total(self):
        kg_costo = self.costo_kg_efectivo
        if kg_costo is None:
            return None
        return self.kg_consumidos * kg_costo


class Medicacion(AuditableModel):
    """Aplicación de medicamento a un lote (recepción/metafilaxia o hospital)."""

    TIPOS = [
        ("recepcion", "Recepción / Metafilaxia"),
        ("hospital", "Hospital"),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="medicaciones")
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=12, choices=TIPOS, default="recepcion")
    fecha = models.DateField()
    cabezas = models.PositiveIntegerField(verbose_name="Cabezas tratadas")
    dosis_descripcion = models.CharField(
        max_length=60,
        blank=True,
        help_text="Ej: 2.5 ml/cab, 1 ml/10 kg.",
    )
    costo_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override del costo unitario. Si vacío, usa medicamento.costo_unitario.",
    )
    arete = models.CharField(max_length=20, blank=True, verbose_name="Arete (hospital)")
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Medicación"
        verbose_name_plural = "Medicaciones"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.lote.folio} · {self.medicamento.nombre} · {self.fecha}"

    @property
    def costo_unitario_efectivo(self):
        if self.costo_unitario is not None:
            return self.costo_unitario
        return self.medicamento.costo_unitario

    @property
    def costo_total(self):
        from decimal import Decimal

        cu = self.costo_unitario_efectivo
        if cu is None:
            return None
        return cu * Decimal(self.cabezas)


class CostoHotelComponente(AuditableModel):
    """Componente del costo hotel (agua, mano de obra, depreciación, admin, etc.).

    El costo hotel se calcula por día-animal. Cada componente puede estar
    habilitado/deshabilitado para evitar duplicar costos que ya están en otra
    cuenta (alimentación, medicación). El total/d-a es la suma de los habilitados.
    """

    nombre = models.CharField(max_length=80, unique=True)
    costo_dia_animal = models.DecimalField(max_digits=8, decimal_places=2)
    habilitado = models.BooleanField(
        default=True,
        help_text="Desmarcar si este componente ya se contabiliza en otra cuenta.",
    )
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Componente costo hotel"
        verbose_name_plural = "Componentes costo hotel"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (${self.costo_dia_animal}/d-a)"
