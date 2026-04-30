"""Seed the four standard groups with their permissions."""

from django.contrib.auth.management import create_permissions
from django.db import migrations


GROUP_DEFINITIONS = {
    "Administrador": "ALL",
    "Gerente": ["view"],
    "Capturista": ["view"],
    "Solo Lectura": ["view"],
}


def seed_groups(apps, schema_editor):
    # Ensure all permissions exist before we reference them (they are normally
    # created by the post_migrate signal, which fires after all migrations run,
    # so we must trigger creation explicitly here).
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for name, scope in GROUP_DEFINITIONS.items():
        group = Group.objects.filter(name=name).first()
        if group is None:
            group = Group.objects.create(name=name)
        if scope == "ALL":
            group.permissions.set(Permission.objects.all())
        else:
            perms = Permission.objects.filter(codename__regex=r"^(" + "|".join(scope) + r")_")
            group.permissions.set(perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=GROUP_DEFINITIONS.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(seed_groups, remove_groups),
    ]
