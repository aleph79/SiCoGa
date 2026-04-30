"""Capturista gana add/view sobre Alimentacion, Medicacion y view de catálogos Formula/Medicamento."""

from django.db import migrations

PERMISOS = [
    ("cierre", "add_alimentacion"),
    ("cierre", "view_alimentacion"),
    ("cierre", "add_medicacion"),
    ("cierre", "view_medicacion"),
    ("catalogos", "view_formula"),
    ("catalogos", "view_medicamento"),
]


def forwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    capturista, _ = Group.objects.get_or_create(name="Capturista")
    perms = Permission.objects.filter(
        content_type__app_label__in={a for a, _ in PERMISOS},
        codename__in={c for _, c in PERMISOS},
    )
    capturista.permissions.add(*perms)


def backwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    capturista = Group.objects.filter(name="Capturista").first()
    if not capturista:
        return
    perms = Permission.objects.filter(codename__in={c for _, c in PERMISOS})
    capturista.permissions.remove(*perms)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_capturista_cierre_perms"),
        ("cierre", "0002_alimentacion_historicalalimentacion_and_more"),
        ("catalogos", "0015_seed_formulas"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
