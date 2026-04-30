# SiCoGa — Spec D: Submódulos Operativos (Diseño)

**Fecha:** 2026-04-30
**Estado:**
- 🚧 **DRAFT** general; sub-spec D.1 (Reimplantes) ✅ **ENTREGADO 2026-04-30** — 158 tests, cobertura 87.25% en `apps.operacion`. D.2-D.4 pendientes de priorizar con Chamizal.
**Cliente:** Chamizal Camperos
**Spec previo:** [C — Disponibilidad](./2026-04-30-sicoga-spec-c-disponibilidad-design.md) ✅ entregado

## Contexto

Specs A, B, C dejaron el sistema con catálogos, lotes, cálculos derivados, y la pantalla operativa principal con 49 reglas precargadas del Excel. Pero el sistema **sólo refleja proyecciones** — todavía no captura los eventos operativos reales que ocurren día con día en el rancho:

- Aplicación de reimplantes (¿a qué lote, qué día, qué tipo, qué peso?).
- Transiciones de alimentación (F1 → F3, etc.).
- Entrada formal a fase de Zilpaterol (que dispara el reloj de 35 días para venta).
- Pesajes reales que corrigen las proyecciones de peso actual.
- Inventario general consolidado (corrales + potreros).
- Vistas de calendario y reporte (salidas por semana, proyección anual).

Spec D introduce los modelos y pantallas para todos estos eventos. **Es el spec más grande del proyecto** — proponemos partirlo en 4 sub-fases entregables independientes (D.1 a D.4).

## Objetivo

Al cerrar Spec D completo, el sistema permite:

1. Registrar la **aplicación de cada reimplante** (cuál lote, cuándo, qué tipo de implante, peso aplicado).
2. Registrar **transiciones de alimentación** entre fases.
3. Registrar la **entrada formal a Zilpaterol** (35 días previos a venta).
4. Capturar **pesajes reales** que actualizan la proyección.
5. Ver **calendarios semanales** de pendientes/aplicados para cada tipo de evento.
6. Ver el **inventario general consolidado** (corrales + potreros).
7. Consultar la **proyección anual** (semana a semana).
8. Catálogo de **Implantes** (FK desde Reimplante).
9. Catálogo de **Potreros** (espejo de Corral pero para ganado en pastoreo).

Lo que **NO** entra (queda para E):
- Compra/recepción del lote con costo (Spec E).
- Muertes (mortalidad) — Spec E.
- Ventas reales con cliente, kilos, precio — Spec E.
- Alimentación con consumo por fórmula y costos — Spec E.
- Medicación (metafilaxia) — Spec E.
- Cierre técnico-financiero del lote — Spec E.

---

## Propuesta de partición — 4 sub-specs

| Sub-spec | Alcance | Tasks aprox. | Valor |
|---|---|---|---|
| **D.1 — Reimplantes** | Catálogo de Implantes, modelo `Reimplante`, calendario pendientes/aplicados, captura. | ~10 | 🔥 Alto — el reimplante es el evento más frecuente y crítico. |
| **D.2 — Transiciones y Zilpaterol** | Modelos `Transicion` y `EntradaZilpaterol`, sus calendarios y formularios. | ~8 | Medio-alto — completa el flujo de fases. |
| **D.3 — Pesajes y proyección de peso** | Modelo `Pesaje`, ajuste de proyecciones a partir del último pesaje, vista. | ~6 | Medio — corrige drift entre proyectado y real. |
| **D.4 — Reportes operativos** | Catálogo de Potreros, vista Inventario General, Proyección Anual, Salidas por semana. | ~7 | Alto para gerencia, opcional para operación diaria. |

> **Recomendación**: ejecutar D.1 → smoke con Chamizal → D.2 → smoke → D.3 → D.4. Cada sub-spec es un PR/release independiente. Si Chamizal valida D.1 y siente que cubre lo crítico, podemos pausar y pasar a Spec E (Cierre). Si quieren más, seguimos con D.2-D.4.

---

## Decisiones tomadas (aplican a todo Spec D)

| # | Decisión | Valor |
|---|---|---|
| 1 | Registro de eventos | Cada evento es un modelo nuevo con FK a `Lote`, fecha, datos específicos del evento, y `simple_history`. |
| 2 | Permisos | Capturista gana `add/view` sobre todos los modelos nuevos. Admin/Gerente además `change/delete`. |
| 3 | Calendario | Cada submódulo tiene una vista tipo "/operacion/X/" con tabla por semana mostrando pendientes (calculados de `Lote.fecha_X_proyectada`) + historial (registros reales en BD). |
| 4 | Captura | Form modal-like en la misma vista de calendario, o página `/operacion/X/registrar/` con `?lote=Y&fecha=Z` prellenado. |
| 5 | Borrado | Lógico (`activo=False`) en todos los modelos. |
| 6 | URL prefix | `/operacion/` (app `apps.operacion`). Subdomain en futuras specs si crece. |

---

## Decisiones pendientes — necesitan validación con Chamizal

### D1. Catálogo de Implantes: ¿qué fields?

Mínimo: `nombre` (ej. "Revalor-G", "Component TE-200"), `notas`, `activo`.

Adicional posible: `principio_activo`, `dosis_default_mg`, `frasco_ml`, `costo_unitario`. Útiles para Spec E (medicación) pero no estrictamente necesarios en D.1.

**Recomendación**: empezar con `nombre + notas + activo`. Los campos de costo/dosis se agregan en Spec E cuando se necesiten.

### D2. ¿Cómo se llena el "tipo de implante" del registro?

- **(a)** FK al catálogo Implante. Operador elige de un dropdown.
- **(b)** Texto libre prefilled con el implante sugerido del programa (`programa.implante_inicial` / `reimplante_1` / etc.).
- **(c)** Ambos: FK con override manual si el texto del programa no matchea ningún catálogo.

**Recomendación**: **(a) FK al catálogo**. Migración inicial siembra el catálogo con los implantes únicos que aparecen en el programa actual ("REV. G", "60 DIAS REV. IMPX", "REV. H + XR", etc.), y luego el `programa.implante_inicial` se vuelve también FK al catálogo. Es un breaking change menor pero deja todo consistente.

### D3. ¿Pesajes individuales o promedio?

- **(a)** Cada pesaje es UN registro con peso promedio del lote (operador estima).
- **(b)** Cada pesaje permite capturar pesos individuales de N cabezas y calcular promedio automáticamente.

**Recomendación**: **(a) promedio**. El cliente trabaja en grupo, no individualmente. La granularidad fina puede entrar en Spec G si CATLE la trae.

### D4. ¿Potreros heredan de Corral o son modelo aparte?

- **(a)** Reusar `Corral` con `TipoCorral.nombre = "Potrero"`. Cero código nuevo, pero se mezcla en queries.
- **(b)** Crear modelo `Potrero` separado. Más limpio operativamente, pero duplica código.

**Recomendación**: **(a) reusar Corral**. Ya tenemos seed de TipoCorral con 3 valores; se puede agregar "Potrero" sin friccion. Las queries que sólo quieren corrales filtran por `tipo_corral.nombre != "Potrero"`.

### D5. Bulk capture

Para Reimplantes p.ej.: ¿el operador captura uno por uno o puede aplicar el mismo implante a múltiples lotes en una pantalla?

**Recomendación**: empezar con captura **uno por uno**. Si en uso real Chamizal pide bulk, lo agregamos después.

---

## Modelo de datos — Sub-spec D.1 (Reimplantes)

### `apps.catalogos.Implante` (catálogo nuevo)

```python
class Implante(AuditableModel):
    nombre = models.CharField(max_length=60, unique=True)
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

Data migration que siembra los nombres únicos extraídos de `ProgramaReimplante.implante_inicial`, `reimplante_1`, ..., `reimplante_4`.

### `apps.operacion.Reimplante`

```python
class Reimplante(AuditableModel):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="reimplantes")
    fecha_aplicada = models.DateField()
    numero = models.PositiveSmallIntegerField(
        choices=[(0, "Implante inicial"), (1, "1er reimplante"), (2, "2do"), (3, "3er"), (4, "4to")],
        default=0,
        help_text="0 = implante inicial; 1-4 = reimplantes consecutivos.",
    )
    implante = models.ForeignKey(Implante, on_delete=models.PROTECT)
    peso_aplicado = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Peso promedio del lote al aplicar el reimplante (kg). Opcional pero útil para reportes.",
    )
    cabezas_aplicadas = models.PositiveIntegerField(
        help_text="Cuántas cabezas recibieron el implante. Default = cabezas_iniciales del lote.",
    )
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["-fecha_aplicada", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "numero"],
                name="reimplante_unico_por_lote_y_numero",
            ),
        ]

    def __str__(self):
        return f"{self.lote.folio} · {self.get_numero_display()} · {self.fecha_aplicada}"
```

> El `numero` permite distinguir "ya se aplicó el inicial pero falta el 1ero" en queries de pendientes.

### Vista calendario

`/operacion/reimplantes/` muestra:

- KPIs: pendientes esta semana, próxima semana, completados año, lotes en programa.
- Tabla por semana de **pendientes** (lotes activos con `fecha_reimplante_1/2/3` proyectada en esa semana, sin `Reimplante` registrado para ese número).
- Tabla histórica de últimos N **aplicados**.
- Botón "✔ Registrar" abre form prellenado para el lote/número correspondiente.

### `Lote.proximo_reimplante_pendiente` (helper)

```python
@property
def proximo_reimplante_pendiente(self):
    """Devuelve (numero, fecha_proyectada) del siguiente reimplante que falta aplicar.

    Si ya se aplicaron los 3 (o 4 para machos), devuelve None.
    """
    aplicados = set(self.reimplantes.filter(activo=True).values_list("numero", flat=True))
    for n in (1, 2, 3):
        if n not in aplicados:
            return n, self.fecha_reimplante(n)
    return None
```

---

## Modelo de datos — Sub-spec D.2 (Transiciones y Zilpaterol)

### `Transicion`

```python
class Transicion(AuditableModel):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="transiciones")
    fecha = models.DateField()
    de_fase = models.CharField(max_length=20, choices=[
        ("F1", "F1"), ("FT", "F1+F3 transición"), ("F3", "F3"),
    ])
    a_fase = models.CharField(max_length=20, choices=[
        ("FT", "F1+F3 transición"), ("F3", "F3"), ("F3Z", "F3+Zilpaterol"),
    ])
    proporcion = models.CharField(max_length=20, blank=True, help_text="Ej: 50/50, 100% F3.")
    notas = models.TextField(blank=True)
    history = HistoricalRecords()
```

### `EntradaZilpaterol`

```python
class EntradaZilpaterol(AuditableModel):
    lote = models.OneToOneField(Lote, on_delete=models.PROTECT, related_name="entrada_zilpaterol")
    fecha_entrada = models.DateField()
    observaciones = models.TextField(blank=True)
    history = HistoricalRecords()

    @property
    def fecha_salida_proyectada(self):
        """fecha_entrada + 35 días (mínimo legal de Zilpaterol antes de venta)."""
        from datetime import timedelta
        return self.fecha_entrada + timedelta(days=35)
```

> `OneToOneField` porque cada lote entra a Zilpaterol exactamente una vez.

---

## Modelo de datos — Sub-spec D.3 (Pesajes)

### `Pesaje`

```python
class Pesaje(AuditableModel):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="pesajes")
    fecha = models.DateField()
    peso_promedio = models.DecimalField(max_digits=6, decimal_places=2)
    cabezas_pesadas = models.PositiveIntegerField(
        help_text="¿Cuántas cabezas se pesaron? Si fue muestreo, este número es < cabezas_iniciales.",
    )
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-fecha"]
```

### Ajuste de proyección

`Lote.peso_actual_proyectado` (ya existe en Spec C) cambia a:

```python
@property
def peso_actual_proyectado(self):
    """Si hay pesajes, parte del último; si no, del peso inicial."""
    ultimo = self.pesajes.filter(activo=True).order_by("-fecha").first()
    base_peso = ultimo.peso_promedio if ultimo else self.peso_inicial_promedio
    base_fecha = ultimo.fecha if ultimo else self.fecha_inicio
    if not self.gdp_efectiva:
        return None
    from datetime import date
    dias = (date.today() - base_fecha).days
    return base_peso + (dias * self.gdp_efectiva)
```

> Test golden: con un pesaje real intermedio, la proyección actual usa ese pesaje en lugar del inicial. Sin pesajes, comportamiento idéntico al actual.

---

## Modelo de datos — Sub-spec D.4 (Reportes)

### `Potrero` reusando `Corral`

Sólo un seed extra en `TipoCorral`: agregar "Potrero". No hay modelo nuevo. Las vistas de "corrales" filtran por `tipo_corral.nombre != "Potrero"` y la vista de "potreros" filtra por `tipo_corral.nombre == "Potrero"`.

### Vistas

- `/operacion/inventario/` — KPIs (total corrales, total potreros, total Chamizal, ocupados/total) + dos tablas (corrales, potreros).
- `/operacion/proyeccion-anual/` — semana 1 a 52 del año seleccionado, con qué lotes salen cada semana.
- `/operacion/salidas-semanales/` — espejo de la sección "Venta por Semana" del dummy: las próximas 8 semanas, con cabezas y kilos proyectados, alertas de "sin salida".

Sin modelos nuevos, sólo views + templates.

---

## URLs

```python
# apps/operacion/urls.py
urlpatterns = [
    # D.1
    path("reimplantes/", views.ReimplantesCalendarioView.as_view(), name="reimplantes"),
    path("reimplantes/registrar/", views.RegistrarReimplanteView.as_view(), name="registrar_reimplante"),
    # D.2
    path("transiciones/", views.TransicionesCalendarioView.as_view(), name="transiciones"),
    path("transiciones/registrar/", views.RegistrarTransicionView.as_view(), name="registrar_transicion"),
    path("zilpaterol/", views.ZilpaterolCalendarioView.as_view(), name="zilpaterol"),
    path("zilpaterol/registrar/", views.RegistrarEntradaZilpaterolView.as_view(), name="registrar_zilp"),
    # D.3
    path("pesajes/", views.PesajesView.as_view(), name="pesajes"),
    path("pesajes/registrar/", views.RegistrarPesajeView.as_view(), name="registrar_pesaje"),
    # D.4
    path("inventario/", views.InventarioGeneralView.as_view(), name="inventario"),
    path("proyeccion-anual/", views.ProyeccionAnualView.as_view(), name="proyeccion_anual"),
    path("salidas-semanales/", views.SalidasSemanalesView.as_view(), name="salidas_semanales"),
]
```

Montaje: `path("operacion/", include("apps.operacion.urls", namespace="operacion"))`.

---

## Sidebar

Después de Spec D el sidebar queda:

```
Operación
  📊 Disponibilidad
  🐂 Lotes
  💉 Reimplantes
  🔄 Transiciones
  ⚡ Zilpaterol
  ⚖️ Pesajes
  📦 Inventario
  📅 Proyección anual
  📈 Salidas por semana

Catálogos
  ...

Próximamente
  Cierre de Lotes
  Reportes ejecutivos
```

---

## Permisos

Migración data que extiende:

| Grupo | Permisos nuevos |
|---|---|
| Administrador | Todos. |
| Gerente | view + change en todo. |
| Capturista | view + add para Reimplante, Transicion, EntradaZilpaterol, Pesaje. |
| Solo Lectura | view en todo. |

---

## Criterios de aceptación (resumidos por sub-spec)

### D.1 — Reimplantes
1. Crear catálogo Implante con seed inicial.
2. Registrar reimplante para un lote queda en BD y aparece en historial.
3. Calendario muestra pendientes correctos (lotes con fecha proyectada en la semana sin reimplante registrado).
4. Capturista crea reimplante; Solo Lectura recibe 403.
5. Cobertura ≥ 85% en `apps.operacion` y nuevos modelos.

### D.2 — Transiciones y Zilpaterol
6. Cada lote sólo puede tener una `EntradaZilpaterol` (OneToOne).
7. `EntradaZilpaterol.fecha_salida_proyectada` = fecha_entrada + 35 días.
8. Calendario de transiciones muestra próximas correctamente.

### D.3 — Pesajes
9. `Lote.peso_actual_proyectado` con un pesaje intermedio devuelve valor correcto basado en el pesaje, no en el inicial.
10. Sin pesajes, comportamiento idéntico al actual.

### D.4 — Reportes
11. Inventario General muestra KPIs correctos.
12. Proyección Anual lista las 52 semanas con lotes que salen.
13. Salidas Semanales detecta correctamente "Sin salida" en semanas sin lotes.

---

## Plan de implementación tentativo

**D.1** (~10 tasks): Foundation (app + Implante + seed) → Reimplante model → calendario view → registrar form → permisos + tests + cierre.

**D.2** (~8 tasks): Transicion model → calendario → registrar → EntradaZilp model (OneToOne) → calendario → registrar → tests → cierre.

**D.3** (~6 tasks): Pesaje model → registro view → ajuste de `peso_actual_proyectado` → tests golden → vista lista pesajes → cierre.

**D.4** (~7 tasks): seed Potrero → InventarioGeneralView → ProyeccionAnualView → SalidasSemanalesView → sidebar update → tests → cierre.

**Total Spec D completo: ~31 tasks** distribuidos en 4 sub-specs de 1-2 días cada uno.

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Spec inflado: 31 tasks es mucho de un jalón. | Partir en D.1-D.4 (recomendación principal). Cada uno se entrega independiente. |
| El cliente quiere captura masiva. | Cubierto en D5 (decisión pendiente). Si dice sí, agregamos al final de cada sub-spec. |
| Catálogo de Implantes no matchea con los nombres del Excel. | Migration inicial extrae nombres únicos del programa actual; cliente los limpia/renombra desde el admin. |
| Pesajes individuales (D3 alternativa b). | Documentado como decisión pendiente; mi recomendación es promedios, no individuales. |

---

## Próximos pasos

1. Validar con Chamizal:
   - ¿Mantener Spec D unificado o partir en D.1–D.4?
   - Decisiones D1–D5.
2. Si D.1–D.4 separados: arrancar D.1 (Reimplantes) primero — es el evento más frecuente.
3. Generar plan TDD del sub-spec acordado.
4. Ejecutar.
