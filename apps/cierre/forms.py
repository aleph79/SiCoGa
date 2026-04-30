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


from apps.lotes.models import Lote  # noqa: E402


class CompraLoteForm(forms.ModelForm):
    """Form para capturar los datos de compra/recepción de un lote existente."""

    class Meta:
        model = Lote
        fields = [
            "fecha_compra",
            "cabezas_origen",
            "kilos_origen",
            "kilos_recibo",
            "costo_compra",
        ]
        widgets = {
            "fecha_compra": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "cabezas_origen": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "kilos_origen": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "kilos_recibo": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "costo_compra": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
        }


from .models import Alimentacion, Medicacion  # noqa: E402


class AlimentacionForm(forms.ModelForm):
    class Meta:
        model = Alimentacion
        fields = [
            "lote",
            "formula",
            "fecha_inicio",
            "fecha_fin",
            "kg_consumidos",
            "costo_kg",
            "notas",
            "activo",
        ]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "kg_consumidos": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "costo_kg": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }


class MedicacionForm(forms.ModelForm):
    class Meta:
        model = Medicacion
        fields = [
            "lote",
            "medicamento",
            "tipo",
            "fecha",
            "cabezas",
            "dosis_descripcion",
            "costo_unitario",
            "arete",
            "notas",
            "activo",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "cabezas": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "dosis_descripcion": forms.TextInput(attrs={"class": "input"}),
            "costo_unitario": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "arete": forms.TextInput(attrs={"class": "input"}),
            "notas": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }
