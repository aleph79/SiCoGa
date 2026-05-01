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

    # ----- Compra / Recepción (Spec E.2) -----
    fecha_compra = models.DateField(
        null=True, blank=True, verbose_name="Fecha de compra"
    )
    cabezas_origen = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Cabezas en origen",
        help_text="Cabezas embarcadas en el rancho/proveedor.",
    )
    kilos_origen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Kilos en origen",
    )
    kilos_recibo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Kilos en recibo",
        help_text="Kilos al desembarque en corral.",
    )
    costo_compra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo total de compra ($)",
    )

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

    # ----- Properties para Compra / Recepción (Spec E.2) -----

    @property
    def peso_promedio_origen(self):
        from decimal import Decimal

        if not self.cabezas_origen or not self.kilos_origen:
            return None
        return self.kilos_origen / Decimal(self.cabezas_origen)

    @property
    def peso_promedio_recibo(self):
        from decimal import Decimal

        if not self.cabezas_iniciales or not self.kilos_recibo:
            return None
        return self.kilos_recibo / Decimal(self.cabezas_iniciales)

    @property
    def merma_transito_cabezas(self):
        if self.cabezas_origen is None:
            return None
        return self.cabezas_origen - self.cabezas_iniciales

    @property
    def merma_transito_pct(self):
        from decimal import Decimal

        if not self.cabezas_origen:
            return None
        return Decimal(self.merma_transito_cabezas) / Decimal(self.cabezas_origen) * Decimal("100")

    @property
    def merma_transito_kilos(self):
        if self.kilos_origen is None or self.kilos_recibo is None:
            return None
        return self.kilos_origen - self.kilos_recibo

    @property
    def costo_por_cabeza(self):
        from decimal import Decimal

        if not self.costo_compra or not self.cabezas_iniciales:
            return None
        return self.costo_compra / Decimal(self.cabezas_iniciales)

    @property
    def costo_por_kilo(self):
        if not self.costo_compra or not self.kilos_recibo:
            return None
        return self.costo_compra / self.kilos_recibo

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

    # ----- Costo Hotel (Spec E.4) -----

    @property
    def fecha_cierre(self):
        """Fecha de cierre del lote (última venta) o hoy si sigue activo."""
        from datetime import date

        try:
            ultima = self.ventas.filter(activo=True).order_by("-fecha").first()
        except Exception:
            ultima = None
        return ultima.fecha if ultima else date.today()

    @property
    def dias_calendario(self):
        return (self.fecha_cierre - self.fecha_inicio).days + 1

    @property
    def dias_animal_base(self):
        """días_calendario × cabezas iniciales."""
        return self.dias_calendario * self.cabezas_iniciales

    @property
    def dias_animal_descuento_muertes(self):
        """Cada muerte resta los días que faltaban del animal hasta el cierre."""
        try:
            qs = self.muertes.filter(activo=True)
        except Exception:
            return 0
        descuento = 0
        for m in qs:
            dias_restantes = (self.fecha_cierre - m.fecha).days
            if dias_restantes > 0:
                descuento += dias_restantes
        return descuento

    @property
    def dias_animal_netos(self):
        return self.dias_animal_base - self.dias_animal_descuento_muertes

    @property
    def costo_hotel_dia_animal(self):
        """Suma de costo/d-a de los componentes habilitados."""
        from decimal import Decimal

        from apps.cierre.models import CostoHotelComponente

        total = CostoHotelComponente.objects.filter(
            activo=True, habilitado=True
        ).aggregate(s=models.Sum("costo_dia_animal"))["s"]
        return total or Decimal("0")

    @property
    def costo_hotel_total(self):
        from decimal import Decimal

        return Decimal(self.dias_animal_netos) * self.costo_hotel_dia_animal

    # ----- Cierre consolidado (Spec E.5) -----

    @property
    def costo_alimentacion_total(self):
        from decimal import Decimal

        try:
            return sum(
                ((a.costo_total or Decimal("0")) for a in self.alimentaciones.filter(activo=True)),
                start=Decimal("0"),
            )
        except Exception:
            return Decimal("0")

    @property
    def kg_alimento_total(self):
        from decimal import Decimal

        try:
            return sum(
                (a.kg_consumidos for a in self.alimentaciones.filter(activo=True)),
                start=Decimal("0"),
            )
        except Exception:
            return Decimal("0")

    @property
    def costo_medicacion_total(self):
        from decimal import Decimal

        try:
            return sum(
                ((m.costo_total or Decimal("0")) for m in self.medicaciones.filter(activo=True)),
                start=Decimal("0"),
            )
        except Exception:
            return Decimal("0")

    @property
    def costo_total(self):
        """Compra + alimentación + medicación + costo hotel."""
        from decimal import Decimal

        compra = self.costo_compra or Decimal("0")
        return (
            compra
            + self.costo_alimentacion_total
            + self.costo_medicacion_total
            + self.costo_hotel_total
        )

    @property
    def kilos_vendidos(self):
        from decimal import Decimal

        try:
            return sum(
                (v.kilos for v in self.ventas.filter(activo=True)),
                start=Decimal("0"),
            )
        except Exception:
            return Decimal("0")

    @property
    def kg_ganados(self):
        """Kilos en venta − kilos al recibo (proxy del peso ganado real)."""
        from decimal import Decimal

        kilos_vta = self.kilos_vendidos
        if not kilos_vta:
            return Decimal("0")
        kilos_inicio = self.kilos_recibo or (
            self.peso_inicial_promedio * self.cabezas_iniciales
        )
        return kilos_vta - kilos_inicio

    @property
    def gdp_real(self):
        """Ganancia diaria real promedio = kg_ganados / días."""
        from decimal import Decimal

        if not self.dias_calendario:
            return Decimal("0")
        kg = self.kg_ganados
        if kg == 0:
            return Decimal("0")
        return kg / Decimal(self.dias_calendario) / Decimal(self.cabezas_iniciales)

    @property
    def conversion_alimenticia(self):
        """kg de alimento por kg ganado."""
        from decimal import Decimal

        kg = self.kg_ganados
        if not kg or kg == 0:
            return Decimal("0")
        alim = self.kg_alimento_total
        if not alim:
            return Decimal("0")
        return alim / kg

    @property
    def margen_bruto(self):
        return self.ingreso_total_ventas - self.costo_total

    @property
    def margen_pct(self):
        from decimal import Decimal

        ing = self.ingreso_total_ventas
        if not ing or ing == 0:
            return Decimal("0")
        return self.margen_bruto / ing * Decimal("100")

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
