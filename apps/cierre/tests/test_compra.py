"""Tests para compra/recepción del lote (Spec E.2)."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_e2(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_e2", email="ae2@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    c = Corral.objects.create(
        clave="CL-CMP", nombre="Cmp", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-CMP",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=220,
        fecha_inicio=date.today() - timedelta(days=30),
        peso_inicial_promedio=Decimal("251.50"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote}


def test_lote_sin_compra_props_son_none(setup):
    lote = setup["lote"]
    assert lote.peso_promedio_origen is None
    assert lote.peso_promedio_recibo is None
    assert lote.merma_transito_cabezas is None
    assert lote.costo_por_cabeza is None
    assert lote.costo_por_kilo is None


def test_merma_transito(setup):
    lote = setup["lote"]
    lote.cabezas_origen = 224
    lote.kilos_origen = Decimal("56000")
    lote.kilos_recibo = Decimal("55330")
    lote.save()
    lote.refresh_from_db()
    assert lote.merma_transito_cabezas == 4
    assert lote.merma_transito_kilos == Decimal("670")


def test_pesos_promedio(setup):
    lote = setup["lote"]
    lote.cabezas_origen = 224
    lote.kilos_origen = Decimal("56000")
    lote.kilos_recibo = Decimal("55330")
    lote.save()
    lote.refresh_from_db()
    assert lote.peso_promedio_origen == Decimal("250")
    assert lote.peso_promedio_recibo == Decimal("251.50")


def test_costos(setup):
    lote = setup["lote"]
    lote.kilos_recibo = Decimal("55330")
    lote.costo_compra = Decimal("2486850")
    lote.save()
    lote.refresh_from_db()
    assert lote.costo_por_cabeza == pytest.approx(Decimal("11303.86"), abs=Decimal("0.01"))
    assert lote.costo_por_kilo == pytest.approx(Decimal("44.95"), abs=Decimal("0.01"))


@pytest.mark.django_db(transaction=True)
def test_view_compra_carga(client, admin_e2, setup):
    client.force_login(admin_e2)
    response = client.get(reverse("cierre:compra_lote", args=[setup["lote"].pk]))
    assert response.status_code == 200
    assert b"CH-CMP" in response.content


@pytest.mark.django_db(transaction=True)
def test_view_compra_guarda_datos(client, admin_e2, setup):
    client.force_login(admin_e2)
    response = client.post(
        reverse("cierre:compra_lote", args=[setup["lote"].pk]),
        {
            "fecha_compra": "2026-04-01",
            "cabezas_origen": "224",
            "kilos_origen": "56000.00",
            "kilos_recibo": "55330.00",
            "costo_compra": "2486850.00",
        },
        follow=True,
    )
    assert response.status_code == 200
    setup["lote"].refresh_from_db()
    assert setup["lote"].cabezas_origen == 224
    assert setup["lote"].costo_compra == Decimal("2486850.00")


@pytest.mark.django_db(transaction=True)
def test_anonimo_no_puede_editar_compra(client, setup):
    response = client.get(reverse("cierre:compra_lote", args=[setup["lote"].pk]))
    assert response.status_code == 302
