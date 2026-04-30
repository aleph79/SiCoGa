"""Operación forms."""

from django import forms

from .models import Reimplante


class ReimplanteForm(forms.ModelForm):
    class Meta:
        model = Reimplante
        fields = [
            "lote",
            "numero",
            "fecha_aplicada",
            "implante",
            "peso_aplicado",
            "cabezas_aplicadas",
            "observaciones",
            "activo",
        ]
        widgets = {
            "fecha_aplicada": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "peso_aplicado": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "cabezas_aplicadas": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "observaciones": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }
