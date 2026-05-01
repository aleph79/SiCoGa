# Release 2026-05-01 — Specs B, C, D, E, F

> Instrucciones para subir a producción los cambios desde el último deploy (que tenía sólo Spec A — Cimientos).

## Qué incluye este release

| Spec | Funcionalidad |
|---|---|
| **B — Lotes y Formación** | Modelo `Lote`, CRUD, HTMX preview de proyección, fusión de lotes |
| **C — Disponibilidad** | Pantalla principal `/disponibilidad/` con KPIs, tabla por corral, filtros HTMX, export CSV |
| **D.1 — Reimplantes** | Catálogo Implantes (seedeado del Excel) + modelo Reimplante + calendario |
| **D.2 — Transiciones y Zilpaterol** | Calendarios y captura de transiciones de fórmula y entrada a Zilpaterol |
| **D.3 — Pesajes** | Pesajes reales que corrigen automáticamente la proyección de peso actual |
| **D.4 — Reportes** | Inventario General, Proyección Anual, Salidas semanales |
| **E.1 — Muertes y Ventas** | Mortalidad y ventas reales con `Lote.cabezas_actuales` derivado |
| **E.2 — Compra/Recepción** | Datos de origen, merma de tránsito, costo por cabeza/kg |
| **E.3 — Alimentación y Medicación** | Catálogos Formula y Medicamento + registro con cálculo de costos |
| **E.4 — Costo Hotel** | Componentes configurables + cálculo de días-animal-netos |
| **E.5 — Cierre consolidado** | Pantalla `/cierre/lotes/<pk>/cierre/` con KPIs financieros y export CSV |
| **F — Dashboard ejecutivo** | `/dashboard/` con KPIs gerenciales, mapa de corrales, salidas proyectadas y timeline |

**234 tests** pasando. Cobertura ≥85% en cada app.

---

## 🚀 Comando único para deploy

En el server `dedi-1544783.siweb-ia.com`, como **root**:

```bash
sudo bash /home/sicoga/sicoga/scripts/update.sh
```

Ese script hace:
- `git pull origin main` (como usuario `sicoga`)
- `pip install -r requirements/prod.txt`
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`
- `systemctl restart sicoga`
- Smoke HTTP a `https://sicoga.com/`

---

## Si prefieres manual (paso a paso)

```bash
# 1. Cambiar a usuario sicoga
su - sicoga
cd /home/sicoga/sicoga
source /home/sicoga/venv_sicoga/bin/activate

# 2. Bajar los cambios
git pull origin main

# 3. Instalar dependencias (no hay nuevas, pero por seguridad)
pip install -r requirements/prod.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Recolectar estáticos
python manage.py collectstatic --noinput

# 6. Salir y reiniciar el servicio como root
exit
sudo systemctl restart sicoga

# 7. Verificar
sudo journalctl -u sicoga -n 30 --no-pager
curl -kI https://sicoga.com/
curl -kI https://sicoga.com/dashboard/
```

---

## Migraciones que se aplicarán

```
accounts.0003 → 0009    (permisos Capturista para nuevos modelos)
catalogos.0011 → 0015   (Implante + seed, Formula + seed, Potrero, Medicamento)
lotes.0001 → 0003       (Lote, LoteFusion, campos de compra)
operacion.0001 → 0003   (Reimplante, Transicion, EntradaZilpaterol, Pesaje)
cierre.0001 → 0004      (Muerte, Venta, Alimentacion, Medicacion, CostoHotelComponente)
```

---

## Datos seedeados automáticamente

- **8 Implantes** del Excel del programa de reimplantes:
  REV. G · 60 DIAS REV. IMPX · 60 DIAS REV. H · 60 DIAS REV. H + XR · REV. H · REV. H + XR · REV. H Y XR · REV. IMPLEMAX
- **5 Fórmulas**: F1 sin melaza · F1 con melaza · Transición F1/F3 · F3 SSS · F3 SZ + Zilpaterol
- **TipoCorral "Potrero"** (para inventario en pastoreo)
- **4 Componentes Costo Hotel**:
  - Agua y sanidad — $4.20/d-a (habilitado)
  - Mano de obra operativa — $5.80/d-a (habilitado)
  - Depreciación instalaciones — $2.10/d-a (deshabilitado)
  - Costos administrativos — $1.40/d-a (deshabilitado)

Todos editables desde `/admin/` cuando Chamizal valide.

---

## Smoke test post-deploy (en navegador)

Login con cuenta admin y verifica:

- [ ] `/disponibilidad/` (home) carga con KPIs y tabla por corral
- [ ] `/lotes/nuevo/` muestra HTMX preview de proyección en vivo al capturar
- [ ] `/operacion/reimplantes/` · `/operacion/transiciones/` · `/operacion/zilpaterol/` · `/operacion/pesajes/`
- [ ] `/operacion/inventario/` · `/operacion/proyeccion-anual/` · `/operacion/salidas-semanales/`
- [ ] `/cierre/muertes/` · `/cierre/ventas/` · `/cierre/alimentaciones/` · `/cierre/medicaciones/` · `/cierre/costo-hotel/`
- [ ] `/dashboard/` muestra mapa de corrales + KPIs + timeline de actividad
- [ ] En detalle de un lote: botones **🛒 Compra/Recepción** · **🏨 Costo Hotel** · **📊 Cierre del lote**
- [ ] Sidebar reorganizado con secciones Operación · Cierre · Gerencial

---

## Lo que NO cambia en este release

- `.env` — sin variables nuevas
- `requirements/` — sin dependencias nuevas
- nginx / Apache / `.htaccess` — sin cambios de configuración
- Certificados SSL — intactos

---

## Si algo falla

### Diagnóstico

```bash
# Logs de gunicorn vía systemd
sudo journalctl -u sicoga -n 50 --no-pager

# Log de errores de gunicorn
sudo tail -f /home/sicoga/logs/gunicorn-error.log

# Log de Django (errores 500)
sudo tail -f /home/sicoga/sicoga/logs/sicoga.log

# Estado del servicio
sudo systemctl status sicoga
```

### Rollback

```bash
# Volver al commit anterior (Spec A solo)
sudo -u sicoga git -C /home/sicoga/sicoga reset --hard <sha-anterior>

# Si quieres revertir migraciones (poco común, sólo si hay problema con datos):
sudo -u sicoga /home/sicoga/venv_sicoga/bin/python /home/sicoga/sicoga/manage.py migrate cierre zero
sudo -u sicoga /home/sicoga/venv_sicoga/bin/python /home/sicoga/sicoga/manage.py migrate operacion zero
sudo -u sicoga /home/sicoga/venv_sicoga/bin/python /home/sicoga/sicoga/manage.py migrate lotes zero
# (catalogos y accounts se quedan como están — son catálogos compatibles hacia atrás)

sudo systemctl restart sicoga
```

---

## Después del deploy

1. **Crear usuarios Capturista de prueba** desde `/admin/` para que Chamizal pruebe.
2. **Validar el smoke checklist** con un usuario Chamizal real.
3. **Editar costos seedeados** según sus precios reales (fórmulas, costo hotel).
4. **Capturar 1-2 lotes de prueba** para verificar el flujo completo: alta → reimplantes → ventas → cierre consolidado.

---

## Próximos pasos (post-validación)

- **Spec G — CATLE**: requiere discovery con Chamizal (ver `docs/superpowers/specs/2026-05-01-sicoga-spec-g-catle-design.md`). Ideal: que traigan un export real de CATLE para diseñar el parser.

Mientras tanto, el sistema queda **operacionalmente completo** sin Spec G.
