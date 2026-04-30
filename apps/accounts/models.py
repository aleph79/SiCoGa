"""User and Profile models."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """Custom user with unique email and phone field."""

    email = models.EmailField(unique=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username


class Profile(TimeStampedModel):
    """Per-user profile with optional avatar and job title."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    puesto = models.CharField(max_length=80, blank=True, verbose_name="Puesto")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Avatar")

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.user.username}"
