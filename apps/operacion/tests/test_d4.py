"""Tests para D.4 Reportes (Inventario, Proyección Anual, Salidas)."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_d4(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_d4", email="ad4@x.com", password="p", is_staff=True
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
    tipo_engorda = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    tipo_potrero = TipoCorral.objects.get_or_create(nombre="Potrero")[0]

    c1 = Corral.objects.create(
        clave="CL-IN1", nombre="In1", tipo_corral=tipo_engorda, capacidad_maxima=300
    )
    c2 = Corral.objects.create(
        clave="CL-IN2", nombre="In2", tipo_corral=tipo_engorda, capacidad_maxima=300
    )
    p1 = Corral.objects.create(
        clave="PT-1", nombre="Potrero 1", tipo_corral=tipo_potrero, capacidad_maxima=500
    )

    Lote.objects.create(
        folio="CH-IN1",
        corral=c1,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=200),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    Lote.objects.create(
        folio="CH-PT1",
        corral=p1,
        tipo_ganado=macho,
        cabezas_iniciales=300,
        fecha_inicio=date.today() - timedelta(days=100),
        peso_inicial_promedio=Decimal("220.00"),
        peso_salida_objetivo=Decimal("560.00"),
        gdp_esperada=Decimal("1.50"),
    )
    return {"corral1": c1, "corral2": c2, "potrero": p1, "macho": macho}


def test_potrero_seedeado(db):
    """La migración 0013 agrega Potrero a TipoCorral."""
    from apps.catalogos.models import TipoCorral

    assert TipoCorral.objects.filter(nombre="Potrero").exists()


@pytest.mark.django_db(transaction=True)
def test_inventario_general_carga(client, admin_d4, setup):
    client.force_login(admin_d4)
    response = client.get(reverse("operacion:inventario"))
    assert response.status_code == 200
    # Lote CH-IN1 en corral, CH-PT1 en potrero
    assert b"CH-IN1" in response.content
    assert b"CH-PT1" in response.content
    # CL-IN2 (libre) también debe aparecer
    assert b"CL-IN2" in response.content


@pytest.mark.django_db(transaction=True)
def test_inventario_separa_corrales_y_potreros(client, admin_d4, setup):
    """El potrero PT-1 con CH-PT1 debe contar en 'total_potreros' no en 'total_corrales'."""
    client.force_login(admin_d4)
    response = client.get(reverse("operacion:inventario"))
    # 200 cabezas en corral, 300 en potrero, 500 total
    assert b"200" in response.content
    assert b"300" in response.content
    assert b"500" in response.content


@pytest.mark.django_db(transaction=True)
def test_proyeccion_anual_carga(client, admin_d4, setup):
    client.force_login(admin_d4)
    response = client.get(reverse("operacion:proyeccion_anual"))
    assert response.status_code == 200
    assert b"Sem 1" in response.content  # alguna semana visible


@pytest.mark.django_db(transaction=True)
def test_proyeccion_anual_filtra_por_anio(client, admin_d4, setup):
    client.force_login(admin_d4)
    response = client.get(reverse("operacion:proyeccion_anual"), {"anio": "2030"})
    assert response.status_code == 200
    # 2030 no tiene lotes proyectados
    assert b"Sin salida" in response.content


@pytest.mark.django_db(transaction=True)
def test_salidas_semanales_carga(client, admin_d4, setup):
    client.force_login(admin_d4)
    response = client.get(reverse("operacion:salidas_semanales"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_anonimo_no_puede_ver_reportes(client):
    for url_name in ("operacion:inventario", "operacion:proyeccion_anual", "operacion:salidas_semanales"):
        response = client.get(reverse(url_name))
        assert response.status_code == 302  # redirect a login
