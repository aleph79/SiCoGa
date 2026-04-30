"""Capturista gana add/view sobre Transicion y EntradaZilpaterol."""

from django.db import migrations

PERMISOS = [
    ("operacion", "add_transicion"),
    ("operacion", "view_transicion"),
    ("operacion", "add_entradazilpaterol"),
    ("operacion", "view_entradazilpaterol"),
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
        ("accounts", "0004_capturista_operacion_perms"),
        ("operacion", "0002_entradazilpaterol_historicalentradazilpaterol_and_more"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
