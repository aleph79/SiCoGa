# SiCoGa — Spec A: Cimientos (Diseño)

**Fecha:** 2026-04-29
**Cliente:** Chamizal Camperos
**Proveedor:** SIWEB (Soluciones Informáticas Web S.A. de C.V.)
**Repositorio:** https://github.com/aleph79/SiCoGa
**Folio de propuesta:** 321

## Contexto

SiCoGa (Sistema Integral de Gestión Ganadera) es un sistema web interno que centraliza la operación ganadera del cliente Chamizal Camperos, sustituyendo controles manuales en Excel. La propuesta total contempla 6 fases con un costo de $67,585 MXN + IVA y duración de 6–8 semanas.

Este documento es el **diseño del primer entregable**, que llamamos **Spec A — Cimientos**. El proyecto se descompone en 7 specs incrementales:

- **A — Cimientos** *(este documento)*: proyecto Django + auth + roles + catálogos base + motor de programa de reimplantes
- **B — Lotes y Formación**: lotes, entrada de jaula, dispersión, histórico de formación
- **C — Disponibilidad y Proyección**: pantalla principal + cálculos
- **D — Submódulos operativos**: reimplantes, transiciones, zilpaterol, salidas semanales, proyección anual, inventario general
- **E — Cierre**: cierre de lotes y todos sus submódulos
- **F — Dashboard**: KPIs y vista gerencial
- **G — CATLE**: integración o importación

Los specs B–G se diseñarán en sesiones independientes; este documento sólo aplica al Spec A.

## Objetivo del Spec A

Dejar el proyecto Django operativo con:

1. Autenticación funcional con cuatro grupos de roles.
2. Seis catálogos del módulo de cimientos accesibles vía web con CRUD completo.
3. Motor del **Programa de Reimplantes** con datos precargados desde el Excel actual.
4. Auditoría automática de cambios en todos los modelos.
5. CI/CD básico, pre-commit y entorno de desarrollo reproducible reconocible por PyCharm.

Al cerrar este spec, el sistema acepta operadores reales capturando catálogos y queda listo para que Spec B introduzca el modelo `Lote`.

## Decisiones tomadas

| # | Decisión | Valor |
|---|---|---|
| 1 | Tenancy | Single-tenant (sólo Chamizal). Sin FK a `Rancho`. |
| 2 | Frontend | Django templates + HTMX 1.9.x + Alpine.js 3.x; CSS del dummy v4 portado a `static/css/sicoga.css`. |
| 3 | Roles | 4 grupos: `Administrador`, `Gerente`, `Capturista`, `Solo Lectura`. |
| 4 | Stack | Python 3.12 · Django 5.1 · MySQL 8.0.46 · `mysqlclient`. |
| 5 | Hosting | Mismo servidor Linux que MiContaAI · gunicorn + nginx · sin Docker. |
| 6 | Dev local | virtualenv tradicional reconocible por PyCharm; sin Docker para desarrollo. |
| 7 | CI | GitHub Actions (flake8 + pytest + coverage). |
| 8 | Hooks | pre-commit con black + isort + flake8 + checks básicos. |
| 9 | Programa de reimplantes | Categoría = `TipoGanado` × `TipoOrigen`; `tipo_origen` nullable como comodín (vacas). Precarga del Excel como data migration. |
| 10 | Auditoría | `django-simple-history` desde el día 1 en todos los catálogos. |
| 11 | Folio del lote | 100% editable manualmente por el operador; `TipoGanado` no carga campo de sufijo. (Aplicará en Spec B.) |
| 12 | Implantes | Texto libre en el programa (`CharField`); el catálogo dedicado de Implantes entrará en Spec D. |
| 13 | Hospital | Fuera del alcance del proyecto. La pantalla del dummy v4 se descarta. |
| 14 | Borrado | Lógico (`activo=False`) en todos los catálogos del Spec A. |
| 15 | Localización | `LANGUAGE_CODE='es-mx'`, `TIME_ZONE='America/Mexico_City'`, `USE_TZ=True`, `USE_I18N=True`. |

## Arquitectura

### Estructura de carpetas

```
SiCoGa/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── .gitignore
├── .env.example
├── pyproject.toml
├── pytest.ini
├── manage.py
├── README.md
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/         (modelos abstractos, mixins)
│   ├── accounts/     (User custom, perfil, roles)
│   └── catalogos/    (los 6 catálogos del Spec A)
├── templates/
│   ├── base.html
│   ├── partials/
│   ├── accounts/
│   └── catalogos/
├── static/
│   ├── css/sicoga.css
│   ├── js/sicoga.js
│   └── img/
├── locale/
└── tests/
```

### Apps y responsabilidades

| App | Responsabilidad | Modelos |
|---|---|---|
| `core` | `TimeStampedModel`, `AuditableModel`, mixins de vistas, helpers comunes. | (sólo abstractos) |
| `accounts` | `User` custom (`AbstractUser` + `email unique` + `telefono`), `Profile`, vistas de login/logout/perfil/cambio de password. | `User`, `Profile` |
| `catalogos` | Catálogos del Spec A. | `TipoCorral`, `TipoGanado`, `TipoOrigen`, `Corral`, `Proveedor`, `ProgramaReimplante` |

### Dependencias

**Producción:**

```
Django==5.1.*
mysqlclient==2.2.*
django-simple-history==3.7.*
django-environ==0.11.*
gunicorn==23.0.*
whitenoise==6.7.*
```

**Desarrollo (`requirements/dev.txt` extiende `base.txt`):**

```
pytest==8.*
pytest-django==4.*
pytest-cov==5.*
factory-boy==3.*
coverage==7.*
black==24.*
isort==5.*
flake8==7.*
pre-commit==3.*
django-debug-toolbar==4.*
ipython
```

## Modelo de datos

### Modelos abstractos (`apps/core/models.py`)

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class AuditableModel(TimeStampedModel):
    """Mezclar con HistoricalRecords() en cada modelo concreto."""
    activo = models.BooleanField(default=True)
    class Meta:
        abstract = True
```

### `accounts` — usuarios y perfil

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)

class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    puesto = models.CharField(max_length=80, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
```

### Grupos (data migration `accounts/migrations/0002_seed_groups.py`)

| Grupo | Permisos clave |
|---|---|
| `Administrador` | Todos los permisos del sistema. |
| `Gerente` | `view_*` en todos los modelos + `change_parametro` (futuro). |
| `Capturista` | `view_*` en catálogos del Spec A. (Permisos `add/change` operativos se añaden en Specs B/C/D cuando aterricen los modelos.) |
| `Solo Lectura` | `view_*` en todos los modelos. |

### `catalogos` — modelos

```python
class TipoCorral(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True)
    history = HistoricalRecords()

class TipoGanado(AuditableModel):
    nombre = models.CharField(max_length=40, unique=True)
    history = HistoricalRecords()

class TipoOrigen(AuditableModel):
    nombre = models.CharField(max_length=20, unique=True)
    history = HistoricalRecords()

class Corral(AuditableModel):
    clave = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=80)
    tipo_corral = models.ForeignKey(TipoCorral, on_delete=models.PROTECT)
    capacidad_maxima = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    history = HistoricalRecords()

    @property
    def ocupacion_actual(self) -> int:
        # Spec A: placeholder. Spec B sustituye por suma de inventarios de lotes activos.
        return 0

    @property
    def disponibilidad(self) -> int:
        return self.capacidad_maxima - self.ocupacion_actual

    class Meta:
        ordering = ['clave']

class Proveedor(AuditableModel):
    nombre = models.CharField(max_length=120, unique=True)
    rfc = models.CharField(max_length=13, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    contacto = models.CharField(max_length=80, blank=True)
    notas = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['nombre']

class ProgramaReimplante(AuditableModel):
    """Motor de cálculo. Una fila por (TipoGanado × TipoOrigen × rango_peso)."""
    tipo_ganado = models.ForeignKey(TipoGanado, on_delete=models.PROTECT)
    tipo_origen = models.ForeignKey(
        TipoOrigen, on_delete=models.PROTECT, null=True, blank=True,
        help_text="Vacío = aplica a cualquier origen (caso vacas).",
    )
    peso_min = models.DecimalField(max_digits=6, decimal_places=2)
    peso_max = models.DecimalField(max_digits=6, decimal_places=2)
    gdp_esperada = models.DecimalField(max_digits=4, decimal_places=2)
    peso_objetivo_salida = models.DecimalField(max_digits=6, decimal_places=2)

    implante_inicial = models.CharField(max_length=40, blank=True)
    reimplante_1 = models.CharField(max_length=40, blank=True)
    reimplante_2 = models.CharField(max_length=40, blank=True)
    reimplante_3 = models.CharField(max_length=40, blank=True)
    reimplante_4 = models.CharField(max_length=40, blank=True)

    dias_recepcion = models.PositiveSmallIntegerField(default=0)
    dias_f1 = models.PositiveSmallIntegerField(default=0)
    dias_transicion = models.PositiveSmallIntegerField(default=14)
    dias_f3 = models.PositiveSmallIntegerField(default=0)
    dias_zilpaterol = models.PositiveSmallIntegerField(default=35)

    history = HistoricalRecords()

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
        return (self.dias_recepcion + self.dias_f1 + self.dias_transicion
                + self.dias_f3 + self.dias_zilpaterol)

    @classmethod
    def resolver(cls, tipo_ganado, tipo_origen, peso_inicial):
        qs = cls.objects.filter(
            activo=True, tipo_ganado=tipo_ganado,
            peso_min__lte=peso_inicial, peso_max__gte=peso_inicial,
        )
        return (qs.filter(tipo_origen=tipo_origen).first()
                or qs.filter(tipo_origen__isnull=True).first())

    class Meta:
        ordering = ['tipo_ganado', 'tipo_origen', 'peso_min']
        constraints = [
            models.CheckConstraint(check=Q(peso_max__gt=F('peso_min')),
                                   name='programa_peso_max_gt_min'),
        ]
```

### Precargas (data migrations)

| Migration | Qué hace |
|---|---|
| `accounts/0002_seed_groups.py` | Crea los 4 grupos con permisos. |
| `catalogos/0002_seed_tipo_corral.py` | Recepción · Engorda · Zilpaterol. |
| `catalogos/0003_seed_tipo_ganado.py` | Macho · Hembra · Vaca. |
| `catalogos/0004_seed_tipo_origen.py` | Corral · Potrero. |
| `catalogos/0005_seed_programa_reimplantes.py` | Lee `docs/DISPONIBILIDAD 2026 1.xlsx` (hoja `PROGRAMA REIMPLANTES`) y carga las 5 categorías × N rangos. Filtra filas vacías y filas separadoras del Excel (las que tienen `peso_min` nulo). Vacas se cargan con `tipo_origen=None`. Conteo esperado: ~14 Machos + ~15 Hembras + ~12 Potrero Macho + ~8 Potrero Hembra + 2 Vacas ≈ 51 filas. |

## URLs y vistas

### Mapa de URLs

```
/                                       → redirect /dashboard/
/dashboard/                             → placeholder "Bienvenido"

/accounts/login/                        → LoginView
/accounts/logout/                       → LogoutView
/accounts/password/change/              → PasswordChangeView
/accounts/perfil/                       → ver/editar perfil

/catalogos/tipos-corral/                → list / nuevo / pk / editar / eliminar
/catalogos/tipos-ganado/                → idem
/catalogos/tipos-origen/                → idem
/catalogos/corrales/                    → idem
/catalogos/proveedores/                 → idem
/catalogos/programa-reimplantes/        → idem (con filtros HTMX)

/admin/                                 → Django admin con history
```

### Patrón de vistas

```python
class CatalogoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True
    paginate_by = 25
```

Por cada modelo: `ListView`, `CreateView`, `DetailView`, `UpdateView`, `DeleteView` (soft-delete que pone `activo=False`). Permisos por vista mapean al permiso Django correspondiente (`view_*`, `add_*`, `change_*`, `delete_*`).

### Forms

`ModelForm` por modelo. Validaciones específicas:

- `ProgramaReimplanteForm.clean()`: valida `peso_max > peso_min` y rechaza si existe traslape de rangos activo en la misma combinación `(tipo_ganado, tipo_origen)`.
- Otros forms: validaciones estándar de unicidad y campos requeridos.

## Templates

```
templates/
├── base.html                     # layout dark del dummy v4
├── partials/
│   ├── _sidebar.html
│   ├── _header.html
│   ├── _flashes.html
│   ├── _pagination.html
│   └── _delete_confirm.html
├── 400.html · 403.html · 404.html · 500.html
├── accounts/
│   ├── login.html
│   ├── logout.html
│   ├── perfil.html
│   └── password_change.html
└── catalogos/
    ├── _form.html
    ├── _list_actions.html
    ├── tipocorral_list.html · tipocorral_form.html · tipocorral_detail.html
    ├── tipoganado_*.html
    ├── tipoorigen_*.html
    ├── corral_*.html
    ├── proveedor_*.html
    └── programareimplante_list.html (con filtros HTMX) · _form.html · _detail.html
```

`base.html` carga:

- CSS: `static/css/sicoga.css` (variables `--bg`, `--surface`, `--bdr`, etc. del dummy).
- HTMX 1.9.x vía CDN.
- Alpine.js 3.x vía CDN.
- Bloques: `title`, `content`, `extra_css`, `extra_js`.

### Sidebar inicial

Visible en Spec A:

- Dashboard (placeholder)
- Catálogos: Corrales, Tipos de Corral, Tipos de Ganado, Tipos de Origen, Proveedores, Programa de Reimplantes
- Administración: Usuarios (admin Django), Bitácora (history viewer), Mi Perfil

Deshabilitado con tag "próximamente":

- Disponibilidad, Cierre, Reportes y demás módulos futuros.

## Manejo de errores

| Condición | Comportamiento |
|---|---|
| 400 | `templates/400.html` con layout dark. |
| 403 | `templates/403.html` "No tienes permiso". |
| 404 | `templates/404.html`. |
| 500 | `templates/500.html` + email a admins (configurado en `prod.py`). |
| Validación de form | Errores inline + flash superior. |
| `ProtectedError` al borrar (FK) | Flash "No se puede eliminar: está usado en X registros". |
| Login expirado | Redirect a `login?next=`. |

## Testing

### Estrategia

| Tipo | Herramienta | Cubre |
|---|---|---|
| Unit modelos | `pytest-django` + `factory-boy` | Propiedades calculadas, `resolver()`, validaciones de modelo. |
| Forms | `pytest-django` | Traslapes, peso_max > peso_min, unicidad. |
| Vistas | `Client` | Permisos por rol, redirects, CRUD completo, soft-delete. |
| Data migrations | `django_db(transaction=True)` | Precargas correctas. |
| Auditoría | `pytest-django` | `HistoricalRecord` con `history_user`. |

### Cobertura objetivo

≥ 85% en `apps/`, configurado en `.coveragerc`.

### Casos críticos mínimos

1. `ProgramaReimplante.resolver(Macho, Corral, 170)` → fila del rango 151–180.
2. `ProgramaReimplante.resolver(Vaca, Corral, 350)` → fila con `tipo_origen=None`.
3. `ProgramaReimplante.resolver(Macho, Corral, 9999)` → `None`.
4. Crear dos programas con rangos solapados en la misma combinación → `ValidationError`.
5. Borrar un `TipoCorral` con `Corral` referenciado → `ProtectedError` traducido a flash.
6. Capturista intenta entrar a `/catalogos/corrales/nuevo/` → 403.
7. Solo Lectura intenta editar un proveedor → 403.
8. Cambiar el `nombre` de un `Corral` genera entrada en `Corral.history`.
9. Login con credenciales inválidas → mensaje en español.
10. Soft-delete pone `activo=False` y el registro deja de aparecer en lista por defecto.

## CI/CD y hooks

### GitHub Actions (`.github/workflows/ci.yml`)

Ejecuta en cada push y pull request:

1. Levanta MySQL 8.0 como servicio.
2. Instala dependencias y `default-libmysqlclient-dev`.
3. Lint: `black --check`, `isort --check`, `flake8`.
4. `python manage.py migrate` con `DATABASE_URL` apuntando al MySQL del job.
5. `pytest --cov=apps --cov-report=xml`.

### pre-commit (`.pre-commit-config.yaml`)

- `black` (Python 3.12).
- `isort`.
- `flake8`.
- `trailing-whitespace`, `end-of-file-fixer`, `check-merge-conflict`, `check-added-large-files (--maxkb=500)`.

## Criterios de aceptación

El Spec A se considera entregable cuando:

| # | Criterio | Verificación |
|---|---|---|
| 1 | El proyecto arranca con `python manage.py runserver` sin errores. | Manual. |
| 2 | `python manage.py migrate` aplica todas las migraciones (incluidas data migrations). | Manual + CI. |
| 3 | Existen los 4 grupos de usuarios con sus permisos. | Test `test_seed_groups.py`. |
| 4 | El programa de reimplantes está precargado con todas las filas del Excel. | Test `test_seed_programa.py`. |
| 5 | Login funciona para los 4 roles, redirigiendo al dashboard. | Test de integración. |
| 6 | Cada uno de los 6 catálogos tiene CRUD completo accesible vía web. | Test por modelo + manual. |
| 7 | Cada modelo registra cambios en `simple_history` con `history_user`. | Test `test_audit.py`. |
| 8 | Capturista no puede crear/editar/eliminar catálogos del Spec A. | Test `test_permisos.py`. |
| 9 | El sidebar muestra catálogos activos y módulos futuros como deshabilitados. | Test de template. |
| 10 | El admin de Django muestra todos los modelos con su historial. | Manual. |
| 11 | CI pasa en verde (lint + tests + cobertura ≥ 85 %). | GitHub Actions. |
| 12 | `pre-commit run --all-files` pasa limpio. | Manual. |
| 13 | `README.md` documenta clonar, crear venv, instalar, configurar `.env`, migrar y correr. | Manual. |
| 14 | 403/404/500 usan layout dark del sistema. | Manual. |
| 15 | Login y catálogos se ven con el look del dummy v4. | Manual visual. |

## Fuera de alcance del Spec A

- Modelo `Lote` y formación con múltiples entradas (Spec B).
- Pantalla de Disponibilidad y cálculos de proyección (Spec C).
- Reimplantes operativos, Transiciones, Zilpaterol, Salidas semanales, Inventario general (Spec D).
- Cierre de lotes y todos sus submódulos (Spec E).
- Dashboard gerencial (Spec F).
- Integración con CATLE (Spec G).
- Pantalla de Hospital (descartada del proyecto).

## Riesgos y supuestos

### Supuestos

- El campo `sufijo_lote` se omite del modelo `TipoGanado` porque el folio del `Lote` será editable libre en Spec B.
- El catálogo `Implante` se difiere a Spec D; el programa de reimplantes guarda nombres como texto libre por ahora.
- La operación de Chamizal es single-tenant; si se vendiera a otro rancho, se desplegaría una instancia separada.
- El servidor Linux donde corre MiContaAI tiene capacidad suficiente para alojar SiCoGa.

### Riesgos

- **Cambios en el Excel base**: la precarga del programa de reimplantes lee `docs/DISPONIBILIDAD 2026 1.xlsx` versionado en repo. Las migraciones no se vuelven a correr en producción, así que si el cliente actualiza el Excel después del Spec A se necesitará un `management command` (ej: `python manage.py importar_programa_reimplantes <archivo.xlsx>`) que se diseñará en Spec D si surge la necesidad. Mientras tanto, las ediciones del cliente se hacen en la pantalla web.
- **Permisos del Capturista**: en Spec A no realiza captura porque los modelos operativos aún no existen. La validación real de su flujo se hará en Specs B/C/D.
- **Rendimiento de `simple_history`**: con catálogos pequeños no es problema, pero hay que vigilar tamaño de tablas históricas en el largo plazo.

## Próximos pasos

Tras la aprobación de este spec, se pasará al skill `superpowers:writing-plans` para generar el plan de implementación paso a paso del Spec A. La ejecución se hará con `superpowers:executing-plans`.
