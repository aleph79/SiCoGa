"""Tests for User and Profile models."""

from django.contrib.auth import get_user_model

import pytest

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_user_email_must_be_unique():
    User.objects.create_user(username="dup_a", email="dup@example.com", password="p")
    with pytest.raises(Exception):
        User.objects.create_user(username="dup_b", email="dup@example.com", password="p")


def test_user_can_have_telefono():
    u = User.objects.create_user(
        username="con_tel", email="tel@x.com", password="p", telefono="555-123"
    )
    assert u.telefono == "555-123"


def test_user_str_returns_username():
    u = User.objects.create_user(username="anita", email="anita@x.com", password="p")
    assert str(u) == "anita"
