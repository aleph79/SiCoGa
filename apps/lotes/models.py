"""Lotes models."""

from django.core.validators import MinValueValidator
from django.db import models

from simple_history.models import HistoricalRecords

from apps.catalogos.models import Corral, Proveedor, TipoGanado, TipoOrigen
from apps.core.models import AuditableModel, TimeStampedModel


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

    # ----- Resolución del programa aplicable -----

    @property
    def programa(self):
        from apps.catalogos.models import ProgramaReimplante

        return ProgramaReimplante.resolver(
            self.tipo_ganado, self.tipo_origen, self.peso_inicial_promedio
        )

    @property
    def gdp_efectiva(self):
        if self.gdp_esperada is not None:
            return self.gdp_esperada
        return self.programa.gdp_esperada if self.programa else None

    @property
    def peso_objetivo_efectivo(self):
        if self.peso_salida_objetivo is not None:
            return self.peso_salida_objetivo
        return self.programa.peso_objetivo_salida if self.programa else None

    @property
    def kg_por_hacer(self):
        if self.peso_objetivo_efectivo is None:
            return None
        return self.peso_objetivo_efectivo - self.peso_inicial_promedio

    @property
    def dias_engorda_proyectados(self):
        gdp = self.gdp_efectiva
        kg = self.kg_por_hacer
        if not gdp or kg is None or gdp <= 0:
            return None
        return int(kg / gdp)

    @property
    def fecha_proyectada_venta(self):
        from datetime import timedelta

        dias = self.dias_engorda_proyectados
        if dias is None:
            return None
        return self.fecha_inicio + timedelta(days=dias)

    @property
    def semana_proyectada_venta(self):
        f = self.fecha_proyectada_venta
        return f.isocalendar()[1] if f else None

    @property
    def kilos_proyectados_venta(self):
        peso = self.peso_objetivo_efectivo
        if peso is None:
            return None
        return peso * self.cabezas_iniciales

    # ----- Fechas de reimplantes (60 días desde inicio + 60 entre cada uno) -----

    def fecha_reimplante(self, n: int):
        from datetime import timedelta

        if n < 1:
            return None
        return self.fecha_inicio + timedelta(days=60 * n)

    @property
    def fecha_reimplante_1(self):
        return self.fecha_reimplante(1)

    @property
    def fecha_reimplante_2(self):
        return self.fecha_reimplante(2)

    @property
    def fecha_reimplante_3(self):
        return self.fecha_reimplante(3)

    @property
    def fecha_entrada_zilpaterol(self):
        from datetime import timedelta

        if not self.programa or not self.fecha_proyectada_venta:
            return None
        return self.fecha_proyectada_venta - timedelta(days=self.programa.dias_zilpaterol)

    # ----- Properties para la pantalla de Disponibilidad (Spec C) -----

    @property
    def dias_transcurridos(self):
        from datetime import date

        return (date.today() - self.fecha_inicio).days

    @property
    def peso_actual_proyectado(self):
        """peso base + (días desde la base) × gdp_efectiva.

        La base es el último pesaje real si existe; si no, el peso inicial.
        Esto hace que la proyección se "corrija sola" cuando se captura un
        pesaje real intermedio.
        """
        from datetime import date

        if not self.gdp_efectiva:
            return None

        base_peso = self.peso_inicial_promedio
        base_fecha = self.fecha_inicio

        # Si hay app `operacion` instalada y existen pesajes, usar el último
        try:
            ultimo = self.pesajes.filter(activo=True).order_by("-fecha").first()
        except Exception:
            ultimo = None

        if ultimo:
            base_peso = ultimo.peso_promedio
            base_fecha = ultimo.fecha

        dias = (date.today() - base_fecha).days
        return base_peso + (dias * self.gdp_efectiva)

    @property
    def peso_estimado_rango(self):
        """Peso al cumplir 60 días — referencia para el primer reimplante."""
        if not self.gdp_efectiva:
            return None
        return self.peso_inicial_promedio + (60 * self.gdp_efectiva)

    # ----- Properties para Cierre (Spec E.1) -----

    @property
    def cabezas_muertas(self):
        try:
            return self.muertes.filter(activo=True).count()
        except Exception:
            return 0

    @property
    def cabezas_vendidas(self):
        from django.db.models import Sum

        try:
            return (
                self.ventas.filter(activo=True).aggregate(s=Sum("cabezas"))["s"] or 0
            )
        except Exception:
            return 0

    @property
    def cabezas_actuales(self):
        return self.cabezas_iniciales - self.cabezas_muertas - self.cabezas_vendidas

    @property
    def mortalidad_pct(self):
        from decimal import Decimal

        if not self.cabezas_iniciales:
            return Decimal("0")
        return (
            Decimal(self.cabezas_muertas) / Decimal(self.cabezas_iniciales) * Decimal("100")
        )

    @property
    def ingreso_total_ventas(self):
        from decimal import Decimal

        try:
            return sum(
                (v.ingreso_total for v in self.ventas.filter(activo=True)),
                start=Decimal("0"),
            )
        except Exception:
            return Decimal("0")

    @property
    def etapa(self):
        """Recepción → F1 → Transición → F3 → Zilpaterol → Post-Zilpaterol."""
        p = self.programa
        if not p:
            return "Sin programa"
        d = self.dias_transcurridos
        acum = p.dias_recepcion
        if d < acum:
            return "Recepción"
        acum += p.dias_f1
        if d < acum:
            return "F1"
        acum += p.dias_transicion
        if d < acum:
            return "Transición"
        acum += p.dias_f3
        if d < acum:
            return "F3"
        acum += p.dias_zilpaterol
        if d < acum:
            return "Zilpaterol"
        return "Post-Zilpaterol"


class LoteFusion(TimeStampedModel):
    """Una fila por cada vez que un lote 'origen' se fusiona en un lote 'destino'."""

    lote_destino = models.ForeignKey(
        Lote, on_delete=models.PROTECT, related_name="fusiones_recibidas"
    )
    lote_origen = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="fusiones_dadas")
    cabezas_movidas = models.PositiveIntegerField()
    fecha_fusion = models.DateField()
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Fusión de lote"
        verbose_name_plural = "Fusiones de lote"
        ordering = ["-fecha_fusion", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(lote_destino=models.F("lote_origen")),
                name="fusion_destino_distinto_de_origen",
            ),
        ]

    def __str__(self):
        return f"{self.lote_origen.folio} → {self.lote_destino.folio} ({self.cabezas_movidas} cab.)"
