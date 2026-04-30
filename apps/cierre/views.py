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
