# SiCoGa — Spec E: Cierre del Lote (Diseño)

**Fecha:** 2026-04-30
**Estado:** 🚧 **DRAFT — pendiente de validación con Chamizal**
**Cliente:** Chamizal Camperos
**Spec previo:** [D — Submódulos Operativos](./2026-04-30-sicoga-spec-d-submodulos-operativos-design.md) ✅ entregado

## Contexto

Specs A-D cubren el ciclo de vida del lote: alta, seguimiento, eventos operativos. Spec E cierra el ciclo: registra los costos e ingresos reales y produce el **cierre técnico-financiero** del lote (GDP real, conversión alimenticia, mortalidad, costo total, margen).

## Objetivo

Al cerrar Spec E, el sistema permite:

1. Registrar **muertes** con causa, peso estimado y costo imputado.
2. Registrar **ventas reales** (totales o parciales) con cliente, cabezas, kilos, precio.
3. Capturar **datos de compra/recepción**: cabezas origen vs recibidas (merma de tránsito), costo de compra.
4. Registrar **alimentación** consumida por fórmula con costos.
5. Registrar **medicación** (metafilaxia + hospital).
6. Calcular **días-animal netos** y aplicar costo hotel configurable.
7. Generar la pantalla de **Cierre** con resumen técnico-financiero consolidado.

## Partición — 5 sub-specs

| Sub-spec | Alcance | Tasks aprox. |
|---|---|---|
| **E.1 — Muertes y Ventas** | Modelos `Muerte` y `Venta`, `cabezas_actuales` derivado, mortalidad %, vistas y captura. | ~10 |
| **E.2 — Compra / Recepción** | Datos de origen del lote (campos en `Lote` o modelo `Recepcion`), merma tránsito, costo compra. | ~5 |
| **E.3 — Alimentación y Medicación** | Catálogos `Formula` + `Medicamento`, modelos `Alimentacion` y `Medicacion`. | ~10 |
| **E.4 — Costo Hotel** | Configuración de componentes (agua, mano de obra, etc.) y cálculo de días-animal netos. | ~3 |
| **E.5 — Cierre consolidado** | Pantalla `/cierre/<lote>/` con resumen técnico+financiero, GDP real, conversión, margen, export PDF/Excel. | ~5 |

**Total: ~33 tasks** distribuidos entre 5 sub-specs.

> Recomendación: ejecutar E.1 primero (es el más crítico para operación diaria). E.2-E.5 pueden seguir si Chamizal sigue priorizando, o pausar para validar con datos reales.

---

## E.1 — Muertes y Ventas (alcance del primer sub-spec)

### Modelo `Muerte`

```python
class Muerte(AuditableModel):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="muertes")
    fecha = models.DateField()
    arete = models.CharField(max_length=20, blank=True, help_text="Identificador del animal")
    causa = models.CharField(max_length=80, blank=True, help_text="Neumonía, timpanismo, etc.")
    peso_estimado = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-fecha", "-created_at"]
```

### Modelo `Venta`

```python
class Venta(AuditableModel):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="ventas")
    fecha = models.DateField()
    cliente = models.CharField(max_length=120, blank=True)
    cabezas = models.PositiveIntegerField()
    kilos = models.DecimalField(max_digits=8, decimal_places=2)
    precio_kg = models.DecimalField(max_digits=8, decimal_places=2)
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    @property
    def ingreso_total(self):
        return self.kilos * self.precio_kg

    @property
    def peso_promedio(self):
        return self.kilos / self.cabezas if self.cabezas else 0

    @property
    def precio_cabeza(self):
        return self.ingreso_total / self.cabezas if self.cabezas else 0
```

### Properties nuevas en `Lote`

```python
@property
def cabezas_muertas(self):
    return self.muertes.filter(activo=True).count()

@property
def cabezas_vendidas(self):
    return self.ventas.filter(activo=True).aggregate(s=Sum("cabezas"))["s"] or 0

@property
def cabezas_actuales(self):
    return self.cabezas_iniciales - self.cabezas_muertas - self.cabezas_vendidas

@property
def mortalidad_pct(self):
    if self.cabezas_iniciales == 0:
        return 0
    return Decimal(self.cabezas_muertas) / self.cabezas_iniciales * 100

@property
def ingreso_total_ventas(self):
    return sum(v.ingreso_total for v in self.ventas.filter(activo=True))
```

### Pantallas

- `/cierre/lotes/<pk>/muertes/` — lista + form para registrar muerte de un lote.
- `/cierre/lotes/<pk>/ventas/` — lista + form para registrar venta (parcial o total).
- En `Lote.detail`: nuevos bloques "Muertes" y "Ventas" con totales y link a las pantallas detalle.
- Update **Disponibilidad** y **Inventario General** para mostrar `cabezas_actuales` en lugar de `cabezas_iniciales` cuando hay muertes/ventas.

### Permisos

- Capturista: `add/view` sobre `Muerte` y `Venta` (operativos diarios).
- Admin/Gerente: `change/delete` adicionales.

---

## Decisiones tomadas (Spec E global)

| # | Decisión | Valor |
|---|---|---|
| 1 | App | `apps.cierre` (nueva). |
| 2 | URL prefix | `/cierre/`. |
| 3 | Auditoría | `simple_history` en todos los nuevos modelos. |
| 4 | Borrado | Lógico (`activo=False`). |
| 5 | `cabezas_actuales` | Calculado: iniciales − muertes − vendidas. No campo persistente. |
| 6 | Capturista | `add/view` operativos en todos los modelos. |

---

## Decisiones pendientes (las atendemos cuando lleguemos al sub-spec)

- **E2.1**: Datos de compra → ¿campos en `Lote` o modelo separado `Recepcion`? Recomendación: campos en `Lote` (es 1-a-1 con el lote).
- **E3.1**: Catálogo de fórmulas → ¿qué campos exactos? F1, F1+F3, F3, F3+Zilp, etc., con costo/kg.
- **E3.2**: Medicación → ¿estructura del catálogo? Nombre, principio activo, dosis_default, costo/unidad.
- **E4.1**: Costo hotel → ¿singleton de configuración o histórico de versiones?
- **E5.1**: Export PDF — ¿qué template, qué dependencias añadimos? (`reportlab`, `weasyprint`).

---

## Plan tentativo

Cuando cliente firme: generar plan TDD detallado por sub-spec, ejecutar E.1 → E.2 → E.3 → E.4 → E.5, smoke por sub-spec.

---

## Próximos pasos

1. Validar con Chamizal el alcance partido E.1-E.5.
2. Arrancar **E.1 (Muertes y Ventas)** — más crítico operativamente.
3. Pausa post-E.1 para que Chamizal capture datos reales antes de seguir con compra/alimentación/cierre.
