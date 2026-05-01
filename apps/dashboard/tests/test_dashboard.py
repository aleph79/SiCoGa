"""Tests para el Dashboard ejecutivo."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_f(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_f", email="af@x.com", password="p", is_staff=True
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
    c1 = Corral.objects.create(
        clave="CL-DA1", nombre="Da1", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    c2 = Corral.objects.create(
        clave="CL-DA2", nombre="Da2", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    Lote.objects.create(
        folio="CH-DA1",
        corral=c1,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=200),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    Lote.objects.create(
        folio="CH-DA2",
        corral=c2,
        tipo_ganado=macho,
        cabezas_iniciales=180,
        fecha_inicio=date.today() - timedelta(days=50),
        peso_inicial_promedio=Decimal("280.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.40"),
    )
    return {"c1": c1, "c2": c2, "macho": macho}


@pytest.mark.django_db(transaction=True)
def test_anonimo_redirige(client):
    response = client.get(reverse("dashboard:ejecutivo"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_dashboard_carga(client, admin_f, setup):
    client.force_login(admin_f)
    response = client.get(reverse("dashboard:ejecutivo"))
    assert response.status_code == 200
    # Bloques principales presentes
    assert b"Dashboard ejecutivo" in response.content
    assert b"Salidas proyectadas" in response.content
    assert b"Mapa de corrales" in response.content
    assert b"Indicadores operativos" in response.content
    assert b"Actividad reciente" in response.content


@pytest.mark.django_db(transaction=True)
def test_mapa_muestra_corrales(client, admin_f, setup):
    client.force_login(admin_f)
    response = client.get(reverse("dashboard:ejecutivo"))
    assert response.status_code == 200
    assert b"CL-DA1" in response.content
    assert b"CL-DA2" in response.content


@pytest.mark.django_db(transaction=True)
def test_inventario_total_correcto(client, admin_f, setup):
    """200 + 180 = 380 cabezas en lotes activos."""
    client.force_login(admin_f)
    response = client.get(reverse("dashboard:ejecutivo"))
    assert b"380" in response.content


@pytest.mark.django_db(transaction=True)
def test_actividad_reciente_aparece_en_dashboard(client, admin_f, setup):
    """Un reimplante reciente debe aparecer en la sección actividad."""
    from apps.catalogos.models import Implante
    from apps.lotes.models import Lote
    from apps.operacion.models import Reimplante

    implante = Implante.objects.get_or_create(nombre="Test Imp")[0]
    lote = Lote.objects.get(folio="CH-DA1")
    Reimplante.objects.create(
        lote=lote,
        numero=1,
        fecha_aplicada=date.today() - timedelta(days=2),
        implante=implante,
        cabezas_aplicadas=200,
    )

    client.force_login(admin_f)
    response = client.get(reverse("dashboard:ejecutivo"))
    assert b"Reimplante" in response.content
    assert b"CH-DA1" in response.content
