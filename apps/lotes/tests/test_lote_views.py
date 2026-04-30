"""Tests E2E para las vistas CRUD de Lote."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_b(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(username="admin_b", email="ab@x.com", password="p", is_staff=True)
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado

    ProgramaReimplante.objects.all().delete()
    return {
        "macho": TipoGanado.objects.get_or_create(nombre="Macho")[0],
        "corral": Corral.objects.create(
            clave="CL-V",
            nombre="View test",
            tipo_corral=TipoCorral.objects.get_or_create(nombre="Engorda")[0],
            capacidad_maxima=300,
        ),
    }


@pytest.mark.django_db(transaction=True)
def test_lote_list_anonymous_redirects_to_login(client):
    response = client.get(reverse("lotes:lote_list"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_admin_lista_lotes(client, admin_b):
    client.force_login(admin_b)
    response = client.get(reverse("lotes:lote_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_admin_crea_lote(client, admin_b, setup):
    from apps.lotes.models import Lote

    client.force_login(admin_b)
    response = client.post(
        reverse("lotes:lote_create"),
        {
            "folio": "CH-V1",
            "corral": setup["corral"].pk,
            "tipo_ganado": setup["macho"].pk,
            "cabezas_iniciales": "150",
            "fecha_inicio": "2026-04-30",
            "peso_inicial_promedio": "250.00",
            "peso_salida_objetivo": "580.00",
            "gdp_esperada": "1.30",
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Lote.objects.filter(folio="CH-V1").exists()


@pytest.mark.django_db(transaction=True)
def test_preview_proyeccion_devuelve_dias(client, admin_b, setup):
    client.force_login(admin_b)
    response = client.post(
        reverse("lotes:lote_preview"),
        {
            "tipo_ganado": setup["macho"].pk,
            "cabezas_iniciales": "200",
            "peso_inicial_promedio": "250.00",
            "peso_salida_objetivo": "580.00",
            "gdp_esperada": "1.30",
            "fecha_inicio": "2026-01-01",
        },
    )
    assert response.status_code == 200
    # 330 / 1.30 = 253
    assert b"253" in response.content


@pytest.mark.django_db(transaction=True)
def test_admin_soft_deletes_lote(client, admin_b, setup):
    from apps.lotes.models import Lote

    lote = Lote.objects.create(
        folio="CH-DEL",
        corral=setup["corral"],
        tipo_ganado=setup["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    client.force_login(admin_b)
    client.post(reverse("lotes:lote_delete", args=[lote.pk]))
    lote.refresh_from_db()
    assert lote.activo is False


@pytest.mark.django_db(transaction=True)
def test_corral_ocupacion_lote_inactivo_no_cuenta(setup):
    """Si el lote está inactivo, el corral está libre."""
    from apps.lotes.models import Lote

    lote = Lote.objects.create(
        folio="CH-OCC",
        corral=setup["corral"],
        tipo_ganado=setup["macho"],
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    # Corral.ocupacion_actual es 0 en Spec A; en Spec B no lo cambiamos todavía.
    # Pero verificamos que la query .lotes.filter(activo=True) devuelve correctamente.
    assert setup["corral"].lotes.filter(activo=True).count() == 1
    lote.activo = False
    lote.save()
    assert setup["corral"].lotes.filter(activo=True).count() == 0
