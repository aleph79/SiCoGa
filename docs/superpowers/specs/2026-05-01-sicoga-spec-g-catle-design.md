# SiCoGa — Spec G: Integración CATLE (Diseño)

**Fecha:** 2026-05-01
**Estado:** 🚧 **DRAFT — DISCOVERY pendiente con Chamizal**
**Cliente:** Chamizal Camperos
**Spec previo:** [F — Dashboard ejecutivo](./2026-05-01-sicoga-spec-f-dashboard-design.md) ✅ entregado

> Este spec es **diferente** a los anteriores: no se puede ejecutar sin información técnica del sistema externo CATLE que sólo Chamizal tiene. Aquí documentamos qué sabemos, qué no sabemos, y las preguntas que cierran el alcance.

---

## Lo que sabemos

CATLE es un sistema externo que el cliente ya usa. Aparece en el dummy v4 como botón **"📥 Importar CATLE"** en la pantalla de Alimentación (Spec E.3). En la propuesta original (Folio 321), Spec G se describe como *"integración o importación"* — la decisión entre las dos formas es parte del discovery.

**Inferencias razonables**:

- Probablemente CATLE registra **consumo de alimento** (kg por fórmula, por corral, por día). Su salida natural mapea al modelo `Alimentacion` que ya tenemos en SiCoGa.
- Puede o no incluir: pesajes, medicación, mortalidad. Hay que confirmar.
- Es probable que sea on-premise (instalado en Chamizal) y no en la nube — esto define si la integración puede ser API en vivo o requiere export/import.

---

## Preguntas que necesitan respuesta antes de implementar

### G1. ¿Qué interfaces de salida ofrece CATLE?

- **(a) Export manual a Excel/CSV**: el operador descarga del CATLE y sube a SiCoGa.
- **(b) Archivo en carpeta compartida**: CATLE escribe diariamente a `\\server\catle\export.csv` y SiCoGa lee de ahí.
- **(c) API REST/SOAP**: SiCoGa hace `GET` a una URL de CATLE.
- **(d) Acceso directo a su base de datos**: SiCoGa lee tablas de SQL Server / PostgreSQL / etc.
- **(e) Webhook**: CATLE empuja a SiCoGa cuando hay datos nuevos.

**Por qué importa**: cada opción tiene complejidad y mantenibilidad muy distintas. (a) es el menos riesgoso; (e) el más automatizado pero requiere cambios en CATLE.

### G2. ¿Qué datos se sincronizan?

Lista candidatos (marca lo que aplica):

- [ ] Consumo de alimento (lote, fórmula, fecha, kg)
- [ ] Pesajes (lote, fecha, peso promedio)
- [ ] Medicación
- [ ] Mortalidad
- [ ] Inventario de almacén de alimento (no modelado todavía en SiCoGa)
- [ ] Costos de fórmula

### G3. ¿Frecuencia y volumen?

- **Diario / semanal / a demanda?**
- **¿Cuántas filas/día aproximadamente?** (define si necesitamos paginación o batching).
- **¿Datos del histórico inicial?** (al activar la integración, ¿cargamos los últimos 6 meses, 1 año, todo?).

### G4. ¿Sentido del flujo?

- **Solo lectura**: SiCoGa importa de CATLE pero no le manda nada. Más simple.
- **Bidireccional**: SiCoGa también envía datos (ej. un lote nuevo creado aquí se replica en CATLE). Más complejo, requiere endpoints en ambos lados.

**Recomendación inicial**: solo lectura en Spec G. Si Chamizal eventualmente quiere bidireccional, lo evaluamos en otro spec.

### G5. ¿Cómo se identifican los lotes en CATLE?

CATLE probablemente usa su propio identificador interno. SiCoGa usa el `Folio` (texto libre). ¿Coinciden? ¿Necesitamos un campo `lote.codigo_catle` para mapear?

### G6. ¿Resolución de conflictos?

Si SiCoGa registra una `Alimentacion` manual y luego llega de CATLE el mismo periodo:

- **(a)** CATLE siempre gana (sobrescribe).
- **(b)** SiCoGa siempre gana (descarta CATLE).
- **(c)** Se duplican y operador resuelve.
- **(d)** Tag de origen en cada registro (`origen='manual'` vs `origen='catle'`) y mostrar ambos.

**Recomendación**: (d) con el campo `origen`, así nada se pierde y el operador decide en pantalla.

### G7. ¿Quién mantiene la integración?

- ¿Chamizal tiene acceso al equipo técnico de CATLE para coordinar cambios?
- Si CATLE actualiza su esquema/API, ¿quién avisa?

---

## Alternativas de arquitectura (según G1)

### Opción A — Import manual de CSV/Excel (más simple)

- Pantalla `/integracion/catle/import/` con botón de subir archivo.
- Vista parsea el CSV y crea `Alimentacion` por cada fila.
- Pre-validación: muestra qué se va a crear antes de confirmar.
- Auditoría: cada registro queda con `origen='catle'` y referencia al archivo.

**Costo estimado**: ~5 tasks (1-2 días).

### Opción B — Pull desde archivo compartido

- Comando management (`python manage.py importar_catle`) que lee de un path configurable y crea registros.
- Cron/systemd lo corre cada N horas.
- Igual que A pero sin UI, automático.

**Costo estimado**: ~6 tasks (2 días). Necesita coordinar acceso al servidor.

### Opción C — Pull vía API

- SiCoGa hace requests HTTP a CATLE (auth si requiere).
- Job programado (Celery o cron) trae datos nuevos por delta de fecha.
- Mapeo CATLE → SiCoGa por adaptador.

**Costo estimado**: ~10-15 tasks (1 semana). Requiere doc de la API de CATLE.

### Opción D — Lectura directa de BD

- SiCoGa abre conexión a la BD de CATLE en modo lectura.
- Vistas de SiCoGa pueden hacer `JOIN` con datos vivos sin sincronización.

**Costo estimado**: ~8 tasks. Requiere acceso de red + credenciales + acuerdo de no-modificar.

### Opción E — Webhook/push

- CATLE llama a un endpoint en SiCoGa cuando tiene datos nuevos.
- Más eficiente pero requiere cambios en CATLE.

**Costo estimado**: ~10 tasks + trabajo en CATLE (responsabilidad del proveedor de CATLE).

---

## Recomendación

**Empezar con Opción A** (import manual de Excel/CSV). Razones:

1. Es lo que el dummy v4 implícitamente sugiere ("📥 Importar CATLE").
2. Sin riesgo de dependencia operativa con CATLE en producción.
3. Si CATLE cambia, sólo se ajusta el parser — no el sistema entero.
4. Permite que Chamizal pruebe la integración sin pedirle nada al proveedor de CATLE.
5. Si después se quiere automatizar, Opción A se vuelve la base sobre la que se monta B/C.

**Estimación si vamos con A**: ~5 tasks · 1-2 días de trabajo.

---

## Modelo de datos tentativo

Sin tablas nuevas. Sólo extender `Alimentacion`:

```python
class Alimentacion(AuditableModel):
    # ... campos existentes ...
    origen = models.CharField(
        max_length=10,
        choices=[("manual", "Manual"), ("catle", "CATLE")],
        default="manual",
    )
    catle_ref = models.CharField(
        max_length=80,
        blank=True,
        help_text="Identificador del registro en CATLE (para idempotencia).",
    )
```

Y un nuevo modelo `ImportacionCatle` para auditar cada import:

```python
class ImportacionCatle(TimeStampedModel):
    archivo_nombre = models.CharField(max_length=200)
    filas_creadas = models.PositiveIntegerField(default=0)
    filas_omitidas = models.PositiveIntegerField(default=0, help_text="Duplicados.")
    filas_error = models.PositiveIntegerField(default=0)
    log = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
```

---

## Plan tentativo (si Opción A confirmada)

1. **Migration** para `Alimentacion.origen` + `Alimentacion.catle_ref`.
2. **Modelo `ImportacionCatle`** + admin.
3. **Parser**: módulo `apps.cierre.services.catle_importer` que lee un Excel/CSV y devuelve dict de cambios pendientes.
4. **Vista `/integracion/catle/import/`** con upload y vista previa.
5. **Vista de confirmación** que ejecuta el import dentro de `transaction.atomic()`.
6. **Tests** con un CSV de ejemplo.

---

## Próximos pasos

1. **Sesión con Chamizal** sobre las 7 preguntas (G1-G7).
2. Idealmente, traer **un export real de CATLE** (Excel, CSV, dump SQL — lo que tengan) para diseñar el parser sobre datos reales.
3. Confirmar Opción A (recomendada) u otra.
4. Generar plan TDD detallado y ejecutar.

**Si no hay info disponible**, Spec G se queda como "diferido" y el sistema queda funcional sin él — Chamizal puede usar Alimentación con captura manual mientras tanto.
