"""Seed common fórmulas alimenticias del Excel del cliente."""

from django.db import migrations

NOMBRES = [
    "F1 sin melaza",
    "F1 con melaza",
    "Transición F1/F3",
    "F3 SSS",
    "F3 SZ + Zilpaterol",
]


def forwards(apps, schema_editor):
    Formula = apps.get_model("catalogos", "Formula")
    for nombre in NOMBRES:
        Formula.objects.get_or_create(nombre=nombre)


def backwards(apps, schema_editor):
    Formula = apps.get_model("catalogos", "Formula")
    Formula.objects.filter(nombre__in=NOMBRES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogos", "0014_formula_medicamento_historicalformula_and_more"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
