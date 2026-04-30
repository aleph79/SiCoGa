"""Tests for the seeded groups."""

from django.contrib.auth.models import Group

import pytest


@pytest.mark.django_db
def test_four_groups_exist():
    expected = {"Administrador", "Gerente", "Capturista", "Solo Lectura"}
    actual = set(Group.objects.values_list("name", flat=True))
    assert expected.issubset(actual)


@pytest.mark.django_db
def test_solo_lectura_has_only_view_permissions():
    g = Group.objects.get(name="Solo Lectura")
    perms = g.permissions.values_list("codename", flat=True)
    assert all(p.startswith("view_") for p in perms)


@pytest.mark.django_db
def test_administrador_has_all_permissions():
    from django.contrib.auth.models import Permission

    g = Group.objects.get(name="Administrador")
    assert g.permissions.count() == Permission.objects.count()
