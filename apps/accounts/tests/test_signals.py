"""Tests for accounts signals."""

from django.contrib.auth import get_user_model

from apps.accounts.models import Profile

User = get_user_model()


def test_profile_created_automatically_on_user_create():
    u = User.objects.create_user(username="auto", email="a@x.com", password="p")
    assert Profile.objects.filter(user=u).exists()


def test_profile_not_recreated_on_save():
    u = User.objects.create_user(username="once", email="o@x.com", password="p")
    u.first_name = "Cambio"
    u.save()
    assert Profile.objects.filter(user=u).count() == 1
