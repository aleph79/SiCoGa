"""Catálogos views."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.core.mixins import CatalogoMixin

from .forms import CorralForm, ProveedorForm, TipoCorralForm, TipoGanadoForm, TipoOrigenForm
from .models import Corral, Proveedor, TipoCorral, TipoGanado, TipoOrigen


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


# ----- TipoOrigen -----
class TipoOrigenListView(CatalogoMixin, ListView):
    model = TipoOrigen
    template_name = "catalogos/tipoorigen_list.html"
    permission_required = "catalogos.view_tipoorigen"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class TipoOrigenCreateView(CatalogoMixin, CreateView):
    model = TipoOrigen
    form_class = TipoOrigenForm
    template_name = "catalogos/tipoorigen_form.html"
    permission_required = "catalogos.add_tipoorigen"
    success_url = reverse_lazy("catalogos:tipoorigen_list")


class TipoOrigenUpdateView(CatalogoMixin, UpdateView):
    model = TipoOrigen
    form_class = TipoOrigenForm
    template_name = "catalogos/tipoorigen_form.html"
    permission_required = "catalogos.change_tipoorigen"
    success_url = reverse_lazy("catalogos:tipoorigen_list")


class TipoOrigenDetailView(CatalogoMixin, DetailView):
    model = TipoOrigen
    template_name = "catalogos/tipoorigen_detail.html"
    permission_required = "catalogos.view_tipoorigen"
    context_object_name = "obj"


class TipoOrigenDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_tipoorigen"

    def get(self, request, pk):
        obj = get_object_or_404(TipoOrigen, pk=pk)
        return render(
            request,
            "catalogos/tipoorigen_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:tipoorigen_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(TipoOrigen, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:tipoorigen_list")


# ----- Proveedor -----
class ProveedorListView(CatalogoMixin, ListView):
    model = Proveedor
    template_name = "catalogos/proveedor_list.html"
    permission_required = "catalogos.view_proveedor"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class ProveedorCreateView(CatalogoMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "catalogos/proveedor_form.html"
    permission_required = "catalogos.add_proveedor"
    success_url = reverse_lazy("catalogos:proveedor_list")


class ProveedorUpdateView(CatalogoMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "catalogos/proveedor_form.html"
    permission_required = "catalogos.change_proveedor"
    success_url = reverse_lazy("catalogos:proveedor_list")


class ProveedorDetailView(CatalogoMixin, DetailView):
    model = Proveedor
    template_name = "catalogos/proveedor_detail.html"
    permission_required = "catalogos.view_proveedor"
    context_object_name = "obj"


class ProveedorDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_proveedor"

    def get(self, request, pk):
        obj = get_object_or_404(Proveedor, pk=pk)
        return render(
            request,
            "catalogos/proveedor_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:proveedor_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(Proveedor, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:proveedor_list")


# ----- Corral -----
class CorralListView(CatalogoMixin, ListView):
    model = Corral
    template_name = "catalogos/corral_list.html"
    permission_required = "catalogos.view_corral"
    context_object_name = "objetos"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("ver") != "todos":
            qs = qs.filter(activo=True)
        return qs


class CorralCreateView(CatalogoMixin, CreateView):
    model = Corral
    form_class = CorralForm
    template_name = "catalogos/corral_form.html"
    permission_required = "catalogos.add_corral"
    success_url = reverse_lazy("catalogos:corral_list")


class CorralUpdateView(CatalogoMixin, UpdateView):
    model = Corral
    form_class = CorralForm
    template_name = "catalogos/corral_form.html"
    permission_required = "catalogos.change_corral"
    success_url = reverse_lazy("catalogos:corral_list")


class CorralDetailView(CatalogoMixin, DetailView):
    model = Corral
    template_name = "catalogos/corral_detail.html"
    permission_required = "catalogos.view_corral"
    context_object_name = "obj"


class CorralDeleteView(CatalogoMixin, View):
    permission_required = "catalogos.delete_corral"

    def get(self, request, pk):
        obj = get_object_or_404(Corral, pk=pk)
        return render(
            request,
            "catalogos/corral_confirm_delete.html",
            {"object": obj, "cancel_url": reverse_lazy("catalogos:corral_list")},
        )

    def post(self, request, pk):
        obj = get_object_or_404(Corral, pk=pk)
        obj.activo = False
        obj.save()
        messages.success(request, f"'{obj}' marcado como inactivo.")
        return redirect("catalogos:corral_list")
