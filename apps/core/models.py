"""Abstract base models for SiCoGa."""

from django.db import models


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        abstract = True


class AuditableModel(TimeStampedModel):
    """Adds soft-delete via `activo`. Combine with HistoricalRecords() in concrete models."""

    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
