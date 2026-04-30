"""Capturista gana add/view sobre Muerte y Venta."""

from django.db import migrations

PERMISOS = [
    ("cierre", "add_muerte"),
    ("cierre", "view_muerte"),
    ("cierre", "add_venta"),
    ("cierre", "view_venta"),
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
        ("accounts", "0006_capturista_d3_perms"),
        ("cierre", "0001_initial"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
