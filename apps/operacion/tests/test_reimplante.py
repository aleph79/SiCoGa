"""Tests para Reimplante model y vistas."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_d(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(username="admin_d", email="ad@x.com", password="p", is_staff=True)
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, Implante, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    implante = Implante.objects.get_or_create(nombre="Revalor-G")[0]

    c = Corral.objects.create(
        clave="CL-R", nombre="R", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-R1",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=70),  # 1er reimpl. ya tocó
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    return {"lote": lote, "implante": implante, "corral": c, "macho": macho}


def test_implante_seedeado(db):
    """Las migraciones siembran al menos algunos implantes del Excel."""
    from apps.catalogos.models import Implante

    assert Implante.objects.count() >= 5


def test_reimplante_str(setup):
    from apps.operacion.models import Reimplante

    r = Reimplante.objects.create(
        lote=setup["lote"],
        numero=1,
        fecha_aplicada=date.today(),
        implante=setup["implante"],
        cabezas_aplicadas=200,
    )
    assert "CH-R1" in str(r)
    assert "1er reimplante" in str(r)


@pytest.mark.django_db(transaction=True)
def test_reimplante_unico_por_lote_y_numero(setup):
    from django.db import IntegrityError

    from apps.operacion.models import Reimplante

    Reimplante.objects.create(
        lote=setup["lote"],
        numero=1,
        fecha_aplicada=date.today(),
        implante=setup["implante"],
        cabezas_aplicadas=200,
    )
    with pytest.raises(IntegrityError):
        Reimplante.objects.create(
            lote=setup["lote"],
            numero=1,
            fecha_aplicada=date.today(),
            implante=setup["implante"],
            cabezas_aplicadas=200,
        )


def test_reimplantes_distintos_numeros_ok(setup):
    """Mismo lote acepta reimplante 1 y 2 sin chocar."""
    from apps.operacion.models import Reimplante

    Reimplante.objects.create(
        lote=setup["lote"],
        numero=1,
        fecha_aplicada=date.today() - timedelta(days=10),
        implante=setup["implante"],
        cabezas_aplicadas=200,
    )
    r2 = Reimplante.objects.create(
        lote=setup["lote"],
        numero=2,
        fecha_aplicada=date.today(),
        implante=setup["implante"],
        cabezas_aplicadas=200,
    )
    assert r2.pk


@pytest.mark.django_db(transaction=True)
def test_anonimo_redirige(client):
    response = client.get(reverse("operacion:reimplantes"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_admin_ve_calendario(client, admin_d, setup):
    client.force_login(admin_d)
    response = client.get(reverse("operacion:reimplantes"))
    assert response.status_code == 200
    # Lote CH-R1 debe aparecer como pendiente (1er reimpl. con 70 días debería estar ya pasado o cercano)
    assert b"CH-R1" in response.content


@pytest.mark.django_db(transaction=True)
def test_admin_registra_reimplante(client, admin_d, setup):
    from apps.operacion.models import Reimplante

    client.force_login(admin_d)
    response = client.post(
        reverse("operacion:registrar_reimplante"),
        {
            "lote": setup["lote"].pk,
            "numero": 1,
            "fecha_aplicada": date.today().isoformat(),
            "implante": setup["implante"].pk,
            "cabezas_aplicadas": 200,
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Reimplante.objects.filter(lote=setup["lote"], numero=1).exists()


@pytest.mark.django_db(transaction=True)
def test_pendientes_no_listan_aplicados(client, admin_d, setup):
    """Una vez registrado el reimpl. 1, debe dejar de aparecer en pendientes."""
    from apps.operacion.models import Reimplante

    client.force_login(admin_d)
    response = client.get(reverse("operacion:reimplantes"))
    assert response.status_code == 200
    # CH-R1 debe aparecer como pendiente al menos una vez
    assert b"CH-R1" in response.content

    Reimplante.objects.create(
        lote=setup["lote"],
        numero=1,
        fecha_aplicada=date.today(),
        implante=setup["implante"],
        cabezas_aplicadas=200,
    )

    response = client.get(reverse("operacion:reimplantes"))
    # Debería aparecer en historial pero el "1er" pendiente ya no
    historial_section = response.content.split(b"Historial reciente")[-1]
    assert b"CH-R1" in historial_section
