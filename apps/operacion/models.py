"""Operación models — eventos durante la vida del lote."""

from django.db import models

from simple_history.models import HistoricalRecords

from apps.catalogos.models import Implante
from apps.core.models import AuditableModel
from apps.lotes.models import Lote


class Reimplante(AuditableModel):
    """Aplicación de un implante (inicial, 1ero, 2do, 3ero, 4to) a un lote."""

    NUMERO_CHOICES = [
        (0, "Implante inicial"),
        (1, "1er reimplante"),
        (2, "2do reimplante"),
        (3, "3er reimplante"),
        (4, "4to reimplante"),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="reimplantes")
    fecha_aplicada = models.DateField(verbose_name="Fecha aplicada")
    numero = models.PositiveSmallIntegerField(
        choices=NUMERO_CHOICES,
        default=0,
        help_text="0 = implante inicial; 1-4 = reimplantes consecutivos.",
    )
    implante = models.ForeignKey(Implante, on_delete=models.PROTECT)
    peso_aplicado = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso al aplicar (kg)",
        help_text="Peso promedio del lote al momento del reimplante. Opcional.",
    )
    cabezas_aplicadas = models.PositiveIntegerField(
        verbose_name="Cabezas aplicadas",
        help_text="Cuántas cabezas recibieron el implante.",
    )
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Reimplante"
        verbose_name_plural = "Reimplantes"
        ordering = ["-fecha_aplicada", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "numero"],
                condition=models.Q(activo=True),
                name="reimplante_unico_por_lote_y_numero",
            ),
        ]

    def __str__(self):
        return f"{self.lote.folio} · {self.get_numero_display()} · {self.fecha_aplicada}"

    def save(self, *args, **kwargs):
        # MySQL no soporta partial unique constraints; enforzamos en app.
        if self.activo and self.lote_id is not None and self.numero is not None:
            from django.db import IntegrityError

            qs = Reimplante.objects.filter(lote_id=self.lote_id, numero=self.numero, activo=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise IntegrityError(
                    f"Ya existe un reimplante activo {self.get_numero_display()} "
                    f"para el lote {self.lote.folio}."
                )
        super().save(*args, **kwargs)
