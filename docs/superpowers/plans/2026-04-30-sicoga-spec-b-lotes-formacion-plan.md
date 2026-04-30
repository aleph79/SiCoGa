# SiCoGa — Spec B: Lotes y Formación (Plan de implementación)

**Fecha:** 2026-04-30
**Spec:** [docs/superpowers/specs/2026-04-30-sicoga-spec-b-lotes-formacion-design.md](../specs/2026-04-30-sicoga-spec-b-lotes-formacion-design.md) (DRAFT v2)
**Repositorio:** https://github.com/aleph79/SiCoGa
**Branch:** `main` (mismo flujo que Spec A — commits incrementales, push después de cada fase)

20 tasks TDD bite-sized. Cada task: test rojo → implementación → test verde → commit. Pre-commit corre black/isort/flake8 automático.

| Phase | Tasks | Resumen |
|---|---|---|
| 1 — Foundation | 1–3 | App `apps.lotes`, modelo `Lote`, registro admin |
| 2 — Cálculos | 4–7 | Properties: kg, días, fechas, kilos, reimplantes, zilpaterol |
| 3 — CRUD UI | 8–13 | Form + 5 vistas + templates + sidebar + HTMX preview |
| 4 — Fusión | 14–17 | `LoteFusion` modelo + función atómica + UI |
| 5 — Permisos + cierre | 18–20 | Seed groups, tests Capturista, smoke |

> Convención: cada Task termina con `git commit` (Conventional Commits) y suite verde con `make test`.

---

## Phase 1 — Foundation

### Task 1: Bootstrap `apps/lotes` empty app

**Files:**
- Create: `apps/lotes/__init__.py`, `apps/lotes/apps.py`, `apps/lotes/models.py`, `apps/lotes/views.py`, `apps/lotes/urls.py`, `apps/lotes/admin.py`, `apps/lotes/forms.py`, `apps/lotes/tests/__init__.py`
- Modify: `config/settings/base.py` (add to `INSTALLED_APPS`)
- Modify: `config/urls.py` (add include)

**Steps:**

1.1. Crear archivos:

```bash
mkdir -p apps/lotes/tests apps/lotes/migrations
touch apps/lotes/{__init__,models,views,urls,admin,forms}.py
touch apps/lotes/tests/__init__.py
touch apps/lotes/migrations/__init__.py
```

1.2. `apps/lotes/apps.py`:

```python
from django.apps import AppConfig


class LotesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lotes"
    verbose_name = "Lotes"
```

1.3. `apps/lotes/urls.py`:

```python
from django.urls import path

app_name = "lotes"
urlpatterns = []  # Se llenan en Tasks 9–13, 16
```

1.4. Añadir `"apps.lotes"` a `INSTALLED_APPS` en `config/settings/base.py`.

1.5. Añadir `path("lotes/", include("apps.lotes.urls", namespace="lotes"))` en `config/urls.py`.

1.6. Verifica:

```bash
python manage.py check
make test  # 86 pasan, sin nuevos
```

1.7. Commit: `chore(lotes): bootstrap empty lotes app`

---

### Task 2: `Lote` model + migration

**Files:**
- Modify: `apps/lotes/models.py`
- Create: `apps/lotes/migrations/0001_initial.py` (autogenerada)
- Create: `apps/lotes/tests/test_lote_model.py`

**Steps:**

2.1. Test failing primero (`apps/lotes/tests/test_lote_model.py`):

```python
"""Tests for Lote model: estructura, constraints, history."""
from datetime import date
from decimal import Decimal

import pytest


@pytest.fixture
def fixtures(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado, TipoOrigen

    ProgramaReimplante.objects.all().delete()
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral_origen": TipoOrigen.objects.get_or_create(nombre="Corral")[0],
        "tipo_corral": TipoCorral.objects.get_or_create(nombre="Engorda")[0],
        "corral": Corral.objects.create(
            clave="C99",
            nombre="Corral Test 99",
            tipo_corral=TipoCorral.objects.get_or_create(nombre="Engorda")[0],
            capacidad_maxima=300,
        ),
    }


def test_lote_str(fixtures):
    from apps.lotes.models import Lote

    lote = Lote.objects.create(
        folio="CH-001",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        tipo_origen=fixtures["corral_origen"],
        cabezas_iniciales=200,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    assert str(lote) == "CH-001 (Macho · C99)"


@pytest.mark.django_db(transaction=True)
def test_lote_folio_unique(fixtures):
    from django.db import IntegrityError

    from apps.lotes.models import Lote

    Lote.objects.create(
        folio="CH-DUP",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    with pytest.raises(IntegrityError):
        Lote.objects.create(
            folio="CH-DUP",
            corral=fixtures["corral"],
            tipo_ganado=fixtures["macho"],
            cabezas_iniciales=100,
            fecha_inicio=date(2026, 4, 30),
            peso_inicial_promedio=Decimal("250.00"),
        )


@pytest.mark.django_db(transaction=True)
def test_un_lote_activo_por_corral(fixtures):
    from django.db import IntegrityError

    from apps.lotes.models import Lote

    Lote.objects.create(
        folio="CH-A",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    with pytest.raises(IntegrityError):
        Lote.objects.create(
            folio="CH-B",
            corral=fixtures["corral"],
            tipo_ganado=fixtures["macho"],
            cabezas_iniciales=50,
            fecha_inicio=date(2026, 4, 30),
            peso_inicial_promedio=Decimal("250.00"),
        )


def test_dos_lotes_misma_corral_si_uno_inactivo(fixtures):
    """Si el primer lote queda inactivo, se puede crear otro en el mismo corral."""
    from apps.lotes.models import Lote

    primero = Lote.objects.create(
        folio="CH-OLD",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 1, 1),
        peso_inicial_promedio=Decimal("250.00"),
    )
    primero.activo = False
    primero.save()

    nuevo = Lote.objects.create(
        folio="CH-NEW",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=200,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("280.00"),
    )
    assert nuevo.pk
```

2.2. `apps/lotes/models.py`:

```python
from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords

from apps.catalogos.models import Corral, ProgramaReimplante, Proveedor, TipoGanado, TipoOrigen
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
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name="Peso de salida objetivo (kg)",
        help_text="Si vacío, se toma del programa aplicable.",
    )
    gdp_esperada = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        verbose_name="GDP esperada (kg/día)",
        help_text="Si vacío, se toma del programa aplicable.",
    )
    observaciones = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
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
```

2.3. Generar y aplicar migración:

```bash
python manage.py makemigrations lotes
python manage.py migrate lotes
```

2.4. Suite verde:

```bash
make test
```

2.5. Commit: `feat(lotes): add Lote model with single-active-per-corral constraint`

---

### Task 3: Admin registration + history smoke test

**Files:**
- Modify: `apps/lotes/admin.py`
- Modify: `apps/lotes/tests/test_lote_model.py` (un test extra)

**Steps:**

3.1. Test failing:

```python
def test_lote_history_records_changes(fixtures):
    from apps.lotes.models import Lote

    lote = Lote.objects.create(
        folio="CH-HIST",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    lote.cabezas_iniciales = 110
    lote.save()
    assert lote.history.count() == 2
```

3.2. `apps/lotes/admin.py`:

```python
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Lote


@admin.register(Lote)
class LoteAdmin(SimpleHistoryAdmin):
    list_display = (
        "folio", "corral", "tipo_ganado", "tipo_origen", "cabezas_iniciales",
        "fecha_inicio", "peso_inicial_promedio", "activo",
    )
    list_filter = ("activo", "tipo_ganado", "tipo_origen", "corral")
    search_fields = ("folio",)
    autocomplete_fields = ("corral", "proveedor")
```

3.3. Test verde, commit: `feat(lotes): register Lote admin with history`

---

## Phase 2 — Cálculos

### Task 4: `kg_por_hacer` y `dias_engorda_proyectados`

**Files:**
- Modify: `apps/lotes/models.py`
- Create: `apps/lotes/tests/test_lote_calculos.py`

4.1. Test failing — usa `peso_salida_objetivo` y `gdp_esperada` directos del lote:

```python
"""Cálculos derivados sobre Lote (sin pasar por ProgramaReimplante todavía)."""
from datetime import date
from decimal import Decimal

import pytest


@pytest.fixture
def fixtures(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado

    ProgramaReimplante.objects.all().delete()
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral": Corral.objects.create(
            clave="C-CALC", nombre="Calc",
            tipo_corral=TipoCorral.objects.get_or_create(nombre="Engorda")[0],
            capacidad_maxima=500,
        ),
    }


def _make(fixtures, **kwargs):
    from apps.lotes.models import Lote

    defaults = dict(
        folio="CH-X",
        corral=fixtures["corral"],
        tipo_ganado=fixtures["macho"],
        cabezas_iniciales=200,
        fecha_inicio=date(2026, 1, 1),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    defaults.update(kwargs)
    return Lote.objects.create(**defaults)


def test_kg_por_hacer(fixtures):
    lote = _make(fixtures)
    assert lote.kg_por_hacer == Decimal("330.00")  # 580 - 250


def test_dias_engorda_proyectados(fixtures):
    lote = _make(fixtures)
    # 330 / 1.30 = 253.84... → int = 253
    assert lote.dias_engorda_proyectados == 253


def test_kg_por_hacer_sin_peso_objetivo_y_sin_programa(fixtures):
    lote = _make(fixtures, peso_salida_objetivo=None, gdp_esperada=None)
    # Sin programa que matchee, kg_por_hacer es None
    assert lote.kg_por_hacer is None
```

4.2. Implementar en `Lote`:

```python
@property
def programa(self):
    from apps.catalogos.models import ProgramaReimplante
    return ProgramaReimplante.resolver(
        self.tipo_ganado, self.tipo_origen, self.peso_inicial_promedio
    )

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
```

4.3. Tests verde, commit: `feat(lotes): add kg_por_hacer + dias_engorda_proyectados`

---

### Task 5: fechas y kilos proyectados

**Files:**
- Modify: `apps/lotes/models.py`
- Modify: `apps/lotes/tests/test_lote_calculos.py`

5.1. Tests failing:

```python
def test_fecha_proyectada_venta(fixtures):
    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    # 253 días desde 2026-01-01 → 2026-09-11
    assert lote.fecha_proyectada_venta == date(2026, 9, 11)


def test_semana_proyectada_venta(fixtures):
    from datetime import date as dt_date

    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    expected_week = dt_date(2026, 9, 11).isocalendar()[1]
    assert lote.semana_proyectada_venta == expected_week


def test_kilos_proyectados_venta(fixtures):
    lote = _make(fixtures, cabezas_iniciales=200, peso_salida_objetivo=Decimal("580"))
    assert lote.kilos_proyectados_venta == Decimal("116000.00")  # 580 * 200
```

5.2. Implementar:

```python
from datetime import timedelta

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
```

5.3. Verde, commit: `feat(lotes): add fecha y kilos proyectados de venta`

---

### Task 6: integración con `ProgramaReimplante`

**Files:**
- Modify: `apps/lotes/tests/test_lote_calculos.py`

6.1. Tests con programa real:

```python
@pytest.fixture
def fixtures_con_programa(fixtures):
    from apps.catalogos.models import ProgramaReimplante, TipoOrigen

    corral_origen = TipoOrigen.objects.get_or_create(nombre="Corral")[0]
    programa = ProgramaReimplante.objects.create(
        tipo_ganado=fixtures["macho"],
        tipo_origen=corral_origen,
        peso_min=Decimal("200"),
        peso_max=Decimal("280"),
        gdp_esperada=Decimal("1.45"),
        peso_objetivo_salida=Decimal("580"),
        dias_zilpaterol=35,
    )
    return {**fixtures, "programa": programa, "corral_origen": corral_origen}


def test_lote_resuelve_programa(fixtures_con_programa):
    lote = _make(
        fixtures_con_programa,
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=None,
        gdp_esperada=None,
        tipo_origen=fixtures_con_programa["corral_origen"],
    )
    assert lote.programa == fixtures_con_programa["programa"]


def test_gdp_y_peso_objetivo_se_toman_del_programa(fixtures_con_programa):
    lote = _make(
        fixtures_con_programa,
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=None,
        gdp_esperada=None,
        tipo_origen=fixtures_con_programa["corral_origen"],
    )
    assert lote.gdp_efectiva == Decimal("1.45")
    assert lote.peso_objetivo_efectivo == Decimal("580.00")


def test_overrides_del_lote_vencen_al_programa(fixtures_con_programa):
    lote = _make(
        fixtures_con_programa,
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("600"),  # override
        gdp_esperada=Decimal("1.50"),         # override
        tipo_origen=fixtures_con_programa["corral_origen"],
    )
    assert lote.gdp_efectiva == Decimal("1.50")
    assert lote.peso_objetivo_efectivo == Decimal("600.00")
```

6.2. La implementación ya quedó en Task 4 (properties `programa`, `gdp_efectiva`, `peso_objetivo_efectivo`). Tests deben pasar sin cambios extra.

6.3. Commit: `test(lotes): verify fallback to ProgramaReimplante values`

---

### Task 7: fechas de reimplantes y entrada a Zilpaterol

**Files:**
- Modify: `apps/lotes/models.py`
- Modify: `apps/lotes/tests/test_lote_calculos.py`

7.1. Tests:

```python
def test_fecha_reimplante_1(fixtures):
    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    assert lote.fecha_reimplante_1 == date(2026, 3, 2)  # +60 días


def test_fecha_reimplante_2_y_3(fixtures):
    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    assert lote.fecha_reimplante_2 == date(2026, 5, 1)  # +120
    assert lote.fecha_reimplante_3 == date(2026, 6, 30)  # +180


def test_fecha_entrada_zilpaterol(fixtures_con_programa):
    lote = _make(
        fixtures_con_programa,
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=None,
        gdp_esperada=None,
        tipo_origen=fixtures_con_programa["corral_origen"],
        fecha_inicio=date(2026, 1, 1),
    )
    # gdp 1.45, kg 330, días 227. Venta 2026-08-16. Zilp = -35 = 2026-07-12
    venta = lote.fecha_proyectada_venta
    assert lote.fecha_entrada_zilpaterol == venta - timedelta(days=35)
```

7.2. Implementar:

```python
def fecha_reimplante(self, n: int):
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

@property
def fecha_entrada_zilpaterol(self):
    if not self.programa or not self.fecha_proyectada_venta:
        return None
    return self.fecha_proyectada_venta - timedelta(days=self.programa.dias_zilpaterol)
```

7.3. Verde, commit: `feat(lotes): add fechas de reimplantes y entrada a zilpaterol`

---

## Phase 3 — CRUD UI

### Task 8: `LoteForm` con validaciones

**Files:**
- Modify: `apps/lotes/forms.py`
- Create: `apps/lotes/tests/test_lote_form.py`

8.1. Tests failing:

```python
"""Tests del LoteForm: capacidad y unicidad."""
from datetime import date
from decimal import Decimal

import pytest


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado

    ProgramaReimplante.objects.all().delete()
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral_chico": Corral.objects.create(
            clave="C-MIN", nombre="Min",
            tipo_corral=TipoCorral.objects.get_or_create(nombre="Engorda")[0],
            capacidad_maxima=100,
        ),
    }


def _form_data(setup, **overrides):
    data = {
        "folio": "CH-FORM",
        "corral": setup["corral_chico"].pk,
        "tipo_ganado": setup["macho"].pk,
        "cabezas_iniciales": "80",
        "fecha_inicio": "2026-04-30",
        "peso_inicial_promedio": "250.00",
        "activo": "on",
    }
    data.update(overrides)
    return data


def test_form_acepta_dentro_de_capacidad(setup):
    from apps.lotes.forms import LoteForm

    f = LoteForm(_form_data(setup, cabezas_iniciales="100"))  # exactamente la capacidad
    assert f.is_valid(), f.errors


def test_form_rechaza_excede_capacidad(setup):
    from apps.lotes.forms import LoteForm

    f = LoteForm(_form_data(setup, cabezas_iniciales="101"))
    assert not f.is_valid()
    assert "cabezas_iniciales" in f.errors


def test_form_folio_duplicado(setup):
    from apps.lotes.forms import LoteForm
    from apps.lotes.models import Lote

    Lote.objects.create(
        folio="CH-DUP",
        corral=setup["corral_chico"],
        tipo_ganado=setup["macho"],
        cabezas_iniciales=80,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    f = LoteForm(_form_data(setup, folio="CH-DUP", cabezas_iniciales="20"))
    assert not f.is_valid()
    assert "folio" in f.errors
```

8.2. `apps/lotes/forms.py`:

```python
from django import forms
from django.core.exceptions import ValidationError

from .models import Lote


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = [
            "folio", "corral", "tipo_ganado", "tipo_origen", "proveedor",
            "cabezas_iniciales", "fecha_inicio", "peso_inicial_promedio",
            "peso_salida_objetivo", "gdp_esperada", "observaciones", "activo",
        ]
        widgets = {
            "folio": forms.TextInput(attrs={"class": "input"}),
            "cabezas_iniciales": forms.NumberInput(attrs={"class": "input proyeccion-input", "min": 1}),
            "fecha_inicio": forms.DateInput(attrs={"class": "input proyeccion-input", "type": "date"}),
            "peso_inicial_promedio": forms.NumberInput(attrs={"class": "input proyeccion-input", "step": "0.01"}),
            "peso_salida_objetivo": forms.NumberInput(attrs={"class": "input proyeccion-input", "step": "0.01"}),
            "gdp_esperada": forms.NumberInput(attrs={"class": "input proyeccion-input", "step": "0.01"}),
            "observaciones": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }

    def clean(self):
        cd = super().clean()
        corral = cd.get("corral")
        cabezas = cd.get("cabezas_iniciales")
        if corral and cabezas and cabezas > corral.capacidad_maxima:
            raise ValidationError({
                "cabezas_iniciales": (
                    f"Excede la capacidad del corral ({corral.capacidad_maxima} cab.)."
                )
            })
        return cd
```

8.3. Verde, commit: `feat(lotes): add LoteForm with capacity validation`

---

### Task 9: `LoteListView` + template

**Files:**
- Modify: `apps/lotes/views.py`, `apps/lotes/urls.py`
- Create: `templates/lotes/lote_list.html`

9.1. Test:

```python
@pytest.mark.django_db(transaction=True)
def test_lista_muestra_lotes_activos(client, admin_user_b):
    # admin_user_b es fixture que crea Administrador con todos los perms (espejo de Spec A)
    ...
```

9.2. Vista (espejando `ProgramaReimplanteListView`):

```python
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import CatalogoMixin

from .forms import LoteForm
from .models import Lote


class LoteListView(CatalogoMixin, ListView):
    model = Lote
    template_name = "lotes/lote_list.html"
    permission_required = "lotes.view_lote"
    context_object_name = "objetos"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "corral", "tipo_ganado", "tipo_origen", "proveedor"
        )
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs
```

9.3. Template `templates/lotes/lote_list.html`: encabezado, botón "+ Nuevo", tabla con columnas Folio · Corral · Tipo · Origen · Cabezas · Peso inicio · Fecha inicio · Días · Estado · acciones.

9.4. URL: `path("", views.LoteListView.as_view(), name="lote_list"),` en `apps/lotes/urls.py`.

9.5. Commit: `feat(lotes): add LoteListView with template`

---

### Task 10: `LoteCreateView` + template + integración con HTMX preview

**Files:**
- Modify: `apps/lotes/views.py`, `apps/lotes/urls.py`
- Create: `templates/lotes/lote_form.html`, `templates/lotes/_proyeccion_preview.html`

10.1. Tests:

```python
def test_crear_lote_valido_redirige_a_lista(client, admin_user_b, setup):
    ...

def test_capturista_puede_crear(client, capturista_b, setup):
    ...
```

10.2. Vista:

```python
class LoteCreateView(CatalogoMixin, CreateView):
    model = Lote
    form_class = LoteForm
    template_name = "lotes/lote_form.html"
    permission_required = "lotes.add_lote"
    success_url = reverse_lazy("lotes:lote_list")
```

10.3. Template `lote_form.html` con dos columnas: form a la izquierda, `<div id="proyeccion-box">` a la derecha que carga vía HTMX.

```html
{% extends "base.html" %}
{% block title %}{% if object %}Editar{% else %}Nuevo{% endif %} lote{% endblock %}
{% block content %}
<div class="ph"><div class="ptitle">{% if object %}Editar{% else %}Alta de{% endif %} Lote</div></div>
<div class="g2">
  <div class="card">
    <form method="post"
          hx-post="{% url 'lotes:lote_preview' %}"
          hx-trigger="change delay:300ms from:.proyeccion-input"
          hx-target="#proyeccion-box">
      {% csrf_token %}
      {% include "catalogos/_form.html" with cancel_url=request.META.HTTP_REFERER %}
    </form>
  </div>
  <div id="proyeccion-box">
    {% include "lotes/_proyeccion_preview.html" %}
  </div>
</div>
{% endblock %}
```

10.4. Commit: `feat(lotes): add LoteCreateView with HTMX projection preview`

---

### Task 11: Update / Detail / Delete views

**Files:**
- Modify: `apps/lotes/views.py`, `apps/lotes/urls.py`
- Create: `templates/lotes/lote_detail.html`, `templates/lotes/lote_confirm_delete.html`

11.1. Tres vistas (`LoteUpdateView`, `LoteDetailView`, `LoteDeleteView`) espejando el patrón de `Proveedor` o `Corral` en Spec A.

11.2. Templates mínimos: `lote_detail.html` muestra todos los cálculos derivados (días, fechas, kilos); `lote_confirm_delete.html` extiende `partials/_delete_confirm.html`.

11.3. Tests de cada vista (acceso, soft delete actualiza `activo=False`).

11.4. Commit: `feat(lotes): add update/detail/delete views`

---

### Task 12: `PreviewProyeccionView` HTMX endpoint

**Files:**
- Modify: `apps/lotes/views.py`, `apps/lotes/urls.py`

12.1. Test failing:

```python
def test_preview_devuelve_dias_proyectados(client, admin_user_b, setup):
    client.force_login(admin_user_b)
    response = client.post(
        "/lotes/preview-proyeccion/",
        {
            "tipo_ganado": setup["macho"].pk,
            "cabezas_iniciales": "200",
            "peso_inicial_promedio": "250",
            "peso_salida_objetivo": "580",
            "gdp_esperada": "1.30",
            "fecha_inicio": "2026-01-01",
        },
    )
    assert response.status_code == 200
    assert b"253" in response.content  # días proyectados
```

12.2. Vista (LoginRequired pero NO permission required — todos los autenticados pueden ver el preview):

```python
from django.contrib.auth.mixins import LoginRequiredMixin


class PreviewProyeccionView(LoginRequiredMixin, View):
    def post(self, request):
        # Construir un Lote NO guardado con los valores del POST
        lote = Lote(
            tipo_ganado_id=request.POST.get("tipo_ganado") or None,
            tipo_origen_id=request.POST.get("tipo_origen") or None,
            cabezas_iniciales=int(request.POST.get("cabezas_iniciales") or 0),
            peso_inicial_promedio=request.POST.get("peso_inicial_promedio") or 0,
            peso_salida_objetivo=request.POST.get("peso_salida_objetivo") or None,
            gdp_esperada=request.POST.get("gdp_esperada") or None,
            fecha_inicio=request.POST.get("fecha_inicio") or None,
        )
        return render(request, "lotes/_proyeccion_preview.html", {"lote": lote})
```

12.3. Template `_proyeccion_preview.html` con todas las cifras calculadas (formato "—" si la propiedad devuelve None).

12.4. Commit: `feat(lotes): add HTMX preview endpoint for projection box`

---

### Task 13: Sidebar entry + URL routing finalizado

**Files:**
- Modify: `templates/partials/_sidebar.html`
- Modify: `apps/lotes/urls.py`

13.1. Añadir sección "Operación" en el sidebar:

```html
<div class="ndiv"></div>
<div class="nsec">Operación</div>
<a class="ni {% if 'lotes' in request.path %}active{% endif %}" href="/lotes/">
  <span class="ico">🐂</span> Lotes
</a>
```

13.2. Verificar todas las URLs declaradas (`lote_list`, `lote_create`, `lote_detail`, `lote_update`, `lote_delete`, `lote_preview`).

13.3. Smoke test integración: `client.get("/lotes/")` con admin debe ser 200; con anónimo 302.

13.4. Commit: `feat(lotes): wire sidebar entry and finalize URL routes`

---

## Phase 4 — Fusión

### Task 14: `LoteFusion` model + migration

**Files:**
- Modify: `apps/lotes/models.py`
- Create: `apps/lotes/migrations/0002_lotefusion.py` (autogenerada)
- Create: `apps/lotes/tests/test_lote_fusion_model.py`

14.1. Tests failing:

```python
def test_fusion_str(fixtures):
    from apps.lotes.models import Lote, LoteFusion
    a = Lote.objects.create(folio="A", corral=fixtures["corral"], ...)
    b_corral = ...  # otro corral
    b = Lote.objects.create(folio="B", corral=b_corral, ...)

    f = LoteFusion.objects.create(
        lote_destino=b, lote_origen=a, cabezas_movidas=50,
        fecha_fusion=date(2026, 4, 30),
    )
    assert str(f) == "A → B (50 cab.)"


@pytest.mark.django_db(transaction=True)
def test_fusion_destino_distinto_de_origen():
    # check_constraint nivel BD
    ...
```

14.2. Model:

```python
class LoteFusion(TimeStampedModel):
    lote_destino = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="fusiones_recibidas")
    lote_origen = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="fusiones_dadas")
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

14.3. `makemigrations lotes && migrate`. Commit: `feat(lotes): add LoteFusion model`

---

### Task 15: función `fusionar()` atómica + tests

**Files:**
- Create: `apps/lotes/services.py`
- Create: `apps/lotes/tests/test_lote_fusion_service.py`

15.1. Tests:

```python
def test_fusionar_suma_cabezas_y_marca_origen_inactivo(...):
    a = ... 100 cabezas activo en C1
    b = ... 80 cabezas activo en C2

    fusionar(destino=b, origen=a, fecha_fusion=date(2026, 4, 30))

    a.refresh_from_db(); b.refresh_from_db()
    assert b.cabezas_iniciales == 180
    assert a.activo is False


def test_fusionar_genera_registro(...):
    ...
    assert LoteFusion.objects.count() == 1


def test_fusionar_origen_inactivo_falla(...):
    ...
    a.activo = False; a.save()
    with pytest.raises(ValueError):
        fusionar(destino=b, origen=a, ...)


def test_fusionar_es_atomico(...):
    """Si algo falla a mitad, ninguno de los cambios se aplica."""
    ...
```

15.2. `apps/lotes/services.py`:

```python
from datetime import date as date_type

from django.db import transaction

from .models import Lote, LoteFusion


@transaction.atomic
def fusionar(*, destino: Lote, origen: Lote, fecha_fusion: date_type, notas: str = "") -> LoteFusion:
    if not origen.activo:
        raise ValueError("El lote origen ya está inactivo")
    if not destino.activo:
        raise ValueError("El lote destino ya está inactivo")
    if destino.pk == origen.pk:
        raise ValueError("No puedes fusionar un lote consigo mismo")

    cabezas = origen.cabezas_iniciales

    fusion = LoteFusion.objects.create(
        lote_destino=destino,
        lote_origen=origen,
        cabezas_movidas=cabezas,
        fecha_fusion=fecha_fusion,
        notas=notas,
    )

    destino.cabezas_iniciales += cabezas
    destino.observaciones = (
        (destino.observaciones or "")
        + f"\n[{fecha_fusion}] Fusión: +{cabezas} cab. del lote {origen.folio}."
    ).strip()
    destino.save()

    origen.activo = False
    origen.observaciones = (
        (origen.observaciones or "")
        + f"\n[{fecha_fusion}] Fusionado a lote {destino.folio}."
    ).strip()
    origen.save()

    return fusion
```

15.3. Verde, commit: `feat(lotes): add atomic fusionar() service`

---

### Task 16: `LoteFusionView` + form + template

**Files:**
- Modify: `apps/lotes/views.py`, `apps/lotes/forms.py`, `apps/lotes/urls.py`
- Create: `templates/lotes/lote_fusion.html`

16.1. Form:

```python
class LoteFusionForm(forms.Form):
    lote_origen = forms.ModelChoiceField(queryset=Lote.objects.none())
    fecha_fusion = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    notas = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, destino=None, **kwargs):
        super().__init__(*args, **kwargs)
        if destino:
            self.fields["lote_origen"].queryset = Lote.objects.filter(
                activo=True
            ).exclude(pk=destino.pk)
```

16.2. View:

```python
class LoteFusionView(CatalogoMixin, View):
    permission_required = "lotes.add_lotefusion"

    def get(self, request, pk):
        destino = get_object_or_404(Lote, pk=pk, activo=True)
        form = LoteFusionForm(destino=destino)
        return render(request, "lotes/lote_fusion.html", {"destino": destino, "form": form})

    def post(self, request, pk):
        from .services import fusionar

        destino = get_object_or_404(Lote, pk=pk, activo=True)
        form = LoteFusionForm(request.POST, destino=destino)
        if not form.is_valid():
            return render(request, "lotes/lote_fusion.html", {"destino": destino, "form": form})

        fusionar(
            destino=destino,
            origen=form.cleaned_data["lote_origen"],
            fecha_fusion=form.cleaned_data["fecha_fusion"],
            notas=form.cleaned_data["notas"],
        )
        messages.success(request, f"Lote {destino.folio} actualizado por fusión.")
        return redirect("lotes:lote_detail", pk=destino.pk)
```

16.3. Template muestra el destino arriba (folio, cabezas actuales) y el form abajo. Botón en `lote_detail.html`: si `obj.activo` y user tiene permiso, link "Fusionar otro lote en éste" → `/lotes/<pk>/fusionar/`.

16.4. Commit: `feat(lotes): add LoteFusionView with form`

---

### Task 17: Tests de integración de fusión

**Files:**
- Create/Modify: `apps/lotes/tests/test_lote_fusion_view.py`

17.1. Tests E2E con `client.post`:
- Admin fusiona A en B → redirige a detail de B → BD refleja cambios.
- Capturista puede fusionar.
- Solo Lectura recibe 403.
- Tras fusión, el corral de A vuelve a aceptar otro lote (`Corral.ocupacion_actual` es 0).

17.2. Commit: `test(lotes): integration tests for fusion flow`

---

## Phase 5 — Permisos + cierre

### Task 18: Seed de permisos para Capturista

**Files:**
- Create: `apps/accounts/migrations/0003_capturista_lotes_perms.py`

18.1. Data migration que añade al grupo Capturista los permisos `add_lote`, `change_lote`, `view_lote`, `add_lotefusion`, `view_lotefusion`:

```python
from django.db import migrations


PERMISOS = [
    ("lotes", "add_lote"),
    ("lotes", "change_lote"),
    ("lotes", "view_lote"),
    ("lotes", "add_lotefusion"),
    ("lotes", "view_lotefusion"),
]


def forwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    capturista, _ = Group.objects.get_or_create(name="Capturista")
    perms = Permission.objects.filter(
        content_type__app_label__in=[a for a, _ in PERMISOS],
        codename__in=[c for _, c in PERMISOS],
    )
    capturista.permissions.add(*perms)


def backwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    capturista = Group.objects.filter(name="Capturista").first()
    if not capturista:
        return
    perms = Permission.objects.filter(codename__in=[c for _, c in PERMISOS])
    capturista.permissions.remove(*perms)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_seed_groups"),
        ("lotes", "0002_lotefusion"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
```

18.2. Commit: `feat(accounts): grant Capturista add/change/view on Lote and LoteFusion`

---

### Task 19: Tests E2E de permisos por rol

**Files:**
- Create: `apps/lotes/tests/test_permisos_lotes.py`

19.1. Tests parametrizados (Capturista y Solo Lectura) sobre URLs `lote_list`, `lote_create`, `lote_update`, `lote_delete`, `lote_fusionar`.

19.2. Commit: `test(lotes): role-based permission tests`

---

### Task 20: Documentación + smoke + push final de Spec B

**Files:**
- Modify: `README.md` (añadir mención de Lotes)
- Modify: `docs/DEPLOY-ALMALINUX.md` (smoke checklist actualizado)
- Modify: `docs/superpowers/specs/2026-04-30-sicoga-spec-b-lotes-formacion-design.md` (cambiar estado a ✅)

20.1. README: añadir "Lotes" a la lista de features de la sección "Estructura".

20.2. Smoke checklist en deploy guide:
- [ ] `/lotes/` lista vacía si no hay datos
- [ ] Crear un lote calcula proyección automática en vivo (HTMX)
- [ ] Editar lote actualiza cifras
- [ ] Fusionar dos lotes mueve cabezas y libera corral
- [ ] Capturista crea/edita pero no elimina

20.3. Cambiar header del spec a `**Estado:** ✅ ENTREGADO 2026-XX-XX`.

20.4. Commit final: `docs: close Spec B (Lotes y Formacion)` + push.

---

## Definition of Done — Spec B

- [ ] 20 tasks completados con commits incrementales en `main`
- [ ] Suite verde (~110+ tests pasando)
- [ ] Cobertura ≥85% en `apps.lotes`
- [ ] Smoke checklist marcado en producción contra `https://sicoga.com/lotes/`
- [ ] Spec doc actualizado a estado ENTREGADO
- [ ] `git push` final empuja todo a origin/main
