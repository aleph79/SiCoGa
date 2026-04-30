"""Seed los 4 componentes default de Costo Hotel del dummy v4."""

from decimal import Decimal

from django.db import migrations

COMPONENTES = [
    ("Agua y sanidad", Decimal("4.20"), True),
    ("Mano de obra operativa", Decimal("5.80"), True),
    ("Depreciación instalaciones", Decimal("2.10"), False),
    ("Costos administrativos", Decimal("1.40"), False),
]


def forwards(apps, schema_editor):
    CostoHotelComponente = apps.get_model("cierre", "CostoHotelComponente")
    for nombre, costo, habilitado in COMPONENTES:
        CostoHotelComponente.objects.get_or_create(
            nombre=nombre,
            defaults={"costo_dia_animal": costo, "habilitado": habilitado},
        )


def backwards(apps, schema_editor):
    CostoHotelComponente = apps.get_model("cierre", "CostoHotelComponente")
    CostoHotelComponente.objects.filter(
        nombre__in=[n for n, _, _ in COMPONENTES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cierre", "0003_costohotelcomponente_historicalcostohotelcomponente"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
