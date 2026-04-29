"""Smoke tests for project bootstrap."""
import django


def test_django_version_is_5_1():
    assert django.get_version().startswith("5.1")


def test_settings_loaded():
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "es-mx"
    assert settings.TIME_ZONE == "America/Mexico_City"
    assert settings.USE_TZ is True
