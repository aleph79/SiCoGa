"""Tests for Corral CRUD with capacity properties."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_user_23(db):
    g, _ = Group.objects.get_or_create(name="Administrador")
    g.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin23", email="admin23@x.com", password="p", is_staff=True
    )
    u.groups.add(g)
    return u


def test_disponibilidad_equals_capacidad_when_empty(db):
    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="EngordaTest")
    c = Corral.objects.create(clave="C25", nombre="Corral 25", tipo_corral=tc, capacidad_maxima=200)
    assert c.ocupacion_actual == 0
    assert c.disponibilidad == 200


@pytest.mark.django_db(transaction=True)
def test_corral_clave_unique():
    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="EngordaTest2")
    Corral.objects.create(clave="C99", nombre="A", tipo_corral=tc, capacidad_maxima=100)
    with pytest.raises(Exception):
        Corral.objects.create(clave="C99", nombre="B", tipo_corral=tc, capacidad_maxima=200)


def test_capacidad_must_be_positive(db):
    from django.core.exceptions import ValidationError

    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="EngordaTest3")
    c = Corral(clave="C100", nombre="A", tipo_corral=tc, capacidad_maxima=0)
    with pytest.raises(ValidationError):
        c.full_clean()


@pytest.mark.django_db(transaction=True)
def test_admin_creates_corral(client, admin_user_23):
    from apps.catalogos.models import Corral, TipoCorral

    tc = TipoCorral.objects.create(nombre="EngordaTest4")
    client.force_login(admin_user_23)
    response = client.post(
        reverse("catalogos:corral_create"),
        {
            "clave": "C25T",
            "nombre": "Corral 25",
            "tipo_corral": tc.pk,
            "capacidad_maxima": 200,
            "activo": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Corral.objects.filter(clave="C25T").exists()
