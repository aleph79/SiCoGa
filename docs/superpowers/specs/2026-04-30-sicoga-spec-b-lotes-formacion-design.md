# SiCoGa — Spec B: Lotes y Formación (Diseño)

**Fecha:** 2026-04-30
**Estado:** 🚧 **DRAFT v2 — incluye operación de Fusión por feedback Chamizal · pendiente de OK final del cliente**
**Cliente:** Chamizal Camperos
**Proveedor:** SIWEB (Soluciones Informáticas Web S.A. de C.V.)
**Repositorio:** https://github.com/aleph79/SiCoGa
**Spec previo:** [A — Cimientos](./2026-04-29-sicoga-spec-a-cimientos-design.md) ✅ entregado 2026-04-30

## Contexto

Spec A dejó la base: auth, roles, catálogos (TipoCorral, TipoGanado, TipoOrigen, Corral, Proveedor) y el motor `ProgramaReimplante` con 49 filas precargadas desde el Excel del cliente.

Spec B introduce la entidad operativa central del sistema: **`Lote`**. Un lote es un grupo de cabezas que entra a un corral en una fecha dada, comparte sexo y peso de entrada, y sigue una trayectoria de engorda hasta su venta. Toda la operación posterior (reimplantes, transiciones, zilpaterol, salidas, cierre) cuelga del lote.

## Objetivo del Spec B

Al cerrar este spec, el sistema permite:

1. Crear (formar) un nuevo lote en un corral con captura mínima.
2. El sistema calcula automáticamente la proyección completa (días de engorda, fecha de venta, fechas de reimplantes, entrada a Zilpaterol, kilos estimados) usando el `ProgramaReimplante` resuelto por (TipoGanado × TipoOrigen × peso entrada).
3. Listar lotes activos, ver el detalle, editar datos correctivos, marcar inactivo.
4. Auditoría completa con `simple_history`.
5. Capturista ya tiene permisos `add/change` operativos sobre `Lote`.

Lo que **NO** entra en este spec (queda para B+):
- Dispersión (dividir un lote en sublotes) — Spec C.
- Movimientos generales entre corrales sin fusionar (transferir un lote de C03 a C07 manteniendo folio) — Spec C.
- Pantalla principal de Disponibilidad con KPIs (Spec C).
- Reimplantes, transiciones, Zilpaterol, salidas (Spec D).
- Cierre del lote (Spec E).
- Muertes, alimentación, medicación, ventas parciales (Spec E o submodelo de D).

---

## Decisiones tomadas

| # | Decisión | Valor | Origen |
|---|---|---|---|
| 1 | Folio del lote | 100% editable manual por el operador. No hay autogeneración ni validación de formato. Único en el sistema. | Spec A decisión 11 |
| 2 | Tipo de ganado del lote | FK a `TipoGanado` ya existente (Macho / Hembra / Vaca). Sin enum nuevo. | Reusa Spec A |
| 3 | Tipo de origen | FK a `TipoOrigen` ya existente (Corral / Potrero / vacío). | Reusa Spec A |
| 4 | Programa aplicable | Resuelto por `ProgramaReimplante.resolver(tipo_ganado, tipo_origen, peso_inicial)`. Si no encuentra match, el alta se permite **con advertencia** y los campos derivados quedan vacíos hasta que se cree la regla. | Pragmatismo |
| 5 | 1 lote ↔ 1 corral | Un lote vive en un corral. La capacidad del corral (`capacidad_maxima`) limita el inventario inicial. | Dummy v4 |
| 6 | Borrado | Lógico (`activo=False`). Spec E manejará el "cierre" formal con campos de salida. | Consistencia con Spec A |
| 7 | Auditoría | `simple_history` desde el día 1, igual que Spec A. | Spec A decisión 10 |
| 8 | Cálculos derivados | Properties de Python sobre el modelo, NO campos persistentes. Si cambia el `ProgramaReimplante`, los lotes existentes ven la nueva proyección sin migración de datos. | Limpieza |
| 9 | Permisos Capturista | `view/add/change/add_fusion_lote` en este spec. Sin `delete` (sólo Admin/Gerente pueden borrar lógicamente). | Operación real |
| 10 | **Fusión de lotes** | Operación atómica: lote A (origen) absorbe sus cabezas en lote B (destino); A queda inactivo y su corral libre; B queda con `cabezas_iniciales += origen.cabezas_iniciales`. Se registra en un modelo `LoteFusion` para auditoría. Constraint de "un solo lote activo por corral" sigue intacta — la fusión nunca crea un segundo lote en el destino. | Realidad operativa: a veces juntan animales de 2 corrales en uno y dejan **un solo folio** capturado. |

---

## Decisiones pendientes — necesitan validación con Chamizal

Estas son las que **bloquean cerrar el diseño**. Tradeoffs tentativos para discutir:

### B1. Estados del lote

¿Qué estados manejamos en este spec? Opciones:

- **Mínimo (recomendado para B):** sólo `activo` booleano (igual que catálogos). El "estado operativo" (engorda, transición, zilpaterol, cerrado) se infiere de las fechas y los registros que entren en Specs D/E.
- **Estados explícitos:** un enum `estado` con `formación · engorda · transición · zilpaterol · cerrado`. Más claro para reportes pero requiere transiciones manuales o automatizadas.

Recomendación: **mínimo**, e introducir el enum en Spec D cuando lleguen los submódulos que lo necesitan.

### B2. ¿"Sexo" del dummy v4 = TipoGanado o un campo aparte?

El dummy muestra "Macho / Hembra / Hembra-Vaca" en alta de lote. La opción "Hembra-Vaca" no existe en `TipoGanado` (Macho / Hembra / Vaca). Tres caminos:

- **(a)** El campo del lote es FK a `TipoGanado` directamente (3 valores). Si Chamizal necesita "Hembra-Vaca" se agrega como cuarto valor del catálogo.
- **(b)** El campo del lote es FK a `TipoGanado` + un boolean `es_vaca_adulta` para distinguir "Hembra de engorda" de "Hembra-Vaca productora".
- **(c)** Un campo enum independiente.

Recomendación: **(a)**. Si surge la necesidad, agregar fila al catálogo es trivial.

### B3. Validación de capacidad

Si un corral tiene `capacidad_maxima=200` y intentan crear un lote con `cabezas_iniciales=220`:

- **(a)** Error duro: el form rechaza el alta.
- **(b)** Advertencia + override: el operador puede forzar con un checkbox.
- **(c)** Sin validación: el campo es informativo.

Recomendación: **(a)** estricto en alta. El operador rara vez quiere superar capacidad — si lo necesita por excepción, edita la `capacidad_maxima` del corral primero.

### B4. ¿Múltiples lotes por corral?

El dummy sugiere 1 lote por corral, pero el modelo de datos podría aceptar varios (un corral grande con dos sublotes, p.ej.).

- **(a)** Constraint: un solo lote activo por corral. Simple y refleja la operación real del cliente.
- **(b)** Múltiples lotes activos por corral. Permite más flexibilidad pero complica los cálculos de ocupación.

Recomendación: **(a)**. Mover ganado entre corrales se modela con histórico de cambios (Spec C/D), no con multiplicar lotes.

### B5. Captura de peso de entrada

Dummy muestra "Peso inicio prom. (kg)". Una decisión: ¿es **el promedio del lote completo** o **el peso del primer animal pesado**?

- **(a)** Promedio del lote (operador ingresa un valor representativo). Simple.
- **(b)** Promedio calculado de un sub-pesaje (ej. pesa 10 cabezas y promedia). Requiere un modelo `Pesaje` con detalle.

Recomendación: **(a)** en Spec B. Los pesajes detallados pueden llegar en Spec D.

### B6. Folio: ¿qué pasa si el operador escribe uno que ya existe?

- **(a)** Constraint `unique=True` → IntegrityError → form lo presenta como error.
- **(b)** Permitir duplicados (caso pragmático de re-uso de folio histórico).

Recomendación: **(a)** unique. Si necesitan reusar un folio cerrado, primero deben reactivar/limpiar el viejo.

---

## Modelo de datos

### `apps/lotes/models.py` (app nueva)

```python
from datetime import date, timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords

from apps.catalogos.models import (
    Corral,
    ProgramaReimplante,
    Proveedor,
    TipoGanado,
    TipoOrigen,
)
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
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, null=True, blank=True
    )

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
        help_text="Si está vacío, se toma del programa de reimplante aplicable.",
    )
    gdp_esperada = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="GDP esperada (kg/día)",
        help_text="Si está vacío, se toma del programa de reimplante aplicable.",
    )
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
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

    # ----- Resolución del programa aplicable -----

    @property
    def programa(self):
        return ProgramaReimplante.resolver(
            self.tipo_ganado, self.tipo_origen, self.peso_inicial_promedio
        )

    # ----- Valores efectivos (lo que captura el operador o lo que viene del programa) -----

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

    # ----- Cálculos derivados -----

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
        """n=1 primer reimplante, n=2 segundo, etc."""
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

    # ----- Entrada a zilpaterol -----

    @property
    def fecha_entrada_zilpaterol(self):
        if not self.programa or not self.fecha_proyectada_venta:
            return None
        return self.fecha_proyectada_venta - timedelta(days=self.programa.dias_zilpaterol)
```

> **Nota sobre la constraint `lote_unico_activo_por_corral`**: implementa la decisión B4(a). Si el cliente prefiere B4(b), se quita esta línea y se ajusta el formulario.

### `LoteFusion` — registro de fusiones

```python
class LoteFusion(TimeStampedModel):
    """Una fila por cada vez que un lote 'origen' se fusiona en un lote 'destino'.

    Operación atómica:
      - destino.cabezas_iniciales += origen.cabezas_iniciales
      - destino.observaciones se anota
      - origen.activo = False
      - origen.observaciones se anota
      - se crea esta fila

    No modifica peso_inicial_promedio del destino — el operador decidió cuál folio
    conservar y por tanto cuál peso es el "oficial". Si necesitan promedio
    ponderado en el futuro, se agrega como cálculo derivado.
    """
    lote_destino = models.ForeignKey(
        Lote, on_delete=models.PROTECT, related_name="fusiones_recibidas"
    )
    lote_origen = models.ForeignKey(
        Lote, on_delete=models.PROTECT, related_name="fusiones_dadas"
    )
    cabezas_movidas = models.PositiveIntegerField()
    fecha_fusion = models.DateField()
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_fusion", "-created_at"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(lote_destino=models.F("lote_origen")),
                name="fusion_destino_distinto_de_origen",
            ),
        ]

    def __str__(self):
        return f"{self.lote_origen.folio} → {self.lote_destino.folio} ({self.cabezas_movidas} cab.)"
```

**Por qué un modelo separado y no sólo `Lote.fusionar()`:**
- Trazabilidad: el cliente quiere poder reconstruir "de dónde salieron las 180 cabezas que tiene este corral hoy".
- Reportes futuros: Spec D/E pueden necesitar listar todas las fusiones del año.
- Auditoría más limpia que sólo confiar en `simple_history` del campo `cabezas_iniciales`.

### Ajuste del modelo `Corral` existente

`Corral.ocupacion_actual` actualmente devuelve `0` (placeholder de Spec A). En este spec lo conectamos:

```python
@property
def ocupacion_actual(self) -> int:
    lote = self.lotes.filter(activo=True).first()
    return lote.cabezas_iniciales if lote else 0
```

> En Spec C/D esto crecerá para considerar muertes y ventas parciales. Por ahora `ocupacion_actual = cabezas_iniciales del lote activo`.

---

## URLs y vistas

```python
# apps/lotes/urls.py
urlpatterns = [
    path("", views.LoteListView.as_view(), name="lote_list"),
    path("nuevo/", views.LoteCreateView.as_view(), name="lote_create"),
    path("<int:pk>/", views.LoteDetailView.as_view(), name="lote_detail"),
    path("<int:pk>/editar/", views.LoteUpdateView.as_view(), name="lote_update"),
    path("<int:pk>/eliminar/", views.LoteDeleteView.as_view(), name="lote_delete"),
    path("<int:pk>/fusionar/", views.LoteFusionView.as_view(), name="lote_fusionar"),
    # HTMX endpoint que devuelve el bloque de "proyección automática" para el form
    path("preview-proyeccion/", views.PreviewProyeccionView.as_view(), name="lote_preview"),
]
```

Montaje en `config/urls.py`: `path("lotes/", include("apps.lotes.urls", namespace="lotes"))`.

### Vista `PreviewProyeccionView`

Endpoint HTMX que recibe los campos clave del form (`tipo_ganado_id`, `tipo_origen_id`, `peso_inicial`, `fecha_inicio`, `cabezas_iniciales`, opcionalmente `peso_salida_objetivo`, `gdp_esperada`) y renderiza un partial (`_proyeccion_preview.html`) con las propiedades calculadas (días, fechas, kilos). El form de alta tiene `hx-post="..."`, `hx-trigger="change delay:300ms from:.proyeccion-input"`, `hx-target="#proyeccion-box"`.

Esto da la UX del dummy v4 (proyección viva mientras el operador captura) sin guardar nada.

### Vista `LoteFusionView`

Form en `/lotes/<pk>/fusionar/` donde el operador:
- Selecciona el **lote origen** (dropdown filtrado a lotes activos distintos al destino actual).
- Captura `fecha_fusion` (default = hoy).
- Captura `notas` (opcional).
- (`cabezas_movidas` se llena automáticamente con el inventario completo del origen — fusión total, no parcial.)

Submit ejecuta dentro de `transaction.atomic()`:

```python
@transaction.atomic
def fusionar(destino, origen, fecha_fusion, notas, usuario):
    cabezas = origen.cabezas_iniciales

    LoteFusion.objects.create(
        lote_destino=destino,
        lote_origen=origen,
        cabezas_movidas=cabezas,
        fecha_fusion=fecha_fusion,
        notas=notas,
    )

    destino.cabezas_iniciales += cabezas
    destino.observaciones += (
        f"\n[{fecha_fusion}] Fusión: +{cabezas} cab. del lote {origen.folio}."
    )
    destino.save()

    origen.activo = False
    origen.observaciones += (
        f"\n[{fecha_fusion}] Fusionado a lote {destino.folio}."
    )
    origen.save()
```

Resultado:
- `destino.cabezas_iniciales` aumenta.
- `origen.activo = False` libera su corral (la constraint `lote_unico_activo_por_corral` se respeta porque el origen ya no es activo).
- Trazabilidad queda en `LoteFusion`.

### Sidebar

Añadir al sidebar bajo una sección nueva "Operación":

```html
<div class="ndiv"></div>
<div class="nsec">Operación</div>
<a class="ni" href="/lotes/">
  <span class="ico">🐂</span> Lotes
</a>
```

(El icono emoji 🐂 sigue el patrón del dummy v4. Si el cliente prefiere otro símbolo, se cambia.)

---

## Permisos

Migración data `apps/lotes/migrations/0002_seed_lote_perms.py` que extiende los grupos:

| Grupo | Permisos sobre Lote |
|---|---|
| Administrador | Todos |
| Gerente | `view`, `change` (para correcciones), `delete` |
| Capturista | `view`, `add`, `change` |
| Solo Lectura | `view` |

> Capturista por fin tiene permisos operativos. Esto cierra el ciclo abierto en Spec A donde Capturista sólo veía catálogos.

---

## Criterios de aceptación

| # | Criterio | Verificación |
|---|---|---|
| 1 | Crear lote con captura mínima funciona y guarda en BD. | Test integration `test_lote_create.py`. |
| 2 | Folio duplicado es rechazado por el form. | Test unit `test_lote_folio_unique`. |
| 3 | Cabezas iniciales > capacidad del corral es rechazado. | Test form `test_capacidad_corral`. |
| 4 | Un corral con lote activo no acepta un segundo lote activo. | Test integrity `test_un_lote_activo_por_corral`. |
| 5 | `lote.dias_engorda_proyectados` calcula correctamente para casos del Excel. | Tests sobre fixtures con cifras conocidas. |
| 6 | Endpoint HTMX `/lotes/preview-proyeccion/` devuelve el bloque con valores calculados sin guardar. | Test view. |
| 7 | Capturista crea/edita lote pero no puede eliminar. | Test permissions. |
| 8 | Lote inactivo (`activo=False`) deja de ocupar el corral en `Corral.ocupacion_actual`. | Test property. |
| 9 | Cambio de `gdp_esperada` queda registrado en `lote.history`. | Test simple_history. |
| 10 | Fusionar lote A en lote B suma cabezas en B, marca A inactivo y libera el corral de A. | Test integration `test_lote_fusion_basica`. |
| 11 | Fusión queda registrada en `LoteFusion` con destino/origen/cabezas/fecha. | Test `test_fusion_genera_registro`. |
| 12 | No se puede fusionar un lote consigo mismo (DB constraint + form). | Test `test_fusion_self_rechazada`. |
| 13 | No se puede fusionar un lote inactivo como origen. | Test `test_fusion_origen_debe_estar_activo`. |
| 14 | Capturista puede fusionar; Solo Lectura no. | Test `test_fusion_permisos`. |
| 15 | Cobertura ≥ 85% en `apps/lotes/`. | `pytest --cov=apps.lotes --cov-fail-under=85`. |

---

## Plan de implementación tentativo

(El plan detallado con tasks TDD se genera **después** de validar el diseño.)

Estimado: **18–22 tasks** divididos en ~5 fases:

1. **Foundation** (3 tasks): app `apps/lotes`, modelo `Lote`, migrations base.
2. **Cálculos** (4 tasks): properties + tests numéricos contra el Excel.
3. **CRUD UI** (6 tasks): form + vistas + templates + sidebar entry + HTMX preview.
4. **Fusión** (4 tasks): modelo `LoteFusion`, función atómica `fusionar()`, vista + form, tests.
5. **Permisos + cierre** (3 tasks): migración de seed groups (Capturista add/change/add_fusion), tests E2E, smoke checklist.

---

## Fuera del alcance

- Movimientos entre corrales sin fusionar (transferir lote de C03 a C07 manteniendo folio).
- Dispersión (dividir un lote en sublotes).
- **Fusión parcial** (mover sólo N cabezas de A a B y dejar A activo). En este spec la fusión es total: A queda vacío e inactivo. Si Chamizal pide fusión parcial, lo movemos a Spec C como sub-feature.
- Pesajes detallados (registrar 10 pesajes individuales y promediar).
- Tracking de muertes / ventas parciales que ajusten `cabezas_actuales`.
- Pantalla de Disponibilidad (Spec C).
- Reimplantes/transiciones/zilpaterol como flujos operativos con registro de fechas reales (Spec D).

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Las decisiones B1–B6 cambian → modelos hay que reescribir. | Validar con cliente ANTES de generar el plan TDD. Por eso este doc está marcado DRAFT. |
| El cliente quiere movimientos/dispersión EN este spec. | Negociar a Spec B fase 2 (sub-spec) o moverlo a inicio de Spec C. Cualquier flujo adicional aquí infla este spec más allá de 4–5 días de trabajo. |
| Los cálculos de proyección no matchean con el Excel del cliente al 100%. | Crear tests con casos del Excel actual (`docs/DISPONIBILIDAD 2026 1.xlsx`) como golden master. |
| `unique` por corral activo bloquea casos legítimos. | Si pasa, levantar el constraint y aceptar B4(b). |

---

## Próximos pasos

1. **Sesión de revisión con Chamizal** sobre las decisiones B1–B6 y los criterios de aceptación.
2. Una vez firmado el alcance, generar `docs/superpowers/plans/2026-XX-XX-sicoga-spec-b-lotes-formacion-plan.md` con tasks TDD.
3. Ejecución vía superpowers:subagent-driven-development (mismo flujo que Spec A).
4. Cierre con smoke manual y push.
