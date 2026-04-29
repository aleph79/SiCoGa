"""Tests for abstract models. Uses a temporary concrete model declared in test."""

from django.db import connection, models

import pytest

from apps.core.models import AuditableModel, TimeStampedModel


class _ConcreteTimeStamped(TimeStampedModel):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "core"


class _ConcreteAuditable(AuditableModel):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "core"


@pytest.fixture(scope="module", autouse=True)
def create_test_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS `core__concretetimestamped` ("
                "  `id` bigint NOT NULL AUTO_INCREMENT,"
                "  `created_at` datetime(6) NOT NULL,"
                "  `updated_at` datetime(6) NOT NULL,"
                "  `name` varchar(20) NOT NULL,"
                "  PRIMARY KEY (`id`)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS `core__concreteauditable` ("
                "  `id` bigint NOT NULL AUTO_INCREMENT,"
                "  `created_at` datetime(6) NOT NULL,"
                "  `updated_at` datetime(6) NOT NULL,"
                "  `activo` tinyint(1) NOT NULL DEFAULT 1,"
                "  `name` varchar(20) NOT NULL,"
                "  PRIMARY KEY (`id`)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
    yield
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS `core__concreteauditable`")
            cursor.execute("DROP TABLE IF EXISTS `core__concretetimestamped`")


@pytest.mark.django_db
def test_timestamped_sets_created_and_updated():
    obj = _ConcreteTimeStamped.objects.create(name="x")
    assert obj.created_at is not None
    assert obj.updated_at is not None


@pytest.mark.django_db
def test_auditable_default_activo_is_true():
    obj = _ConcreteAuditable.objects.create(name="x")
    assert obj.activo is True


@pytest.mark.django_db
def test_auditable_inherits_timestamps():
    obj = _ConcreteAuditable.objects.create(name="x")
    assert obj.created_at is not None
    assert obj.updated_at is not None
