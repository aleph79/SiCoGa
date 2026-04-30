"""Cierre forms."""

from django import forms

from .models import Muerte, Venta


class MuerteForm(forms.ModelForm):
    class Meta:
        model = Muerte
        fields = ["lote", "fecha", "arete", "causa", "peso_estimado", "notas", "activo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "arete": forms.TextInput(attrs={"class": "input"}),
            "causa": forms.TextInput(attrs={"class": "input"}),
            "peso_estimado": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = [
            "lote",
            "fecha",
            "cliente",
            "cabezas",
            "kilos",
            "precio_kg",
            "notas",
            "activo",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "cliente": forms.TextInput(attrs={"class": "input"}),
            "cabezas": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "kilos": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "precio_kg": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }
