"""Catálogos de SiCoGa."""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

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


class Implante(AuditableModel):
    """Catálogo de implantes que se aplican a los lotes (Revalor-G, Component TE-200, etc.)."""

    nombre = models.CharField(max_length=60, unique=True)
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Implante"
        verbose_name_plural = "Implantes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ProgramaReimplante(AuditableModel):
    """Motor de cálculo: una fila por (TipoGanado × TipoOrigen × rango de peso)."""

    tipo_ganado = models.ForeignKey(
        TipoGanado, on_delete=models.PROTECT, verbose_name="Tipo de ganado"
    )
    tipo_origen = models.ForeignKey(
        TipoOrigen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tipo de origen",
        help_text="Vacío = aplica a cualquier origen (caso vacas).",
    )

    peso_min = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso mínimo")
    peso_max = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso máximo")

    gdp_esperada = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="GDP esperada")
    peso_objetivo_salida = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Peso objetivo de salida"
    )

    implante_inicial = models.CharField(max_length=40, blank=True, verbose_name="Implante inicial")
    reimplante_1 = models.CharField(max_length=40, blank=True, verbose_name="1er reimplante")
    reimplante_2 = models.CharField(max_length=40, blank=True, verbose_name="2do reimplante")
    reimplante_3 = models.CharField(max_length=40, blank=True, verbose_name="3er reimplante")
    reimplante_4 = models.CharField(max_length=40, blank=True, verbose_name="4to reimplante")

    dias_recepcion = models.PositiveSmallIntegerField(default=0, verbose_name="Días recepción")
    dias_f1 = models.PositiveSmallIntegerField(default=0, verbose_name="Días F1")
    dias_transicion = models.PositiveSmallIntegerField(default=14, verbose_name="Días transición")
    dias_f3 = models.PositiveSmallIntegerField(default=0, verbose_name="Días F3")
    dias_zilpaterol = models.PositiveSmallIntegerField(default=35, verbose_name="Días Zilpaterol")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Programa de reimplante"
        verbose_name_plural = "Programas de reimplante"
        ordering = ["tipo_ganado__nombre", "tipo_origen__nombre", "peso_min"]
        constraints = [
            models.CheckConstraint(
                check=Q(peso_max__gt=F("peso_min")),
                name="programa_peso_max_gt_min",
            ),
        ]

    def __str__(self):
        origen = self.tipo_origen.nombre if self.tipo_origen else "Cualquiera"
        return f"{self.tipo_ganado.nombre}/{origen} {self.peso_min}-{self.peso_max} kg"

    @property
    def peso_promedio(self):
        return (self.peso_min + self.peso_max) / 2

    @property
    def kg_por_hacer(self):
        return self.peso_objetivo_salida - self.peso_promedio

    @property
    def dias_estancia(self):
        if not self.gdp_esperada:
            return 0
        return int(self.kg_por_hacer / self.gdp_esperada)

    @property
    def total_dias(self):
        return (
            self.dias_recepcion
            + self.dias_f1
            + self.dias_transicion
            + self.dias_f3
            + self.dias_zilpaterol
        )

    @classmethod
    def resolver(cls, tipo_ganado, tipo_origen, peso_inicial):
        """Devuelve la regla aplicable para (tipo_ganado, tipo_origen, peso)."""
        qs = cls.objects.filter(
            activo=True,
            tipo_ganado=tipo_ganado,
            peso_min__lte=peso_inicial,
            peso_max__gte=peso_inicial,
        )
        return (
            qs.filter(tipo_origen=tipo_origen).first()
            or qs.filter(tipo_origen__isnull=True).first()
        )
