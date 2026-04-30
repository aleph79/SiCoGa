"""Catálogos forms."""

from django import forms

from .models import Corral, Proveedor, TipoCorral, TipoGanado, TipoOrigen


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


class TipoOrigenForm(forms.ModelForm):
    class Meta:
        model = TipoOrigen
        fields = ["nombre", "activo"]
        widgets = {"nombre": forms.TextInput(attrs={"class": "input", "autofocus": True})}


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "rfc", "telefono", "contacto", "notas", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "rfc": forms.TextInput(attrs={"class": "input", "maxlength": 13}),
            "telefono": forms.TextInput(attrs={"class": "input"}),
            "contacto": forms.TextInput(attrs={"class": "input"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }


class CorralForm(forms.ModelForm):
    class Meta:
        model = Corral
        fields = ["clave", "nombre", "tipo_corral", "capacidad_maxima", "activo"]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "input"}),
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "capacidad_maxima": forms.NumberInput(attrs={"class": "input", "min": 1}),
        }
