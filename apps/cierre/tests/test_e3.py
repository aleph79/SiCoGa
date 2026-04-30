"""Tests para Alimentacion y Medicacion (Spec E.3)."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_e3(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_e3", email="ae3@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import (
        Corral,
        Formula,
        Medicamento,
        ProgramaReimplante,
        TipoCorral,
        TipoGanado,
    )
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    formula = Formula.objects.get_or_create(
        nombre="F1 sin melaza", defaults={"costo_kg": Decimal("3.20")}
    )[0]
    formula.costo_kg = Decimal("3.20")
    formula.save()
    medicamento = Medicamento.objects.create(
        nombre="Draxxin", unidad_dosis="ml/cab", costo_unitario=Decimal("7.36")
    )
    c = Corral.objects.create(
        clave="CL-E3", nombre="E3", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-E3",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=30),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote, "formula": formula, "medicamento": medicamento}


def test_formulas_seedeadas(db):
    from apps.catalogos.models import Formula

    assert Formula.objects.count() >= 5


def test_alimentacion_dias_y_costo(setup):
    from apps.cierre.models import Alimentacion

    a = Alimentacion.objects.create(
        lote=setup["lote"],
        formula=setup["formula"],
        fecha_inicio=date(2026, 4, 1),
        fecha_fin=date(2026, 4, 21),
        kg_consumidos=Decimal("41160"),
    )
    assert a.dias == 21
    assert a.costo_kg_efectivo == Decimal("3.20")
    assert a.costo_total == Decimal("131712.00")


def test_alimentacion_override_costo(setup):
    from apps.cierre.models import Alimentacion

    a = Alimentacion.objects.create(
        lote=setup["lote"],
        formula=setup["formula"],
        fecha_inicio=date(2026, 4, 1),
        fecha_fin=date(2026, 4, 10),
        kg_consumidos=Decimal("1000"),
        costo_kg=Decimal("4.00"),  # override
    )
    assert a.costo_kg_efectivo == Decimal("4.00")
    assert a.costo_total == Decimal("4000.00")


def test_medicacion_costo_total(setup):
    from apps.cierre.models import Medicacion

    m = Medicacion.objects.create(
        lote=setup["lote"],
        medicamento=setup["medicamento"],
        tipo="recepcion",
        fecha=date.today(),
        cabezas=220,
    )
    assert m.costo_unitario_efectivo == Decimal("7.36")
    assert m.costo_total == Decimal("1619.20")  # 7.36 * 220


def test_medicacion_override(setup):
    from apps.cierre.models import Medicacion

    m = Medicacion.objects.create(
        lote=setup["lote"],
        medicamento=setup["medicamento"],
        tipo="hospital",
        fecha=date.today(),
        cabezas=1,
        costo_unitario=Decimal("100"),
        arete="ABC123",
    )
    assert m.costo_total == Decimal("100")


@pytest.mark.django_db(transaction=True)
def test_admin_registra_alimentacion(client, admin_e3, setup):
    from apps.cierre.models import Alimentacion

    client.force_login(admin_e3)
    response = client.post(
        reverse("cierre:registrar_alimentacion"),
        {
            "lote": setup["lote"].pk,
            "formula": setup["formula"].pk,
            "fecha_inicio": "2026-04-01",
            "fecha_fin": "2026-04-21",
            "kg_consumidos": "41160.00",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Alimentacion.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_admin_registra_medicacion(client, admin_e3, setup):
    from apps.cierre.models import Medicacion

    client.force_login(admin_e3)
    response = client.post(
        reverse("cierre:registrar_medicacion"),
        {
            "lote": setup["lote"].pk,
            "medicamento": setup["medicamento"].pk,
            "tipo": "recepcion",
            "fecha": date.today().isoformat(),
            "cabezas": 220,
            "dosis_descripcion": "2.5 ml/cab",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Medicacion.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_listas_cargan(client, admin_e3, setup):
    client.force_login(admin_e3)
    assert client.get(reverse("cierre:alimentaciones")).status_code == 200
    assert client.get(reverse("cierre:medicaciones")).status_code == 200


@pytest.mark.django_db(transaction=True)
def test_anonimo_redirige(client):
    for url in ("cierre:alimentaciones", "cierre:medicaciones"):
        assert client.get(reverse(url)).status_code == 302
