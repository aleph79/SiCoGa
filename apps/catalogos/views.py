"""Catálogos views."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import CatalogoMixin

from .forms import TipoCorralForm, TipoGanadoForm
from .models import TipoCorral, TipoGanado


# ----- TipoCorral -----
class TipoCorralListView(CatalogoMixin, ListView):
    model = TipoCorral
    template_name = "catalogos/tipocorral_list.html"
    permission_required = "catalogos.view_tipocorral"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class TipoCorralCreateView(CatalogoMixin, CreateView):
    model = TipoCorral
    form_class = TipoCorralForm
    template_name = "catalogos/tipocorral_form.html"
    permission_required = "catalogos.add_tipocorral"
    success_url = reverse_lazy("catalogos:tipocorral_list")


class TipoCorralUpdateView(CatalogoMixin, UpdateView):
    model = TipoCorral
    form_class = TipoCorralForm
    template_name = "catalogos/tipocorral_form.html"
    permission_required = "catalogos.change_tipocorral"
    success_url = reverse_lazy("catalogos:tipocorral_list")


class TipoCorralDetailView(CatalogoMixin, DetailView):
    model = TipoCorral
    template_name = "catalogos/tipocorral_detail.html"
    permission_required = "catalogos.view_tipocorral"
    context_object_name = "obj"


class TipoCorralDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_tipocorral"

    def get(self, request, pk):
        obj = get_object_or_404(TipoCorral, pk=pk)
        return render(
            request,
            "catalogos/tipocorral_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:tipocorral_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(TipoCorral, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:tipocorral_list")


# ----- TipoGanado -----
class TipoGanadoListView(CatalogoMixin, ListView):
    model = TipoGanado
    template_name = "catalogos/tipoganado_list.html"
    permission_required = "catalogos.view_tipoganado"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class TipoGanadoCreateView(CatalogoMixin, CreateView):
    model = TipoGanado
    form_class = TipoGanadoForm
    template_name = "catalogos/tipoganado_form.html"
    permission_required = "catalogos.add_tipoganado"
    success_url = reverse_lazy("catalogos:tipoganado_list")


class TipoGanadoUpdateView(CatalogoMixin, UpdateView):
    model = TipoGanado
    form_class = TipoGanadoForm
    template_name = "catalogos/tipoganado_form.html"
    permission_required = "catalogos.change_tipoganado"
    success_url = reverse_lazy("catalogos:tipoganado_list")


class TipoGanadoDetailView(CatalogoMixin, DetailView):
    model = TipoGanado
    template_name = "catalogos/tipoganado_detail.html"
    permission_required = "catalogos.view_tipoganado"
    context_object_name = "obj"


class TipoGanadoDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_tipoganado"

    def get(self, request, pk):
        obj = get_object_or_404(TipoGanado, pk=pk)
        return render(
            request,
            "catalogos/tipoganado_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:tipoganado_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(TipoGanado, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:tipoganado_list")
