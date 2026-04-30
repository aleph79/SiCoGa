"""Capturista gana add/view sobre Reimplante e Implante."""

from django.db import migrations

PERMISOS = [
    ("operacion", "add_reimplante"),
    ("operacion", "view_reimplante"),
    ("catalogos", "view_implante"),
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
        ("accounts", "0003_capturista_lotes_perms"),
        ("operacion", "0001_initial"),
        ("catalogos", "0012_seed_implantes"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
