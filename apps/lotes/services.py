"""Lotes business operations."""

from datetime import date as date_type

from django.db import transaction

from .models import Lote, LoteFusion


@transaction.atomic
def fusionar(
    *,
    destino: Lote,
    origen: Lote,
    fecha_fusion: date_type,
    notas: str = "",
) -> LoteFusion:
    """Mueve todas las cabezas de `origen` hacia `destino`.

    Operación atómica:
      1. Crea el registro LoteFusion (trazabilidad).
      2. Suma cabezas en destino, anota observación con la fecha y folio.
      3. Marca origen inactivo, anota observación.

    Side-effect: el corral del origen queda libre porque su único lote activo
    deja de serlo.
    """
    if not origen.activo:
        raise ValueError("El lote origen ya está inactivo")
    if not destino.activo:
        raise ValueError("El lote destino ya está inactivo")
    if destino.pk == origen.pk:
        raise ValueError("No puedes fusionar un lote consigo mismo")

    cabezas = origen.cabezas_iniciales

    fusion = LoteFusion.objects.create(
        lote_destino=destino,
        lote_origen=origen,
        cabezas_movidas=cabezas,
        fecha_fusion=fecha_fusion,
        notas=notas,
    )

    destino.cabezas_iniciales += cabezas
    destino.observaciones = (
        (destino.observaciones or "")
        + f"\n[{fecha_fusion}] Fusión: +{cabezas} cab. del lote {origen.folio}."
    ).strip()
    destino.save()

    origen.activo = False
    origen.observaciones = (
        (origen.observaciones or "") + f"\n[{fecha_fusion}] Fusionado a lote {destino.folio}."
    ).strip()
    origen.save()

    return fusion
