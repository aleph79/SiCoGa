"""Tests for TipoCorral CRUD and behavior."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_user(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin19", email="admin19@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def lectura_user(db):
    group, _ = Group.objects.get_or_create(name="Solo Lectura")
    view_perms = Permission.objects.filter(codename__startswith="view_")
    group.permissions.set(view_perms)
    u = User.objects.create_user(username="lectura19", email="lectura19@x.com", password="p")
    u.groups.add(group)
    return u


def test_tipocorral_str_returns_nombre():
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="Recepción")
    assert str(t) == "Recepción"


@pytest.mark.django_db(transaction=True)
def test_tipocorral_nombre_unique():
    from apps.catalogos.models import TipoCorral

    TipoCorral.objects.create(nombre="Engorda")
    with pytest.raises(Exception):
        TipoCorral.objects.create(nombre="Engorda")


def test_tipocorral_history_records_changes():
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="X")
    t.nombre = "Y"
    t.save()
    assert t.history.count() == 2


def test_tipocorral_list_requires_login(client):
    response = client.get(reverse("catalogos:tipocorral_list"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_admin_can_access_list(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("catalogos:tipocorral_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_lectura_can_view_but_not_create(client, lectura_user):
    client.force_login(lectura_user)
    assert client.get(reverse("catalogos:tipocorral_list")).status_code == 200
    assert client.get(reverse("catalogos:tipocorral_create")).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_admin_can_create_tipocorral(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("catalogos:tipocorral_create"),
        {"nombre": "Zilpaterol", "activo": "on"},
        follow=True,
    )
    assert response.status_code == 200
    from apps.catalogos.models import TipoCorral

    assert TipoCorral.objects.filter(nombre="Zilpaterol").exists()


@pytest.mark.django_db(transaction=True)
def test_soft_delete_sets_activo_false(client, admin_user):
    from apps.catalogos.models import TipoCorral

    t = TipoCorral.objects.create(nombre="Tmp")
    client.force_login(admin_user)
    client.post(reverse("catalogos:tipocorral_delete", args=[t.pk]))
    t.refresh_from_db()
    assert t.activo is False
