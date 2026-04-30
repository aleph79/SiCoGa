"""Tests para Muerte, Venta y properties Lote.cabezas_actuales/mortalidad."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_e(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_e", email="ae@x.com", password="p", is_staff=True
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
        clave="CL-CRE",
        nombre="Cre",
        tipo_corral=tipo_corral,
        capacidad_maxima=300,
    )
    lote = Lote.objects.create(
        folio="CH-CRE",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=60),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote, "corral": c, "macho": macho}


def test_muerte_str(setup):
    from apps.cierre.models import Muerte

    m = Muerte.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        causa="Neumonía",
    )
    assert "CH-CRE" in str(m)
    assert "Neumonía" in str(m)


def test_venta_calculos(setup):
    from apps.cierre.models import Venta

    v = Venta.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        cliente="Rastro Norteño",
        cabezas=200,
        kilos=Decimal("60000"),
        precio_kg=Decimal("52.00"),
    )
    assert v.ingreso_total == Decimal("3120000.00")
    assert v.peso_promedio == Decimal("300.00")
    assert v.precio_cabeza == Decimal("15600.00")


def test_lote_cabezas_actuales_sin_muertes_ni_ventas(setup):
    assert setup["lote"].cabezas_actuales == 200
    assert setup["lote"].mortalidad_pct == 0


def test_lote_cabezas_actuales_resta_muertes_y_ventas(setup):
    from apps.cierre.models import Muerte, Venta

    Muerte.objects.create(lote=setup["lote"], fecha=date.today(), causa="Neumonía")
    Muerte.objects.create(lote=setup["lote"], fecha=date.today(), causa="Timpanismo")
    Venta.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        cabezas=50,
        kilos=Decimal("15000"),
        precio_kg=Decimal("50.00"),
    )
    setup["lote"].refresh_from_db()
    assert setup["lote"].cabezas_muertas == 2
    assert setup["lote"].cabezas_vendidas == 50
    assert setup["lote"].cabezas_actuales == 200 - 2 - 50  # = 148


def test_mortalidad_pct(setup):
    from apps.cierre.models import Muerte

    Muerte.objects.create(lote=setup["lote"], fecha=date.today(), causa="X")
    Muerte.objects.create(lote=setup["lote"], fecha=date.today(), causa="Y")
    setup["lote"].refresh_from_db()
    # 2 / 200 = 1%
    assert setup["lote"].mortalidad_pct == Decimal("1")


def test_ingreso_total_ventas_suma(setup):
    from apps.cierre.models import Venta

    Venta.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        cabezas=100,
        kilos=Decimal("30000"),
        precio_kg=Decimal("50"),
    )
    Venta.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        cabezas=100,
        kilos=Decimal("31000"),
        precio_kg=Decimal("52"),
    )
    setup["lote"].refresh_from_db()
    expected = Decimal("30000") * Decimal("50") + Decimal("31000") * Decimal("52")
    assert setup["lote"].ingreso_total_ventas == expected


@pytest.mark.django_db(transaction=True)
def test_admin_registra_muerte(client, admin_e, setup):
    from apps.cierre.models import Muerte

    client.force_login(admin_e)
    response = client.post(
        reverse("cierre:registrar_muerte"),
        {
            "lote": setup["lote"].pk,
            "fecha": date.today().isoformat(),
            "arete": "12345",
            "causa": "Neumonía",
            "peso_estimado": "320.00",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Muerte.objects.filter(lote=setup["lote"], arete="12345").exists()


@pytest.mark.django_db(transaction=True)
def test_admin_registra_venta(client, admin_e, setup):
    from apps.cierre.models import Venta

    client.force_login(admin_e)
    response = client.post(
        reverse("cierre:registrar_venta"),
        {
            "lote": setup["lote"].pk,
            "fecha": date.today().isoformat(),
            "cliente": "Rastro Norteño",
            "cabezas": 200,
            "kilos": "60000.00",
            "precio_kg": "52.00",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Venta.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_lista_muertes_y_ventas_carga(client, admin_e):
    client.force_login(admin_e)
    assert client.get(reverse("cierre:muertes")).status_code == 200
    assert client.get(reverse("cierre:ventas")).status_code == 200


@pytest.mark.django_db(transaction=True)
def test_anonimo_redirige(client):
    for url_name in ("cierre:muertes", "cierre:ventas", "cierre:registrar_muerte", "cierre:registrar_venta"):
        response = client.get(reverse(url_name))
        assert response.status_code == 302
