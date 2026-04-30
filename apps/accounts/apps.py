from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Cuentas"

    def ready(self):
        from django.db.models.signals import post_migrate

        from . import signals  # noqa: F401

        post_migrate.connect(_sync_administrador_permissions, sender=self)


def _sync_administrador_permissions(sender, **kwargs):
    """Keep the Administrador group in sync with all permissions after migrate."""
    from django.contrib.auth.models import Group, Permission

    group = Group.objects.filter(name="Administrador").first()
    if group is not None:
        group.permissions.set(Permission.objects.all())
