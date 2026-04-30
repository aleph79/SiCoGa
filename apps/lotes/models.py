"""Lotes models."""

from django.core.validators import MinValueValidator
from django.db import models

from simple_history.models import HistoricalRecords

from apps.catalogos.models import Corral, Proveedor, TipoGanado, TipoOrigen
from apps.core.models import AuditableModel


class Lote(AuditableModel):
    folio = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Folio",
        help_text="Editable manualmente. Único en el sistema.",
    )
    corral = models.ForeignKey(Corral, on_delete=models.PROTECT, related_name="lotes")
    tipo_ganado = models.ForeignKey(
        TipoGanado, on_delete=models.PROTECT, verbose_name="Tipo de ganado"
    )
    tipo_origen = models.ForeignKey(
        TipoOrigen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tipo de origen",
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)

    cabezas_iniciales = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Cabezas iniciales"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    peso_inicial_promedio = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Peso inicial promedio (kg)"
    )
    peso_salida_objetivo = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso de salida objetivo (kg)",
        help_text="Si vacío, se toma del programa aplicable.",
    )
    gdp_esperada = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="GDP esperada (kg/día)",
        help_text="Si vacío, se toma del programa aplicable.",
    )
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ["-fecha_inicio", "folio"]
        constraints = [
            models.UniqueConstraint(
                fields=["corral"],
                condition=models.Q(activo=True),
                name="lote_unico_activo_por_corral",
            ),
        ]

    def __str__(self):
        return f"{self.folio} ({self.tipo_ganado.nombre} · {self.corral.clave})"

    def save(self, *args, **kwargs):
        # MySQL no soporta partial unique constraints; enforzamos en app.
        if self.activo and self.corral_id:
            from django.db import IntegrityError

            qs = Lote.objects.filter(corral=self.corral, activo=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise IntegrityError(
                    f"Ya existe un lote activo en el corral '{self.corral.clave}'."
                )
        super().save(*args, **kwargs)
