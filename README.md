# SiCoGa — Sistema Integral de Gestión Ganadera

Sistema web interno para Chamizal Camperos. Centraliza la operación ganadera reemplazando el control manual en Excel.

## Stack

- Python 3.12 · Django 5.1 · MySQL 8.0
- HTMX 1.9 · Alpine.js 3 · CSS portado del dummy v4 (dark mode)
- pytest · factory-boy · django-simple-history · django-environ
- gunicorn · whitenoise (producción)

## Setup local

### Prerequisitos

- Python 3.12 instalado.
- MySQL 8.0 corriendo localmente con un usuario que pueda crear bases de datos.
- (macOS) `brew install mysql-client pkg-config` para compilar `mysqlclient`.

### Pasos

```bash
git clone git@github.com:aleph79/SiCoGa.git
cd SiCoGa
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
pre-commit install
cp .env.example .env
# Editar .env: ajustar DATABASE_URL al MySQL local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visitar `http://127.0.0.1:8000/`.

### PyCharm

1. Settings → Project → Python Interpreter → Add → Existing → `./venv/bin/python`.
2. Settings → Languages & Frameworks → Django → Enable: project root, settings = `config/settings/dev.py`, manage.py = `manage.py`.

## Comandos comunes (Makefile)

```bash
make help          # lista todos los comandos
make install       # instala deps de dev + pre-commit
make migrate       # aplica migraciones
make run           # runserver en :8000
make test          # pytest
make test-cov      # pytest con reporte HTML en htmlcov/
make lint          # black + isort + flake8 (autoformatea)
make lint-check    # sólo verifica sin modificar
```

## Tests

```bash
pytest                                    # todos
pytest apps/catalogos -v                  # solo una app
pytest --cov=apps --cov-report=html       # con cobertura HTML
open htmlcov/index.html
```

## Estructura

- `config/` — settings split (base/dev/prod), URLs, WSGI/ASGI.
- `apps/core/` — modelos abstractos y mixins compartidos.
- `apps/accounts/` — autenticación, usuarios, perfil, roles.
- `apps/catalogos/` — catálogos del sistema (Tipos, Corral, Proveedor, Programa de Reimplantes).
- `apps/lotes/` — Lotes (entrada y formación) y operación de Fusión.
- `apps/disponibilidad/` — pantalla operativa principal con KPIs, tabla por corral, filtros HTMX y export CSV.
- `apps/operacion/` — eventos operativos durante la vida del lote (D.1: Reimplantes; D.2-D.4 pendientes).
- `templates/` — templates Django (`base.html`, `partials/`, por app).
- `static/` — CSS y JS.
- `docs/` — propuesta, levantamiento de requerimientos, dummy HTML, Excels base.
- `docs/superpowers/specs/` — specs de diseño por entregable.
- `docs/superpowers/plans/` — planes de implementación.

## Roles del sistema

| Grupo | Permisos en Spec A |
|---|---|
| Administrador | Todos. |
| Gerente | `view_*` en todos los modelos. |
| Capturista | `view_*` en catálogos del Spec A (los `add/change` operativos llegan en Specs B/C/D). |
| Solo Lectura | `view_*` en todos los modelos. |

## Smoke test manual (Spec A)

Tras `python manage.py runserver`, verificar:

- [ ] `/` muestra dashboard placeholder con sidebar.
- [ ] `/accounts/login/` funciona; logout regresa a login.
- [ ] `/accounts/perfil/` accesible y editable.
- [ ] `/catalogos/tipos-corral/` lista 3 tipos seedeados (Recepción, Engorda, Zilpaterol).
- [ ] `/catalogos/tipos-ganado/` lista Macho/Hembra/Vaca.
- [ ] `/catalogos/tipos-origen/` lista Corral/Potrero.
- [ ] `/catalogos/proveedores/` vacío con botón + Nuevo.
- [ ] `/catalogos/corrales/` vacío con botón + Nuevo, dropdown TipoCorral.
- [ ] `/catalogos/programa-reimplantes/` muestra ~49 filas precargadas desde el Excel.
- [ ] Filtro HTMX por TipoGanado y TipoOrigen actualiza la tabla sin recargar.
- [ ] `/admin/` muestra todos los modelos con icono history.
- [ ] Login con usuario Capturista: ve listas pero no botón + Nuevo (403 al forzar la URL).

## Despliegue

Producción se hace en el mismo servidor Linux donde corre MiContaAI (sin Docker). El despliegue se documentará al iniciar la fase de QA.

## Documentación

- Propuesta original: `docs/321. Propuesta y cotización Chamizal Camperos.docx`.
- Toma de requerimientos: `docs/Toma de requerimiento especifico Chamizal primera parte.docx`.
- Spec del entregable actual: `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md`.
- Plan: `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`.
