from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Extras", {"fields": ("telefono",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Extras", {"fields": ("telefono",)}),)
    list_display = ("username", "email", "first_name", "last_name", "telefono", "is_staff")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "puesto", "created_at")
    search_fields = ("user__username", "user__email", "puesto")
