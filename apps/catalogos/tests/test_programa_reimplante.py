"""Tests for ProgramaReimplante model: properties and resolver()."""

from decimal import Decimal

import pytest


@pytest.fixture
def tipos(db):
    from apps.catalogos.models import TipoGanado, TipoOrigen

    return {
        "macho": TipoGanado.objects.create(nombre="Macho"),
        "hembra": TipoGanado.objects.create(nombre="Hembra"),
        "vaca": TipoGanado.objects.create(nombre="Vaca"),
        "corral": TipoOrigen.objects.create(nombre="Corral"),
        "potrero": TipoOrigen.objects.create(nombre="Potrero"),
    }


@pytest.fixture
def programa_machos(tipos):
    from apps.catalogos.models import ProgramaReimplante

    return ProgramaReimplante.objects.create(
        tipo_ganado=tipos["macho"],
        tipo_origen=tipos["corral"],
        peso_min=Decimal("151"),
        peso_max=Decimal("180"),
        gdp_esperada=Decimal("1.35"),
        peso_objetivo_salida=Decimal("580"),
        dias_recepcion=5,
        dias_f1=151,
        dias_transicion=14,
        dias_f3=107,
        dias_zilpaterol=35,
    )


@pytest.fixture
def programa_vacas(tipos):
    """Vaca con tipo_origen=None (comodín)."""
    from apps.catalogos.models import ProgramaReimplante

    return ProgramaReimplante.objects.create(
        tipo_ganado=tipos["vaca"],
        tipo_origen=None,
        peso_min=Decimal("0"),
        peso_max=Decimal("400"),
        gdp_esperada=Decimal("1.60"),
        peso_objetivo_salida=Decimal("485"),
        dias_recepcion=0,
        dias_f1=0,
        dias_transicion=14,
        dias_f3=36,
        dias_zilpaterol=35,
    )


def test_peso_promedio(programa_machos):
    assert programa_machos.peso_promedio == Decimal("165.5")


def test_kg_por_hacer(programa_machos):
    assert programa_machos.kg_por_hacer == Decimal("414.5")


def test_dias_estancia(programa_machos):
    # 414.5 / 1.35 = 307.04 -> int = 307
    assert programa_machos.dias_estancia == 307


def test_total_dias(programa_machos):
    # 5 + 151 + 14 + 107 + 35 = 312
    assert programa_machos.total_dias == 312


def test_resolver_finds_match(programa_machos, tipos):
    from apps.catalogos.models import ProgramaReimplante

    found = ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("170"))
    assert found == programa_machos


def test_resolver_returns_none_when_no_match(tipos):
    from apps.catalogos.models import ProgramaReimplante

    assert ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("9999")) is None


def test_resolver_falls_back_to_null_origen(programa_vacas, tipos):
    """Vacas se resuelven con tipo_origen=None aunque se pase Corral."""
    from apps.catalogos.models import ProgramaReimplante

    found = ProgramaReimplante.resolver(tipos["vaca"], tipos["corral"], Decimal("350"))
    assert found == programa_vacas


def test_resolver_skips_inactive(programa_machos, tipos):
    from apps.catalogos.models import ProgramaReimplante

    programa_machos.activo = False
    programa_machos.save()
    assert ProgramaReimplante.resolver(tipos["macho"], tipos["corral"], Decimal("170")) is None


def test_history_records_changes(programa_machos):
    programa_machos.gdp_esperada = Decimal("1.40")
    programa_machos.save()
    assert programa_machos.history.count() == 2


@pytest.mark.django_db(transaction=True)
def test_check_constraint_peso_max_gt_min(tipos):
    from django.db.utils import IntegrityError

    from apps.catalogos.models import ProgramaReimplante

    with pytest.raises(IntegrityError):
        ProgramaReimplante.objects.create(
            tipo_ganado=tipos["macho"],
            tipo_origen=tipos["corral"],
            peso_min=Decimal("200"),
            peso_max=Decimal("100"),
            gdp_esperada=Decimal("1"),
            peso_objetivo_salida=Decimal("300"),
        )
