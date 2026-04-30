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


def test_fecha_proyectada_venta(fixtures):
    from datetime import timedelta

    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    # 253 días desde 2026-01-01
    assert lote.fecha_proyectada_venta == date(2026, 1, 1) + timedelta(days=253)


def test_semana_proyectada_venta(fixtures):
    lote = _make(fixtures, fecha_inicio=date(2026, 1, 1))
    expected = lote.fecha_proyectada_venta.isocalendar()[1]
    assert lote.semana_proyectada_venta == expected


def test_kilos_proyectados_venta(fixtures):
    lote = _make(fixtures, cabezas_iniciales=200, peso_salida_objetivo=Decimal("580"))
    assert lote.kilos_proyectados_venta == Decimal("116000.00")


def test_fecha_proyectada_venta_sin_dias(fixtures):
    lote = _make(fixtures, gdp_esperada=None)
    assert lote.fecha_proyectada_venta is None


def test_kilos_proyectados_venta_sin_peso_objetivo(fixtures):
    lote = _make(fixtures, peso_salida_objetivo=None, gdp_esperada=None)
    assert lote.kilos_proyectados_venta is None


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
        peso_salida_objetivo=Decimal("600"),
        gdp_esperada=Decimal("1.50"),
        tipo_origen=fixtures_con_programa["corral_origen"],
    )
    assert lote.gdp_efectiva == Decimal("1.50")
    assert lote.peso_objetivo_efectivo == Decimal("600.00")
