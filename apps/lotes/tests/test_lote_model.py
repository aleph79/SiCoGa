"""Tests for Lote model: estructura, constraints, history."""

from datetime import date
from decimal import Decimal

import pytest


@pytest.fixture
def fixtures(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado, TipoOrigen

    ProgramaReimplante.objects.all().delete()
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral_origen": TipoOrigen.objects.get_or_create(nombre="Corral")[0],
        "tipo_corral": tipo_corral,
        "corral": Corral.objects.create(
            clave="CL99",
            nombre="Corral Test 99",
            tipo_corral=tipo_corral,
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
    assert str(lote) == "CH-001 (Macho · CL99)"


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
