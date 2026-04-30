"""Tests para Pesaje y su efecto sobre Lote.peso_actual_proyectado."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_p(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_p", email="ap@x.com", password="p", is_staff=True
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
        clave="CL-PSJ", nombre="PSJ", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-PSJ",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=30),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote, "corral": c, "macho": macho}


def test_pesaje_str(setup):
    from apps.operacion.models import Pesaje

    p = Pesaje.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=10),
        peso_promedio=Decimal("295.50"),
        cabezas_pesadas=200,
    )
    assert "CH-PSJ" in str(p)
    assert "295.50" in str(p)


def test_proyeccion_sin_pesaje_usa_peso_inicial(setup):
    """Sin pesajes, peso_actual_proyectado parte de peso_inicial."""
    lote = setup["lote"]
    # 30 días * 1.30 = 39, + 250 = 289
    assert lote.peso_actual_proyectado == Decimal("289.00")


def test_proyeccion_con_pesaje_usa_pesaje(setup):
    """Con un pesaje intermedio, la proyección parte del pesaje."""
    from apps.operacion.models import Pesaje

    Pesaje.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=10),
        peso_promedio=Decimal("280.00"),
        cabezas_pesadas=200,
    )
    setup["lote"].refresh_from_db()
    # 10 días desde el pesaje * 1.30 = 13, + 280 = 293
    assert setup["lote"].peso_actual_proyectado == Decimal("293.00")


def test_proyeccion_usa_pesaje_mas_reciente(setup):
    """Si hay varios pesajes, usa el más reciente."""
    from apps.operacion.models import Pesaje

    Pesaje.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=20),
        peso_promedio=Decimal("270.00"),
        cabezas_pesadas=200,
    )
    Pesaje.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=5),
        peso_promedio=Decimal("295.00"),
        cabezas_pesadas=200,
    )
    setup["lote"].refresh_from_db()
    # Usa el de hace 5 días: 5 * 1.30 = 6.5, + 295 = 301.5
    assert setup["lote"].peso_actual_proyectado == Decimal("301.50")


@pytest.mark.django_db(transaction=True)
def test_admin_registra_pesaje(client, admin_p, setup):
    from apps.operacion.models import Pesaje

    client.force_login(admin_p)
    response = client.post(
        reverse("operacion:registrar_pesaje"),
        {
            "lote": setup["lote"].pk,
            "fecha": date.today().isoformat(),
            "peso_promedio": "300.00",
            "cabezas_pesadas": 200,
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Pesaje.objects.filter(lote=setup["lote"]).exists()


@pytest.mark.django_db(transaction=True)
def test_lista_pesajes_carga(client, admin_p, setup):
    client.force_login(admin_p)
    response = client.get(reverse("operacion:pesajes"))
    assert response.status_code == 200
    # Lote CH-PSJ debe aparecer en "sin pesaje reciente"
    assert b"CH-PSJ" in response.content


@pytest.mark.django_db(transaction=True)
def test_lote_con_pesaje_reciente_no_alerta(client, admin_p, setup):
    """Si el lote tiene pesaje en últimos 30 días, no aparece en la sección 'sin pesaje'."""
    from apps.operacion.models import Pesaje

    Pesaje.objects.create(
        lote=setup["lote"],
        fecha=date.today() - timedelta(days=5),
        peso_promedio=Decimal("280.00"),
        cabezas_pesadas=200,
    )
    client.force_login(admin_p)
    response = client.get(reverse("operacion:pesajes"))
    assert response.status_code == 200
    sin_pesaje_section = response.content.split(b"Pesajes registrados")[0]
    assert b"CH-PSJ" not in sin_pesaje_section
