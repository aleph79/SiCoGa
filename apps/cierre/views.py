"""Cierre views — captura de muertes y ventas."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView

from apps.core.mixins import CatalogoMixin
from apps.lotes.models import Lote

from .forms import MuerteForm, VentaForm
from .models import Muerte, Venta


class MuertesListView(CatalogoMixin, ListView):
    template_name = "cierre/muertes_list.html"
    permission_required = "cierre.view_muerte"
    context_object_name = "muertes"
    paginate_by = 50

    def get_queryset(self):
        return (
            Muerte.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "lote__tipo_ganado")
            .order_by("-fecha", "-created_at")
        )


class RegistrarMuerteView(CatalogoMixin, CreateView):
    model = Muerte
    form_class = MuerteForm
    template_name = "cierre/registrar_muerte.html"
    permission_required = "cierre.add_muerte"
    success_url = reverse_lazy("cierre:muertes")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            from datetime import date

            initial["fecha"] = date.today()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Muerte registrada: {self.object}")
        return response


class VentasListView(CatalogoMixin, ListView):
    template_name = "cierre/ventas_list.html"
    permission_required = "cierre.view_venta"
    context_object_name = "ventas"
    paginate_by = 50

    def get_queryset(self):
        return (
            Venta.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "lote__tipo_ganado")
            .order_by("-fecha", "-created_at")
        )


class RegistrarVentaView(CatalogoMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = "cierre/registrar_venta.html"
    permission_required = "cierre.add_venta"
    success_url = reverse_lazy("cierre:ventas")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            try:
                lote = Lote.objects.get(pk=lote_pk, activo=True)
                from datetime import date

                initial["fecha"] = date.today()
                initial["cabezas"] = lote.cabezas_actuales
            except Lote.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Venta registrada: {self.object}")
        return response


from django.views.generic import UpdateView  # noqa: E402

from apps.lotes.models import Lote  # noqa: E402

from .forms import CompraLoteForm  # noqa: E402


class CompraLoteView(CatalogoMixin, UpdateView):
    """Captura los datos de compra/recepción del lote (campos del modelo Lote)."""

    model = Lote
    form_class = CompraLoteForm
    template_name = "cierre/compra_lote.html"
    permission_required = "lotes.change_lote"
    pk_url_kwarg = "pk"

    def get_success_url(self):
        from django.urls import reverse

        return reverse("lotes:lote_detail", args=[self.object.pk])

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Compra/recepción guardada para {self.object.folio}")
        return response


from .forms import AlimentacionForm, MedicacionForm  # noqa: E402
from .models import Alimentacion, Medicacion  # noqa: E402


class AlimentacionListView(CatalogoMixin, ListView):
    template_name = "cierre/alimentaciones_list.html"
    permission_required = "cierre.view_alimentacion"
    context_object_name = "alimentaciones"
    paginate_by = 50

    def get_queryset(self):
        return (
            Alimentacion.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "formula")
            .order_by("-fecha_inicio", "-created_at")
        )


class RegistrarAlimentacionView(CatalogoMixin, CreateView):
    model = Alimentacion
    form_class = AlimentacionForm
    template_name = "cierre/registrar_alimentacion.html"
    permission_required = "cierre.add_alimentacion"
    success_url = reverse_lazy("cierre:alimentaciones")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Alimentación registrada: {self.object}")
        return response


class MedicacionListView(CatalogoMixin, ListView):
    template_name = "cierre/medicaciones_list.html"
    permission_required = "cierre.view_medicacion"
    context_object_name = "medicaciones"
    paginate_by = 50

    def get_queryset(self):
        return (
            Medicacion.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "medicamento")
            .order_by("-fecha", "-created_at")
        )


class RegistrarMedicacionView(CatalogoMixin, CreateView):
    model = Medicacion
    form_class = MedicacionForm
    template_name = "cierre/registrar_medicacion.html"
    permission_required = "cierre.add_medicacion"
    success_url = reverse_lazy("cierre:medicaciones")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            try:
                lote = Lote.objects.get(pk=lote_pk, activo=True)
                initial["cabezas"] = lote.cabezas_actuales or lote.cabezas_iniciales
            except Lote.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Medicación registrada: {self.object}")
        return response


from django.views.generic import DetailView  # noqa: E402

from .forms import CostoHotelComponenteForm  # noqa: E402
from .models import CostoHotelComponente  # noqa: E402


class CostoHotelConfigView(CatalogoMixin, ListView):
    """Lista de componentes del costo hotel + total habilitado."""

    template_name = "cierre/costo_hotel_config.html"
    permission_required = "cierre.view_costohotelcomponente"
    context_object_name = "componentes"

    def get_queryset(self):
        return CostoHotelComponente.objects.filter(activo=True).order_by("nombre")

    def get_context_data(self, **kwargs):
        from decimal import Decimal

        ctx = super().get_context_data(**kwargs)
        habilitados = self.get_queryset().filter(habilitado=True)
        ctx["total_dia_animal"] = sum(
            (c.costo_dia_animal for c in habilitados), start=Decimal("0")
        )
        return ctx


class RegistrarCostoHotelComponenteView(CatalogoMixin, CreateView):
    model = CostoHotelComponente
    form_class = CostoHotelComponenteForm
    template_name = "cierre/registrar_costo_hotel.html"
    permission_required = "cierre.add_costohotelcomponente"
    success_url = reverse_lazy("cierre:costo_hotel_config")


class EditarCostoHotelComponenteView(CatalogoMixin, UpdateView):
    model = CostoHotelComponente
    form_class = CostoHotelComponenteForm
    template_name = "cierre/registrar_costo_hotel.html"
    permission_required = "cierre.change_costohotelcomponente"
    success_url = reverse_lazy("cierre:costo_hotel_config")


class CostoHotelLoteView(CatalogoMixin, DetailView):
    """Vista por lote con el cálculo completo de días-animal y costo hotel."""

    model = Lote
    template_name = "cierre/costo_hotel_lote.html"
    permission_required = "lotes.view_lote"
    context_object_name = "obj"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["componentes"] = CostoHotelComponente.objects.filter(activo=True).order_by(
            "nombre"
        )
        return ctx


import csv  # noqa: E402

from django.http import HttpResponse  # noqa: E402


class CierreLoteView(CatalogoMixin, DetailView):
    """Pantalla consolidada de cierre del lote — KPIs + resumen financiero."""

    model = Lote
    template_name = "cierre/cierre_lote.html"
    permission_required = "lotes.view_lote"
    context_object_name = "obj"


class CierreLoteCsvView(CatalogoMixin, DetailView):
    """Export CSV del resumen de cierre del lote."""

    model = Lote
    permission_required = "lotes.view_lote"

    def get(self, request, *args, **kwargs):
        lote = self.get_object()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="cierre-{lote.folio}.csv"'
        )
        w = csv.writer(response)
        w.writerow(["Concepto", "Valor"])
        w.writerow(["Folio", lote.folio])
        w.writerow(["Corral", lote.corral.clave])
        w.writerow(["Tipo de ganado", lote.tipo_ganado.nombre])
        w.writerow(["Fecha inicio", lote.fecha_inicio.isoformat()])
        w.writerow(["Fecha cierre", lote.fecha_cierre.isoformat()])
        w.writerow(["Días calendario", lote.dias_calendario])
        w.writerow(["Cabezas iniciales", lote.cabezas_iniciales])
        w.writerow(["Cabezas muertas", lote.cabezas_muertas])
        w.writerow(["Cabezas vendidas", lote.cabezas_vendidas])
        w.writerow(["Mortalidad %", f"{lote.mortalidad_pct:.2f}"])
        w.writerow(["Días animal netos", lote.dias_animal_netos])
        w.writerow(["", ""])
        w.writerow(["GDP real (kg/d/cab)", f"{lote.gdp_real:.3f}"])
        w.writerow(["Kg alimento total", lote.kg_alimento_total])
        w.writerow(["Conversión alimenticia", f"{lote.conversion_alimenticia:.2f}"])
        w.writerow(["", ""])
        w.writerow(["Costo compra", lote.costo_compra or 0])
        w.writerow(["Costo alimentación", lote.costo_alimentacion_total])
        w.writerow(["Costo medicación", lote.costo_medicacion_total])
        w.writerow(["Costo hotel", lote.costo_hotel_total])
        w.writerow(["COSTO TOTAL", lote.costo_total])
        w.writerow(["Ingreso ventas", lote.ingreso_total_ventas])
        w.writerow(["MARGEN BRUTO", lote.margen_bruto])
        w.writerow(["Margen %", f"{lote.margen_pct:.2f}"])
        return response
