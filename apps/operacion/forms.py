"""Operación forms."""

from django import forms

from .models import EntradaZilpaterol, Pesaje, Reimplante, Transicion


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


class TransicionForm(forms.ModelForm):
    class Meta:
        model = Transicion
        fields = ["lote", "fecha", "de_fase", "a_fase", "proporcion", "notas", "activo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "proporcion": forms.TextInput(attrs={"class": "input"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }


class EntradaZilpaterolForm(forms.ModelForm):
    class Meta:
        model = EntradaZilpaterol
        fields = ["lote", "fecha_entrada", "observaciones", "activo"]
        widgets = {
            "fecha_entrada": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "observaciones": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }


class PesajeForm(forms.ModelForm):
    class Meta:
        model = Pesaje
        fields = ["lote", "fecha", "peso_promedio", "cabezas_pesadas", "notas", "activo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "peso_promedio": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "cabezas_pesadas": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }
