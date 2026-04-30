"""Tests para Transicion y EntradaZilpaterol."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_d2(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_d2", email="ad2@x.com", password="p", is_staff=True
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
        clave="CL-D2X",
        nombre="D2X",
        tipo_corral=tipo_corral,
        capacidad_maxima=300,
    )
    lote = Lote.objects.create(
        folio="CH-D2X",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=30),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote, "corral": c, "macho": macho}


def test_transicion_str(setup):
    from apps.operacion.models import Transicion

    t = Transicion.objects.create(
        lote=setup["lote"],
        fecha=date.today(),
        de_fase="F1",
        a_fase="FT",
        proporcion="50/50",
    )
    assert "CH-D2X" in str(t)
    assert "F1→FT" in str(t)


@pytest.mark.django_db(transaction=True)
def test_admin_registra_transicion(client, admin_d2, setup):
    from apps.operacion.models import Transicion

    client.force_login(admin_d2)
    response = client.post(
        reverse("operacion:registrar_transicion"),
        {
            "lote": setup["lote"].pk,
            "fecha": date.today().isoformat(),
            "de_fase": "F1",
            "a_fase": "FT",
            "proporcion": "50/50",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Transicion.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_calendario_transiciones_carga(client, admin_d2, setup):
    client.force_login(admin_d2)
    response = client.get(reverse("operacion:transiciones"))
    assert response.status_code == 200


def test_zilp_str(setup):
    from apps.operacion.models import EntradaZilpaterol

    e = EntradaZilpaterol.objects.create(
        lote=setup["lote"], fecha_entrada=date.today() - timedelta(days=10)
    )
    assert "CH-D2X" in str(e)


def test_zilp_dias_y_listo(setup):
    from apps.operacion.models import EntradaZilpaterol

    e = EntradaZilpaterol.objects.create(
        lote=setup["lote"], fecha_entrada=date.today() - timedelta(days=40)
    )
    assert e.dias_en_zilpaterol == 40
    assert e.dias_restantes == 0
    assert e.listo_para_venta is True


def test_zilp_no_listo_aun(setup):
    from apps.operacion.models import EntradaZilpaterol

    e = EntradaZilpaterol.objects.create(
        lote=setup["lote"], fecha_entrada=date.today() - timedelta(days=20)
    )
    assert e.dias_restantes == 15
    assert e.listo_para_venta is False


def test_zilp_fecha_salida_proyectada(setup):
    from apps.operacion.models import EntradaZilpaterol

    e = EntradaZilpaterol.objects.create(
        lote=setup["lote"], fecha_entrada=date(2026, 4, 1)
    )
    assert e.fecha_salida_proyectada == date(2026, 4, 1) + timedelta(days=35)


@pytest.mark.django_db(transaction=True)
def test_admin_registra_entrada_zilp(client, admin_d2, setup):
    from apps.operacion.models import EntradaZilpaterol

    client.force_login(admin_d2)
    response = client.post(
        reverse("operacion:registrar_zilpaterol"),
        {
            "lote": setup["lote"].pk,
            "fecha_entrada": date.today().isoformat(),
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert EntradaZilpaterol.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_calendario_zilp_carga(client, admin_d2, setup):
    client.force_login(admin_d2)
    response = client.get(reverse("operacion:zilpaterol"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_zilp_es_one_to_one(setup):
    """Un lote solo puede tener una EntradaZilpaterol."""
    from django.db import IntegrityError

    from apps.operacion.models import EntradaZilpaterol

    EntradaZilpaterol.objects.create(
        lote=setup["lote"], fecha_entrada=date.today() - timedelta(days=10)
    )
    with pytest.raises(IntegrityError):
        EntradaZilpaterol.objects.create(
            lote=setup["lote"], fecha_entrada=date.today()
        )
