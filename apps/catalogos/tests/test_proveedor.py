"""Tests for Proveedor CRUD and behavior."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_user_22(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin22", email="admin22@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def lectura_user_22(db):
    group, _ = Group.objects.get_or_create(name="Solo Lectura")
    view_perms = Permission.objects.filter(codename__startswith="view_")
    group.permissions.set(view_perms)
    u = User.objects.create_user(username="lectura22", email="lectura22@x.com", password="p")
    u.groups.add(group)
    return u


def test_proveedor_str_returns_nombre():
    from apps.catalogos.models import Proveedor

    p = Proveedor.objects.create(nombre="Ganadería Norte")
    assert str(p) == "Ganadería Norte"


@pytest.mark.django_db(transaction=True)
def test_proveedor_nombre_unique():
    from apps.catalogos.models import Proveedor

    Proveedor.objects.create(nombre="Duplicado")
    with pytest.raises(Exception):
        Proveedor.objects.create(nombre="Duplicado")


def test_proveedor_history_records_changes():
    from apps.catalogos.models import Proveedor

    p = Proveedor.objects.create(nombre="X")
    p.nombre = "Y"
    p.save()
    assert p.history.count() == 2


def test_proveedor_list_requires_login(client):
    response = client.get(reverse("catalogos:proveedor_list"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_admin_can_access_list(client, admin_user_22):
    client.force_login(admin_user_22)
    response = client.get(reverse("catalogos:proveedor_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_lectura_can_view_but_not_create(client, lectura_user_22):
    client.force_login(lectura_user_22)
    assert client.get(reverse("catalogos:proveedor_list")).status_code == 200
    assert client.get(reverse("catalogos:proveedor_create")).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_admin_can_create_proveedor(client, admin_user_22):
    client.force_login(admin_user_22)
    response = client.post(
        reverse("catalogos:proveedor_create"),
        {"nombre": "Rancho Test", "activo": "on"},
        follow=True,
    )
    assert response.status_code == 200
    from apps.catalogos.models import Proveedor

    assert Proveedor.objects.filter(nombre="Rancho Test").exists()


@pytest.mark.django_db(transaction=True)
def test_soft_delete_sets_activo_false(client, admin_user_22):
    from apps.catalogos.models import Proveedor

    p = Proveedor.objects.create(nombre="Tmp")
    client.force_login(admin_user_22)
    client.post(reverse("catalogos:proveedor_delete", args=[p.pk]))
    p.refresh_from_db()
    assert p.activo is False
