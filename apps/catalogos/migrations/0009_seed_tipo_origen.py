from django.db import migrations

NOMBRES = ["Corral", "Potrero"]


def forwards(apps, schema_editor):
    TipoOrigen = apps.get_model("catalogos", "TipoOrigen")
    for nombre in NOMBRES:
        TipoOrigen.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    TipoOrigen = apps.get_model("catalogos", "TipoOrigen")
    TipoOrigen.objects.filter(nombre__in=NOMBRES).delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "0008_seed_tipo_ganado")]
    operations = [migrations.RunPython(forwards, backwards)]
