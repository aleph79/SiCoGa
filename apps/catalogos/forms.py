"""Catálogos forms."""

from django import forms

from .models import TipoCorral


class TipoCorralForm(forms.ModelForm):
    class Meta:
        model = TipoCorral
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}
