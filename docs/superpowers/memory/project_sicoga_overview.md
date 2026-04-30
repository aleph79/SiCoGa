---
name: SiCoGa - Visión y decisiones de proyecto
description: Cliente, alcance, repo, stack, decisiones y progreso del Spec A de SiCoGa (Sistema Integral de Gestión Ganadera)
type: project
originSessionId: c6a293b1-5224-4046-8975-1bbc90d80f1c
---
**SiCoGa = Sistema Integral de Gestión Ganadera** desarrollado por SIWEB para **Chamizal Camperos**.

- Repo: `https://github.com/aleph79/SiCoGa` (sincronizado, branch `main`)
- Stack: Python 3.12 + Django 5.1 + MySQL 8.0.46 + mysqlclient
- Frontend: Django templates + HTMX + Alpine.js (CSS portado del dummy v4)
- Working dir local (mac de Zeus): `/Users/zeus/Documents/Fuentes/Django/SiCoGa`
- Costo: $67,585 MXN + IVA, 6–8 semanas, 6 fases (40/30/30 de pago)
- Propuesta firmada el 23 de abril de 2026; documento Folio 321

**MySQL local:**
- `DATABASE_URL=mysql://root:solsticio@127.0.0.1:3306/sicoga_dev`
- BDs `sicoga_dev` y `sicoga_test` con utf8mb4_unicode_ci
- En CI usa root/root con MySQL 8.0 service de GitHub Actions

**Decisiones tomadas:**
1. Pantalla "hospital" del dummy v4 está FUERA del alcance — descartada.
2. Proyecto descompuesto en 7 specs incrementales: A=Cimientos, B=Lotes/Formación, C=Disponibilidad, D=Submódulos operativos, E=Cierre, F=Dashboard, G=CATLE.
3. Spec A aprobado el 2026-04-29 y plan de 33 tasks generado. Ejecución vía superpowers:subagent-driven-development.
4. Folio del lote será 100% editable manual; `TipoGanado` no carga sufijo. Aplica en Spec B.
5. `ProgramaReimplante` usa `tipo_origen` nullable como comodín para vacas (no distinguen corral vs potrero).
6. `simple_history` desde el día 1 en todos los catálogos (auditoría automática).
7. Borrado lógico (`activo=False`) en todos los catálogos del Spec A.

**Progreso del Spec A (al 2026-04-29):**

23 de 33 tasks completadas, **53 tests pasando**, working tree limpio, push a GitHub al día.

| Phase | Estado | Tasks |
|---|---|---|
| 1 — Foundation | ✅ | 1–7 (init, deps, Django, MySQL, pytest, lint, CI) |
| 2 — Core | ✅ | 8 (TimeStampedModel, AuditableModel, CatalogoMixin) |
| 3 — Accounts | ✅ | 9–13 (User, signal, login views, 4 grupos) |
| 4 — Templates | ✅ | 14–17 (CSS, base.html, errors, dashboard) |
| 5 — Catálogos simples | ✅ | 18–23 (TipoCorral, TipoGanado, TipoOrigen, Proveedor, Corral) |
| 6 — ProgramaReimplante | ⏸ | 24–27 (modelo + resolver + form + CRUD HTMX) |
| 7 — Precargas | ⏸ | 28–31 (seed tipos + Excel loader + capturista perms) |
| 8 — Polish | ⏸ | 32–33 (cobertura ≥85% + README + push final) |

**Adaptaciones notables al plan original:**
- `Pillow` añadido a `requirements/base.txt` (necesario para `ImageField` del avatar).
- `conftest.py` movido a la raíz del proyecto (no `tests/`) para que `apps/*/tests/` hereden la fixture autouse de `db`.
- Tests con `force_login` o `IntegrityError` usan `@pytest.mark.django_db(transaction=True)` por compatibilidad con MySQL InnoDB savepoints.
- `apps/accounts/apps.py` tiene `_sync_group_permissions` post_migrate que sincroniza `Administrador` (todos los perms) y `Solo Lectura` (`view_*`).
- `apps/core/mixins.py` `CatalogoMixin` redirige anonymous → login (302), 403 sólo para autenticados sin permiso.
- `whitenoise` en `requirements/base.txt` (no `prod.txt`) porque `base.py` lo importa siempre.
- `debug_toolbar` URL include condicional añadido a `config/urls.py`.

**Why:** Mantener histórico vivo del proyecto para que Claude pueda continuar desde otra máquina con contexto completo.
**How to apply:** Al retomar, leer este memo + `CLAUDE.md` + `docs/superpowers/specs/2026-04-29-sicoga-spec-a-cimientos-design.md` + `docs/superpowers/plans/2026-04-29-sicoga-spec-a-cimientos-plan.md`. Continuar con Task 24 (ProgramaReimplante model con resolver, TDD).
