"""Cálculos derivados sobre Lote."""

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
            clave="CL-CALC",
            nombre="Calc",
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
    assert lote.kg_por_hacer == Decimal("330.00")


def test_dias_engorda_proyectados(fixtures):
    lote = _make(fixtures)
    # 330 / 1.30 = 253.846... → int = 253
    assert lote.dias_engorda_proyectados == 253


def test_kg_por_hacer_sin_peso_objetivo_y_sin_programa(fixtures):
    lote = _make(fixtures, peso_salida_objetivo=None, gdp_esperada=None)
    assert lote.kg_por_hacer is None


def test_dias_engorda_sin_gdp(fixtures):
    lote = _make(fixtures, gdp_esperada=None)
    assert lote.dias_engorda_proyectados is None
