"""Catálogos forms."""

from django import forms

from .models import TipoCorral, TipoGanado


class TipoCorralForm(forms.ModelForm):
    class Meta:
        model = TipoCorral
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}


class TipoGanadoForm(forms.ModelForm):
    class Meta:
        model = TipoGanado
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}
