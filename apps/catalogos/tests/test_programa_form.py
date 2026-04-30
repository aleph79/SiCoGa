from decimal import Decimal

import pytest


@pytest.fixture
def tipos(db):
    from apps.catalogos.models import ProgramaReimplante, TipoGanado, TipoOrigen

    ProgramaReimplante.objects.all().delete()
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral": TipoOrigen.objects.get_or_create(nombre="Corral")[0],
    }


def _form_data(tipos, peso_min, peso_max):
    return {
        "tipo_ganado": tipos["macho"].pk,
        "tipo_origen": tipos["corral"].pk,
        "peso_min": str(peso_min),
        "peso_max": str(peso_max),
        "gdp_esperada": "1.30",
        "peso_objetivo_salida": "580",
        "dias_recepcion": "5",
        "dias_f1": "100",
        "dias_transicion": "14",
        "dias_f3": "100",
        "dias_zilpaterol": "35",
        "activo": "on",
    }


def test_form_rejects_peso_max_le_min(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm

    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("200"), Decimal("100")))
    assert not f.is_valid()
    assert "peso_max" in f.errors or "__all__" in f.errors


def test_form_rejects_overlap_with_active_program(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("180"), Decimal("250")))
    assert not f.is_valid()
    assert "__all__" in f.errors


def test_form_allows_non_overlapping(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("201"), Decimal("250")))
    assert f.is_valid(), f.errors


def test_form_excludes_self_when_editing(tipos):
    from apps.catalogos.forms import ProgramaReimplanteForm
    from apps.catalogos.models import ProgramaReimplante

    obj = ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("100"),
        peso_max=Decimal("200"),
        gdp_esperada=Decimal("1"),
        peso_objetivo_salida=Decimal("500"),
    )
    f = ProgramaReimplanteForm(_form_data(tipos, Decimal("100"), Decimal("200")), instance=obj)
    assert f.is_valid(), f.errors
