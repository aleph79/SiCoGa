"""Seed Implante catalog from existing ProgramaReimplante values."""

from django.db import migrations


def forwards(apps, schema_editor):
    Implante = apps.get_model("catalogos", "Implante")
    Programa = apps.get_model("catalogos", "ProgramaReimplante")

    nombres = set()
    for p in Programa.objects.all():
        for f in (
            p.implante_inicial,
            p.reimplante_1,
            p.reimplante_2,
            p.reimplante_3,
            p.reimplante_4,
        ):
            if f and f.strip() and f.strip().upper() != "N/A":
                nombres.add(f.strip())

    for nombre in sorted(nombres):
        Implante.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    Implante = apps.get_model("catalogos", "Implante")
    Implante.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogos", "0011_implante_historicalimplante"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
