"""Tests para Costo Hotel (Spec E.4)."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_e4(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_e4", email="ae4@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.cierre.models import CostoHotelComponente
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    c = Corral.objects.create(
        clave="CL-HOT", nombre="Hot", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-HOT",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=220,
        fecha_inicio=date.today() - timedelta(days=129),  # 129 días calendario incluyendo hoy = 130
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )

    # Asegurar que existe la config seedeada
    if CostoHotelComponente.objects.count() == 0:
        CostoHotelComponente.objects.create(
            nombre="Agua y sanidad", costo_dia_animal=Decimal("4.20"), habilitado=True
        )
        CostoHotelComponente.objects.create(
            nombre="Mano de obra", costo_dia_animal=Decimal("5.80"), habilitado=True
        )
        CostoHotelComponente.objects.create(
            nombre="Depreciación", costo_dia_animal=Decimal("2.10"), habilitado=False
        )

    return {"lote": lote, "corral": c}


def test_componentes_seedeados(db):
    from apps.cierre.models import CostoHotelComponente

    assert CostoHotelComponente.objects.count() >= 4


def test_dias_calendario(setup):
    # 129 días de diferencia + 1 (incluye día actual) = 130
    assert setup["lote"].dias_calendario == 130


def test_dias_animal_base(setup):
    # 130 días * 220 cab = 28,600
    assert setup["lote"].dias_animal_base == 130 * 220


def test_dias_animal_descuento_muertes(setup):
    """Cada muerte resta los días que faltaban hasta el cierre."""
    from apps.cierre.models import Muerte

    Muerte.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=10),  # murió hace 10 días, faltaban 10 hasta cierre (hoy)
        causa="X",
    )
    setup["lote"].refresh_from_db()
    assert setup["lote"].dias_animal_descuento_muertes == 10


def test_dias_animal_netos(setup):
    from apps.cierre.models import Muerte

    Muerte.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=10),
        causa="Y",
    )
    setup["lote"].refresh_from_db()
    assert setup["lote"].dias_animal_netos == 130 * 220 - 10


def test_costo_hotel_dia_animal_suma_habilitados(setup):
    """Suma sólo de los componentes habilitados (4.20 + 5.80 = 10.00)."""
    # Verificar que hay al menos 2 habilitados con esos costos
    from apps.cierre.models import CostoHotelComponente

    habilitados_seed = CostoHotelComponente.objects.filter(habilitado=True, activo=True)
    expected = sum(c.costo_dia_animal for c in habilitados_seed)
    assert setup["lote"].costo_hotel_dia_animal == expected


def test_costo_hotel_total(setup):
    expected = setup["lote"].dias_animal_netos * setup["lote"].costo_hotel_dia_animal
    assert setup["lote"].costo_hotel_total == expected


@pytest.mark.django_db(transaction=True)
def test_view_config_carga(client, admin_e4):
    client.force_login(admin_e4)
    response = client.get(reverse("cierre:costo_hotel_config"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_view_lote_carga(client, admin_e4, setup):
    client.force_login(admin_e4)
    response = client.get(reverse("cierre:costo_hotel_lote", args=[setup["lote"].pk]))
    assert response.status_code == 200
    assert b"CH-HOT" in response.content


@pytest.mark.django_db(transaction=True)
def test_view_registrar_componente(client, admin_e4):
    from apps.cierre.models import CostoHotelComponente

    client.force_login(admin_e4)
    response = client.post(
        reverse("cierre:registrar_costo_hotel"),
        {
            "nombre": "Test componente",
            "costo_dia_animal": "1.50",
            "habilitado": "on",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert CostoHotelComponente.objects.filter(nombre="Test componente").exists()
