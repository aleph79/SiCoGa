# CLAUDE.md — Contexto de handoff para Claude Code

> Este archivo lo lee Claude Code automáticamente al inicio de cada sesión en este repo. Resume el estado del proyecto y dónde retomar el trabajo.

## Qué es SiCoGa

**Sistema Integral de Gestión Ganadera** desarrollado por SIWEB para Chamizal Camperos. Reemplaza Excels manuales por un sistema web Django+MySQL con dos módulos principales (Disponibilidad y Cierre de Lotes), dashboard gerencial y posible integración con CATLE. Propuesta Folio 321 firmada el 2026-04-23.

## Stack y entorno

- **Python 3.12** · **Django 5.1** · **MySQL 8.0.46** · **mysqlclient**
- **Frontend**: Django templates server-side + HTMX 1.9 + Alpine.js 3 + CSS portado del dummy v4 (dark mode)
- **Auditoría**: `django-simple-history` desde el día 1 en todos los catálogos
- **Testing**: pytest + pytest-django + factory-boy + coverage (objetivo ≥85%)
- **Lint**: black + isort + flake8 + pre-commit hooks
- **CI**: GitHub Actions con MySQL 8.0 service

### MySQL local (mac de Zeus)

```
DATABASE_URL=mysql://root:solsticio@127.0.0.1:3306/sicoga_dev
```

Bases ya creadas: `sicoga_dev` y `sicoga_test` (utf8mb4_unicode_ci). Si vas a otra máquina:
1. Crea las dos BDs.
2. Ajusta `.env` (no committed) con tus credenciales locales.

### Setup en otra máquina

```bash
git clone git@github.com:aleph79/SiCoGa.git
cd SiCoGa
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
pre-commit install
cp .env.example .env
# Editar DATABASE_URL en .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Estado actual del proyecto

**Spec A — Cimientos** está al 70% (23 de 33 tasks completadas). 53 tests pasan. Working tree limpio.

| Phase | Estado | Tasks |
|---|---|---|
| 1. Foundation | ✅ | 1–7 |
| 2. Core | ✅ | 8 |
| 3. Accounts | ✅ | 9–13 |
| 4. Templates | ✅ | 14–17 |
| 5. Catálogos simples | ✅ | 18–23 (TipoCorral, TipoGanado, TipoOrigen, Proveedor, Corral) |
| **6. ProgramaReimplante** | ⏸ | **24–27 ← retomar aquí** |
| 7. Precargas | ⏸ | 28–31 |
| 8. Polish | ⏸ | 32–33 |

## Documentación clave

- **Spec A**: `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md` — diseño aprobado por el cliente (modelos, URLs, criterios de aceptación, decisiones).
- **Plan**: `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md` — 33 tasks TDD bite-sized con código completo. Las tareas 24–33 están listas para ejecutar.
- **Memory snapshot**: `docs/superpowers/memory/` — copia de la auto-memory de Claude (project + user). Si en la otra máquina la auto-memory está vacía, usa estos archivos como referencia o cópialos a `~/.claude/projects/<sanitized-cwd>/memory/`.

## Decisiones de diseño (ya tomadas, no re-discutir)

1. **Hospital fuera del alcance** — la pantalla del dummy v4 NO entra al sistema.
2. **Single-tenant** — sólo Chamizal. No FK a `Rancho`.
3. **Folio del lote 100% editable manual** — `TipoGanado` no tiene campo de sufijo. (Aplica en Spec B.)
4. **Implantes texto libre** en `ProgramaReimplante` — el catálogo dedicado entra en Spec D.
5. **`tipo_origen` nullable** en `ProgramaReimplante` (comodín para vacas).
6. **Borrado lógico** (`activo=False`) en todos los catálogos del Spec A.
7. **4 roles**: Administrador, Gerente, Capturista, Solo Lectura. Capturista en Spec A sólo tiene `view_*`; los `add/change` operativos llegan en Specs B–D.
8. **Auditoría con `django-simple-history`** desde el día 1.

## Convenciones del repo

- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `docs:`, `ci:`).
- **Branch principal**: `main`. PRs si trabajas en features grandes.
- **Pre-commit hooks corren en cada commit**: black + isort + flake8 + checks básicos. Si un hook autoformatea, re-stage y vuelve a commitear.
- **Estructura de apps**: `apps/core/` (modelos abstractos), `apps/accounts/` (auth), `apps/catalogos/` (catálogos). Phase 6+ extenderán catalogos.
- **conftest.py** vive en la **raíz** del proyecto (no en `tests/`) para que la fixture autouse `db` cubra `tests/` y `apps/*/tests/`.
- **Tests con `force_login` o `IntegrityError`** usan `@pytest.mark.django_db(transaction=True)` por compatibilidad con MySQL InnoDB savepoints.

## Adaptaciones al plan original (importante saber al continuar)

- `Pillow` está en `requirements/base.txt` (no en el plan original; necesario para `ImageField`).
- `whitenoise` está en `base.txt` (no `prod.txt`) porque `base.py` lo importa siempre.
- `apps/accounts/apps.py` tiene `_sync_group_permissions` post_migrate que sincroniza Administrador (todos los perms) **y Solo Lectura (view_*)** después de cada migrate.
- `apps/core/mixins.py` `CatalogoMixin` redirige anonymous → login (302), 403 sólo para autenticados sin permiso.
- `config/urls.py` tiene un include condicional de `debug_toolbar` cuando `DEBUG=True`.

## Cómo retomar

Cuando arranques una nueva sesión de Claude Code aquí:

1. Lee este `CLAUDE.md` (auto-cargado).
2. Lee el spec y el plan en `docs/superpowers/`.
3. Verifica el estado: `git log --oneline -5`, `pytest -q`, `python manage.py check`.
4. Continúa con **Task 24 — ProgramaReimplante model with resolver** (TDD). El plan tiene el código completo, sólo hay que dispatch del implementer subagent.
5. Mantén el ritmo: pausa al final de cada Phase para review humano. Phase 6 son 4 tasks (24–27).

## Tareas pendientes (Phase 6 → 8)

Ver detalles en `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`:

- **Phase 6** (Tasks 24–27): ProgramaReimplante model + `resolver()`, form con validación de traslapes, CRUD con filtro HTMX por `tipo_ganado`/`tipo_origen`, tests de permisos.
- **Phase 7** (Tasks 28–31): seed `TipoCorral`/`TipoGanado`/`TipoOrigen`, Excel loader (`apps/catalogos/seeds/programa_excel.py`), data migration que carga `docs/DISPONIBILIDAD 2026 1.xlsx`, test de permisos Capturista.
- **Phase 8** (Tasks 32–33): subir cobertura a ≥85%, README final, smoke checklist, push.
