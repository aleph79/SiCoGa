# SiCoGa — Spec C: Disponibilidad y Proyección (Diseño)

**Fecha:** 2026-04-30
**Estado:** ✅ **ENTREGADO 2026-04-30** — 150 tests, cobertura 96.30% en `apps.disponibilidad`. Pendiente smoke manual con Chamizal.
**Cliente:** Chamizal Camperos
**Spec previo:** [B — Lotes y Formación](./2026-04-30-sicoga-spec-b-lotes-formacion-design.md) ✅ entregado 2026-04-30

## Contexto

Specs A y B dejaron el modelo de datos: catálogos, programa de reimplantes, lotes con cálculos derivados y operación de fusión. Spec C entrega la **pantalla principal del sistema** — la página que el operador y el gerente abren todos los días para ver "¿qué tengo en cada corral, dónde está, cuándo sale?".

La fuente de verdad es el reporte que Chamizal mantiene hoy en `docs/DISPONIBILIDAD 2026 1.xlsx`, hoja DISPONIBILIDAD. Spec C reemplaza ese Excel por una vista web siempre actualizada.

## Objetivo del Spec C

Al cerrar este spec, el sistema permite:

1. Ver `/disponibilidad/` (que se vuelve la home `/`) con 4 KPIs y una tabla por corral.
2. La tabla muestra cada corral del rancho con su lote activo (o "Libre"), incluyendo todas las columnas calculadas que hoy aparecen en el Excel: días transcurridos, peso actual proyectado, etapa, fecha 1er reimplante, semana de venta, etc.
3. Filtros HTMX por tipo de ganado, etapa, y mostrar/ocultar libres.
4. Exportar la tabla a CSV con un click.

Lo que **NO** entra (queda para C+):
- Mapa visual de corrales (Spec F dashboard).
- Indicadores operativos / progress bars / GDP real (necesita registros operativos de Spec D).
- Salidas proyectadas por semana como gráfica (Spec F).
- Carga manual de "peso actual real" (Spec D).

---

## Decisiones tomadas

| # | Decisión | Valor | Origen |
|---|---|---|---|
| 1 | Ruta | `/disponibilidad/`. Adicionalmente, `/` redirige aquí (reemplaza el placeholder de Spec A). | Es la pantalla operativa central. |
| 2 | Mostrar libres | La tabla muestra **todos los corrales activos**, con "Libre" en las columnas de lote cuando no hay lote activo. Filtro opcional permite ocultar libres. | Operador necesita ver dónde meter el siguiente lote. |
| 3 | Etapa automática | Se calcula por `dias_transcurridos` vs los días acumulados del `ProgramaReimplante` aplicable: Recepción → F1 → Transición → F3 → Zilpaterol → Post-Zilpaterol. | Coherencia con el Excel actual. |
| 4 | Peso actual proyectado | `peso_inicial + dias_transcurridos × gdp_efectiva`. No es peso real (Spec D registrará pesajes); es proyección. | Mismo cálculo del Excel. |
| 5 | KPIs | Cuatro: **Lotes activos**, **Inventario en corrales**, **Salen esta semana** (cabezas con `semana_proyectada_venta == semana_actual`), **Corrales libres**. | Espejo del dummy v4. |
| 6 | Filtros HTMX | tipo_ganado · etapa · ver_libres (boolean). | UX del dummy + simplicidad. |
| 7 | Export | CSV con todas las columnas. Botón "📥 Exportar" en la página. | Útil para Excel/correo. |
| 8 | Permisos | Cualquier rol autenticado (`view_lote`) puede acceder. No hay nuevos permisos. | No hay datos sensibles distintos. |

---

## Decisiones pendientes — necesitan validación con Chamizal

### C1. Días por etapa: del programa o globales

El programa tiene `dias_recepcion`, `dias_f1`, `dias_transicion`, `dias_f3`, `dias_zilpaterol`. Recomendación: usar esos valores **para cada lote según su programa resuelto**.

Alternativa: días globales por sexo (sin programa). Más simple pero menos preciso.

**Recomendación: usar los del programa** (ya está modelado y los datos están).

### C2. ¿"Semana actual" se refiere a semana ISO o semana del año del Excel?

Recomendación: ISO week number (lo que hace `date.isocalendar()`). El Excel del cliente parece usar lo mismo (columna SEMANA = 18 corresponde con ISO de la fecha 2026-04-28).

### C3. Inventario actual del lote

Por ahora `Lote.cabezas_iniciales` es lo que se muestra. Spec D introducirá muertes/ventas parciales que ajusten un `cabezas_actuales` derivado. Mientras: usar `cabezas_iniciales`.

**Recomendación: usar `cabezas_iniciales` para "Inventario" en Spec C**. Si el cliente quiere ya un campo manual editable de inventario actual, se agrega ahora; si no, esperamos a Spec D.

### C4. ¿Reemplazar la home con redirect, o dejar dashboard placeholder?

- **(a)** `/` redirige a `/disponibilidad/`. Quien entra al sistema cae directo en la pantalla operativa.
- **(b)** `/` queda con el placeholder "Bienvenido a SiCoGa", y el sidebar tiene "Disponibilidad" como entrada nueva.

**Recomendación: (a)**. La pantalla de bienvenida no aporta nada y los operadores irían a `/disponibilidad/` siempre.

---

## Modelo de datos

### Nuevas properties en `Lote`

Sin nuevas tablas. Sólo agregar al modelo existente:

```python
@property
def dias_transcurridos(self):
    from datetime import date
    return (date.today() - self.fecha_inicio).days

@property
def peso_actual_proyectado(self):
    """peso_inicial + dias_trans × gdp."""
    if not self.gdp_efectiva:
        return None
    return self.peso_inicial_promedio + (self.dias_transcurridos * self.gdp_efectiva)

@property
def etapa(self):
    """Recepción / F1 / Transición / F3 / Zilpaterol / Post-Zilpaterol / Sin programa."""
    p = self.programa
    if not p:
        return "Sin programa"
    d = self.dias_transcurridos
    acum = 0
    if d < (acum := acum + p.dias_recepcion):
        return "Recepción"
    if d < (acum := acum + p.dias_f1):
        return "F1"
    if d < (acum := acum + p.dias_transicion):
        return "Transición"
    if d < (acum := acum + p.dias_f3):
        return "F3"
    if d < (acum := acum + p.dias_zilpaterol):
        return "Zilpaterol"
    return "Post-Zilpaterol"

@property
def peso_estimado_rango(self):
    """Peso al cumplir 60 días = peso_inicial + 60 × gdp_efectiva.

    Nombre histórico del Excel — es 'cuánto debería pesar al primer reimplante'."""
    if not self.gdp_efectiva:
        return None
    return self.peso_inicial_promedio + (60 * self.gdp_efectiva)
```

---

## Vistas y URLs

### `apps/disponibilidad/`

App nueva (delgada — sólo views, no models). Estructura:

```
apps/disponibilidad/
├── __init__.py
├── apps.py
├── urls.py
├── views.py
├── tests/
└── templates/disponibilidad/
    ├── home.html
    ├── _tabla.html       # partial para HTMX
    └── export.csv        # template para CSV
```

### URLs

```python
urlpatterns = [
    path("", views.DisponibilidadView.as_view(), name="home"),
    path("export.csv", views.ExportCsvView.as_view(), name="export_csv"),
]
```

Montaje: `path("disponibilidad/", include("apps.disponibilidad.urls", namespace="disponibilidad"))`.

Adicionalmente: `config/urls.py` cambia `/` para redirigir a `/disponibilidad/`.

### `DisponibilidadView`

```python
class DisponibilidadView(LoginRequiredMixin, TemplateView):
    template_name = "disponibilidad/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Aplicar filtros desde request.GET
        filtros = {
            "tipo_ganado": self.request.GET.get("tipo_ganado") or "",
            "etapa": self.request.GET.get("etapa") or "",
            "ver_libres": self.request.GET.get("ver_libres") == "1",
        }

        # Construir filas: 1 por corral activo, con lote activo si lo hay
        corrales = (
            Corral.objects.filter(activo=True)
            .prefetch_related(Prefetch("lotes", queryset=Lote.objects.filter(activo=True)))
            .order_by("clave")
        )
        filas = []
        for c in corrales:
            lote = c.lotes.first()  # 0 o 1
            if filtros["tipo_ganado"] and (not lote or str(lote.tipo_ganado_id) != filtros["tipo_ganado"]):
                continue
            if filtros["etapa"] and (not lote or lote.etapa != filtros["etapa"]):
                continue
            if not filtros["ver_libres"] and not lote:
                continue
            filas.append({"corral": c, "lote": lote})

        # KPIs
        from datetime import date
        sem_actual = date.today().isocalendar()[1]
        ctx["kpi_lotes_activos"] = Lote.objects.filter(activo=True).count()
        ctx["kpi_inventario"] = sum(l.cabezas_iniciales for l in Lote.objects.filter(activo=True))
        ctx["kpi_salen_semana"] = sum(
            l.cabezas_iniciales for l in Lote.objects.filter(activo=True)
            if l.semana_proyectada_venta == sem_actual
        )
        ctx["kpi_corrales_libres"] = sum(1 for f in filas if not f["lote"]) if filtros["ver_libres"] else (
            Corral.objects.filter(activo=True).count() - Lote.objects.filter(activo=True).count()
        )

        ctx["filas"] = filas
        ctx["filtros"] = filtros
        ctx["tipos_ganado"] = TipoGanado.objects.filter(activo=True)
        ctx["etapas"] = ["Recepción", "F1", "Transición", "F3", "Zilpaterol", "Post-Zilpaterol", "Sin programa"]
        return ctx
```

### `ExportCsvView`

Genera `disponibilidad-YYYY-MM-DD.csv` con todas las columnas de la tabla (sin filtros, exporta el universo completo).

---

## Templates

`disponibilidad/home.html` — extiende `base.html`, contiene 4 KPIs arriba, form de filtros HTMX, y `{% include "disponibilidad/_tabla.html" %}`.

`disponibilidad/_tabla.html` — el `<div id="tabla-disp">` con la tabla. Recibe `filas` y `filtros` desde el contexto. HTMX swap target.

Columnas de la tabla (mirroring del Excel):

| Corral | Lote | Sexo | Origen | Inv. | F. Inicio | Peso Ini. | D. Trans. | D. Eng. Proy. | Peso Act. Proy. | GDP | Peso Salida | Peso Est. Rango | F. 1er Reimp. | Etapa | Sem. Venta | Acciones |

Si la fila es "Libre" (lote=None), todas las columnas operativas muestran "—" y la columna acciones ofrece "+ Alta de lote" enlazando a `/lotes/nuevo/` con `?corral=X` prellenado.

---

## Sidebar

Reemplazar la entrada "Próximamente: Disponibilidad" con la real:

```html
<a class="ni {% if 'disponibilidad' in request.path %}active{% endif %}" href="/disponibilidad/">
  <span class="ico">📊</span> Disponibilidad
</a>
```

(Movemos esta entrada arriba de "Catálogos" o lo que el cliente prefiera; recomendación: justo debajo de "Inicio" / Dashboard.)

---

## Criterios de aceptación

| # | Criterio | Verificación |
|---|---|---|
| 1 | `/` redirige a `/disponibilidad/`. | Test integration. |
| 2 | `/disponibilidad/` muestra 4 KPIs con valores correctos contra fixture. | Test view. |
| 3 | La tabla lista todos los corrales activos con su lote activo o "Libre". | Test view + fixture. |
| 4 | Filtro por tipo_ganado actualiza la tabla vía HTMX sin recargar header/sidebar. | Test (con `hx-select`). |
| 5 | `Lote.dias_transcurridos` calcula correctamente desde `fecha_inicio`. | Test calculo. |
| 6 | `Lote.etapa` resuelve correctamente las 6 etapas + "Sin programa". | Test parametrizado. |
| 7 | `Lote.peso_actual_proyectado` = peso_ini + dias × gdp. | Test. |
| 8 | Export CSV devuelve content-type `text/csv` y filas con encabezado. | Test view. |
| 9 | Anónimo es redirigido a login. | Test. |
| 10 | Cobertura ≥ 85% en `apps.disponibilidad`. | `pytest --cov=apps.disponibilidad`. |

---

## Plan de implementación tentativo

Estimado **13-15 tasks** en 5 fases:

1. **Properties nuevas** (3 tasks): dias_transcurridos, peso_actual_proyectado, etapa, peso_estimado_rango.
2. **App + view base** (3 tasks): bootstrap `apps/disponibilidad`, DisponibilidadView, template con KPIs + tabla.
3. **Filtros HTMX** (2 tasks): form con tipo_ganado/etapa/ver_libres + select target con hx-select.
4. **Export CSV** (2 tasks): ExportCsvView + test.
5. **Cierre** (3 tasks): redirect / → /disponibilidad/, sidebar, smoke + docs + push.

---

## Fuera del alcance

- Mapa visual de corrales (Spec F).
- Salidas proyectadas como gráfica de barras (Spec F).
- Indicadores GDP real, conversión, mortalidad (Spec D).
- Inventario potreros (no cuelga de Lote en Spec B; entra en Spec D).
- Edición inline desde la tabla (Spec D — operación).

---

## Próximos pasos

1. Validar decisiones C1–C4 con Chamizal.
2. Generar plan TDD bite-sized (similar a Spec B).
3. Ejecutar fase por fase.
