from django.db import migrations

NOMBRES = ["Recepción", "Engorda", "Zilpaterol"]


def forwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    for nombre in NOMBRES:
        TipoCorral.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    TipoCorral = apps.get_model("catalogos", "TipoCorral")
    TipoCorral.objects.filter(nombre__in=NOMBRES).delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "0006_historicalprogramareimplante_programareimplante")]
    operations = [migrations.RunPython(forwards, backwards)]
