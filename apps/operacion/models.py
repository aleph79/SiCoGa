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


class Transicion(AuditableModel):
    """Cambio de fórmula alimenticia en un lote (F1 → FT → F3 → F3+Zilp)."""

    FASES = [
        ("F1", "F1"),
        ("FT", "F1+F3 transición"),
        ("F3", "F3"),
        ("F3Z", "F3+Zilpaterol"),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="transiciones")
    fecha = models.DateField()
    de_fase = models.CharField(max_length=4, choices=FASES, verbose_name="De fase")
    a_fase = models.CharField(max_length=4, choices=FASES, verbose_name="A fase")
    proporcion = models.CharField(
        max_length=30, blank=True, help_text="Ej: 50/50, 100% F3."
    )
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Transición"
        verbose_name_plural = "Transiciones"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.lote.folio} · {self.de_fase}→{self.a_fase} · {self.fecha}"


class EntradaZilpaterol(AuditableModel):
    """Registro de cuándo un lote entra formalmente a la fase de Zilpaterol.

    Disparara el reloj de 35 días previos a venta (legalmente obligatorio).
    """

    lote = models.OneToOneField(
        Lote, on_delete=models.PROTECT, related_name="entrada_zilpaterol"
    )
    fecha_entrada = models.DateField()
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Entrada a Zilpaterol"
        verbose_name_plural = "Entradas a Zilpaterol"
        ordering = ["-fecha_entrada"]

    def __str__(self):
        return f"{self.lote.folio} · entró {self.fecha_entrada}"

    @property
    def fecha_salida_proyectada(self):
        """fecha_entrada + 35 días."""
        from datetime import timedelta

        return self.fecha_entrada + timedelta(days=35)

    @property
    def dias_en_zilpaterol(self):
        from datetime import date

        return (date.today() - self.fecha_entrada).days

    @property
    def dias_restantes(self):
        return max(0, 35 - self.dias_en_zilpaterol)

    @property
    def listo_para_venta(self):
        return self.dias_en_zilpaterol >= 35


class Pesaje(AuditableModel):
    """Pesaje real del lote — corrige la proyección a partir de esta fecha."""

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="pesajes")
    fecha = models.DateField()
    peso_promedio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Peso promedio (kg)",
    )
    cabezas_pesadas = models.PositiveIntegerField(
        verbose_name="Cabezas pesadas",
        help_text="Si fue muestreo, este número puede ser menor que el inventario.",
    )
    notas = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pesaje"
        verbose_name_plural = "Pesajes"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.lote.folio} · {self.fecha} · {self.peso_promedio} kg"
