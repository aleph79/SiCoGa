"""Add 'Potrero' to TipoCorral so that pasture-based ganado can be tracked."""

from django.db import migrations


def forwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    TipoCorral.objects.get_or_create(nombre="Potrero")


def backwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    TipoCorral.objects.filter(nombre="Potrero").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogos", "0012_seed_implantes"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
