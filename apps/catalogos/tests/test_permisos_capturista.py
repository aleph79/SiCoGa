"""Capturista en Spec A solo tiene view_*; no puede crear/editar/eliminar catálogos."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def capturista(db):
    group, _ = Group.objects.get_or_create(name="Capturista")
    view_perms = Permission.objects.filter(codename__startswith="view_")
    group.permissions.set(view_perms)
    u = User.objects.create_user(username="capt", email="c@x.com", password="p")
    u.groups.add(group)
    return u


CREATE_URLS = [
    "catalogos:tipocorral_create",
    "catalogos:tipoganado_create",
    "catalogos:tipoorigen_create",
    "catalogos:proveedor_create",
    "catalogos:corral_create",
    "catalogos:programareimplante_create",
]

LIST_URLS = [
    "catalogos:tipocorral_list",
    "catalogos:tipoganado_list",
    "catalogos:tipoorigen_list",
    "catalogos:proveedor_list",
    "catalogos:corral_list",
    "catalogos:programareimplante_list",
]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("urlname", CREATE_URLS)
def test_capturista_blocked_from_create_views(client, capturista, urlname):
    client.force_login(capturista)
    response = client.get(reverse(urlname))
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_capturista_can_view_listings(client, capturista):
    client.force_login(capturista)
    for url in LIST_URLS:
        assert client.get(reverse(url)).status_code == 200
