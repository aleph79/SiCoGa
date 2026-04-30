"""Tests for TipoOrigen CRUD and behavior."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_user_21(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin21", email="admin21@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def lectura_user_21(db):
    group, _ = Group.objects.get_or_create(name="Solo Lectura")
    view_perms = Permission.objects.filter(codename__startswith="view_")
    group.permissions.set(view_perms)
    u = User.objects.create_user(username="lectura21", email="lectura21@x.com", password="p")
    u.groups.add(group)
    return u


def test_tipoorigen_str_returns_nombre():
    from apps.catalogos.models import TipoOrigen

    t = TipoOrigen.objects.create(nombre="Compra")
    assert str(t) == "Compra"


@pytest.mark.django_db(transaction=True)
def test_tipoorigen_nombre_unique():
    from apps.catalogos.models import TipoOrigen

    TipoOrigen.objects.create(nombre="Propio")
    with pytest.raises(Exception):
        TipoOrigen.objects.create(nombre="Propio")


def test_tipoorigen_history_records_changes():
    from apps.catalogos.models import TipoOrigen

    t = TipoOrigen.objects.create(nombre="X")
    t.nombre = "Y"
    t.save()
    assert t.history.count() == 2


def test_tipoorigen_list_requires_login(client):
    response = client.get(reverse("catalogos:tipoorigen_list"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_admin_can_access_list(client, admin_user_21):
    client.force_login(admin_user_21)
    response = client.get(reverse("catalogos:tipoorigen_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_lectura_can_view_but_not_create(client, lectura_user_21):
    client.force_login(lectura_user_21)
    assert client.get(reverse("catalogos:tipoorigen_list")).status_code == 200
    assert client.get(reverse("catalogos:tipoorigen_create")).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_admin_can_create_tipoorigen(client, admin_user_21):
    client.force_login(admin_user_21)
    response = client.post(
        reverse("catalogos:tipoorigen_create"),
        {"nombre": "Subasta", "activo": "on"},
        follow=True,
    )
    assert response.status_code == 200
    from apps.catalogos.models import TipoOrigen

    assert TipoOrigen.objects.filter(nombre="Subasta").exists()


@pytest.mark.django_db(transaction=True)
def test_soft_delete_sets_activo_false(client, admin_user_21):
    from apps.catalogos.models import TipoOrigen

    t = TipoOrigen.objects.create(nombre="Tmp")
    client.force_login(admin_user_21)
    client.post(reverse("catalogos:tipoorigen_delete", args=[t.pk]))
    t.refresh_from_db()
    assert t.activo is False
