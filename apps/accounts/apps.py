from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Cuentas"

    def ready(self):
        from django.db.models.signals import post_migrate

        from . import signals  # noqa: F401

        post_migrate.connect(_sync_group_permissions, sender=self)


def _sync_group_permissions(sender, **kwargs):
    """Keep permission groups in sync after every migrate.

    - Administrador: all permissions.
    - Solo Lectura: only view_* permissions.

    We explicitly call create_permissions first so that permissions for newly
    applied migrations (e.g. a new model) exist before we try to assign them.
    """
    from django.apps import apps as django_apps
    from django.contrib.auth.management import create_permissions
    from django.contrib.auth.models import Group, Permission

    # Ensure all permissions are created for every installed app before we sync.
    for app_config in django_apps.get_app_configs():
        create_permissions(app_config, verbosity=0)

    admin_group = Group.objects.filter(name="Administrador").first()
    if admin_group is not None:
        admin_group.permissions.set(Permission.objects.all())

    lectura_group = Group.objects.filter(name="Solo Lectura").first()
    if lectura_group is not None:
        view_perms = Permission.objects.filter(codename__startswith="view_")
        lectura_group.permissions.set(view_perms)
