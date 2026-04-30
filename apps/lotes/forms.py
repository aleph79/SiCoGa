"""Lotes forms."""

from django import forms
from django.core.exceptions import ValidationError

from .models import Lote, LoteFusion  # noqa: F401


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = [
            "folio",
            "corral",
            "tipo_ganado",
            "tipo_origen",
            "proveedor",
            "cabezas_iniciales",
            "fecha_inicio",
            "peso_inicial_promedio",
            "peso_salida_objetivo",
            "gdp_esperada",
            "observaciones",
            "activo",
        ]
        widgets = {
            "folio": forms.TextInput(attrs={"class": "input"}),
            "cabezas_iniciales": forms.NumberInput(
                attrs={"class": "input proyeccion-input", "min": 1}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "input proyeccion-input", "type": "date"}
            ),
            "peso_inicial_promedio": forms.NumberInput(
                attrs={"class": "input proyeccion-input", "step": "0.01"}
            ),
            "peso_salida_objetivo": forms.NumberInput(
                attrs={"class": "input proyeccion-input", "step": "0.01"}
            ),
            "gdp_esperada": forms.NumberInput(
                attrs={"class": "input proyeccion-input", "step": "0.01"}
            ),
            "observaciones": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }

    def clean(self):
        cd = super().clean()
        corral = cd.get("corral")
        cabezas = cd.get("cabezas_iniciales")
        if corral and cabezas and cabezas > corral.capacidad_maxima:
            raise ValidationError(
                {
                    "cabezas_iniciales": (
                        f"Excede la capacidad del corral ({corral.capacidad_maxima} cab.)."
                    )
                }
            )
        return cd


class LoteFusionForm(forms.Form):
    lote_origen = forms.ModelChoiceField(
        queryset=Lote.objects.none(),
        label="Lote a fusionar (origen)",
        help_text="Sus cabezas se moverán a este lote y el origen quedará inactivo.",
    )
    fecha_fusion = forms.DateField(
        widget=forms.DateInput(attrs={"class": "input", "type": "date"}),
        label="Fecha de fusión",
    )
    notas = forms.CharField(
        widget=forms.Textarea(attrs={"class": "input", "rows": 3}),
        required=False,
        label="Notas",
    )

    def __init__(self, *args, destino=None, **kwargs):
        super().__init__(*args, **kwargs)
        if destino:
            self.fields["lote_origen"].queryset = Lote.objects.filter(activo=True).exclude(
                pk=destino.pk
            )
