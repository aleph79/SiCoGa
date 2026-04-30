"""Catálogos forms."""

from django import forms
from django.core.exceptions import ValidationError

from .models import Corral, ProgramaReimplante, Proveedor, TipoCorral, TipoGanado, TipoOrigen


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


class ProgramaReimplanteForm(forms.ModelForm):
    class Meta:
        model = ProgramaReimplante
        fields = [
            "tipo_ganado",
            "tipo_origen",
            "peso_min",
            "peso_max",
            "gdp_esperada",
            "peso_objetivo_salida",
            "implante_inicial",
            "reimplante_1",
            "reimplante_2",
            "reimplante_3",
            "reimplante_4",
            "dias_recepcion",
            "dias_f1",
            "dias_transicion",
            "dias_f3",
            "dias_zilpaterol",
            "activo",
        ]
        widgets = {
            "peso_min": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "peso_max": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "gdp_esperada": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "peso_objetivo_salida": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
        }

    def clean(self):
        cd = super().clean()
        peso_min = cd.get("peso_min")
        peso_max = cd.get("peso_max")
        tipo_ganado = cd.get("tipo_ganado")
        tipo_origen = cd.get("tipo_origen")

        if peso_min is not None and peso_max is not None and peso_max <= peso_min:
            raise ValidationError({"peso_max": "Debe ser mayor que peso mínimo."})

        if tipo_ganado and peso_min is not None and peso_max is not None:
            qs = ProgramaReimplante.objects.filter(
                tipo_ganado=tipo_ganado,
                tipo_origen=tipo_origen,
                activo=True,
                peso_min__lte=peso_max,
                peso_max__gte=peso_min,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    "Existe un rango activo que se traslapa con éste para la misma combinación."
                )
        return cd
