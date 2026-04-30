from django.db import migrations

NOMBRES = ["Macho", "Hembra", "Vaca"]


def forwards(apps, schema_editor):
    TipoGanado = apps.get_model("catalogos", "TipoGanado")
    for nombre in NOMBRES:
        TipoGanado.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    TipoGanado = apps.get_model("catalogos", "TipoGanado")
    TipoGanado.objects.filter(nombre__in=NOMBRES).delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "0007_seed_tipo_corral")]
    operations = [migrations.RunPython(forwards, backwards)]
