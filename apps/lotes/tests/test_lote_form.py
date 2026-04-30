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
            clave="CL-MIN",
            nombre="Min",
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

    f = LoteForm(_form_data(setup, cabezas_iniciales="100"))
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
    # Form intenta crear otro con mismo folio en otro corral (que aún no existe,
    # así que pongamos el mismo corral pero el primero ya está activo → falla
    # también por unicidad de corral activo). Para aislar el test del folio,
    # marcamos el primero inactivo.
    Lote.objects.filter(folio="CH-DUP").update(activo=False)

    f = LoteForm(_form_data(setup, folio="CH-DUP", cabezas_iniciales="20"))
    assert not f.is_valid()
    assert "folio" in f.errors
