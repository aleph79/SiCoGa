"""Lotes views."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import CatalogoMixin

from .forms import LoteForm
from .models import Lote


class LoteListView(CatalogoMixin, ListView):
    model = Lote
    template_name = "lotes/lote_list.html"
    permission_required = "lotes.view_lote"
    context_object_name = "objetos"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("corral", "tipo_ganado", "tipo_origen", "proveedor")
        )
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class LoteCreateView(CatalogoMixin, CreateView):
    model = Lote
    form_class = LoteForm
    template_name = "lotes/lote_form.html"
    permission_required = "lotes.add_lote"
    success_url = reverse_lazy("lotes:lote_list")


class LoteUpdateView(CatalogoMixin, UpdateView):
    model = Lote
    form_class = LoteForm
    template_name = "lotes/lote_form.html"
    permission_required = "lotes.change_lote"
    success_url = reverse_lazy("lotes:lote_list")


class LoteDetailView(CatalogoMixin, DetailView):
    model = Lote
    template_name = "lotes/lote_detail.html"
    permission_required = "lotes.view_lote"
    context_object_name = "obj"


class LoteDeleteView(CatalogoMixin, View):
    permission_required = "lotes.delete_lote"

    def get(self, request, pk):
        obj = get_object_or_404(Lote, pk=pk)
        return render(
            request,
            "lotes/lote_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("lotes:lote_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(Lote, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("lotes:lote_list")


class PreviewProyeccionView(LoginRequiredMixin, View):
    """HTMX endpoint: recibe los campos clave del form y devuelve el partial
    con la proyección calculada, sin guardar nada."""

    def post(self, request):
        from decimal import Decimal, InvalidOperation

        from apps.catalogos.models import TipoGanado, TipoOrigen

        def _decimal(v):
            try:
                return Decimal(v) if v else None
            except (InvalidOperation, TypeError):
                return None

        def _date(v):
            from datetime import datetime

            try:
                return datetime.strptime(v, "%Y-%m-%d").date() if v else None
            except (ValueError, TypeError):
                return None

        def _int(v):
            try:
                return int(v) if v else 0
            except (ValueError, TypeError):
                return 0

        tipo_ganado = TipoGanado.objects.filter(pk=request.POST.get("tipo_ganado") or 0).first()
        tipo_origen = TipoOrigen.objects.filter(pk=request.POST.get("tipo_origen") or 0).first()

        lote = Lote(
            tipo_ganado=tipo_ganado,
            tipo_origen=tipo_origen,
            cabezas_iniciales=_int(request.POST.get("cabezas_iniciales")),
            peso_inicial_promedio=_decimal(request.POST.get("peso_inicial_promedio"))
            or Decimal("0"),
            peso_salida_objetivo=_decimal(request.POST.get("peso_salida_objetivo")),
            gdp_esperada=_decimal(request.POST.get("gdp_esperada")),
            fecha_inicio=_date(request.POST.get("fecha_inicio")),
        )
        return render(request, "lotes/_proyeccion_preview.html", {"lote": lote})
