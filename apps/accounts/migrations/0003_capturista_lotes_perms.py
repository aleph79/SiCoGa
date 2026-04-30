"""Capturista gana add/change/view sobre Lote y add/view sobre LoteFusion."""

from django.db import migrations

PERMISOS = [
    ("lotes", "add_lote"),
    ("lotes", "change_lote"),
    ("lotes", "view_lote"),
    ("lotes", "add_lotefusion"),
    ("lotes", "view_lotefusion"),
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
        ("accounts", "0002_seed_groups"),
        ("lotes", "0002_lotefusion"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
