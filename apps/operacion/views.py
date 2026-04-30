"""Operación views — calendario de reimplantes y captura."""

from datetime import date, timedelta

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from apps.core.mixins import CatalogoMixin
from apps.lotes.models import Lote

from .forms import EntradaZilpaterolForm, ReimplanteForm, TransicionForm
from .models import EntradaZilpaterol, Reimplante, Transicion


def _semana_de_fecha(d):
    return d.isocalendar()[1] if d else None


class ReimplantesCalendarioView(CatalogoMixin, TemplateView):
    template_name = "operacion/reimplantes_calendario.html"
    permission_required = "operacion.view_reimplante"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        sem_actual = hoy.isocalendar()[1]

        # Pendientes: para cada lote activo, ver qué reimplantes (1, 2, 3) faltan
        pendientes = []
        for lote in Lote.objects.filter(activo=True).select_related("tipo_ganado", "corral"):
            aplicados = set(lote.reimplantes.filter(activo=True).values_list("numero", flat=True))
            for n in (1, 2, 3):
                if n in aplicados:
                    continue
                fecha_proy = lote.fecha_reimplante(n)
                if fecha_proy and fecha_proy >= hoy - timedelta(days=14):
                    pendientes.append(
                        {
                            "lote": lote,
                            "numero": n,
                            "fecha_proyectada": fecha_proy,
                            "semana": _semana_de_fecha(fecha_proy),
                            "vencido": fecha_proy < hoy,
                        }
                    )
        pendientes.sort(key=lambda p: p["fecha_proyectada"])

        # Historial reciente (últimos 20)
        historial = (
            Reimplante.objects.filter(activo=True)
            .select_related("lote", "lote__tipo_ganado", "lote__corral", "implante")
            .order_by("-fecha_aplicada", "-created_at")[:20]
        )

        # KPIs
        sem_proxima = sem_actual + 1
        anio_actual = hoy.year
        ctx["kpis"] = {
            "pendientes_esta_sem": sum(1 for p in pendientes if p["semana"] == sem_actual),
            "pendientes_proxima": sum(1 for p in pendientes if p["semana"] == sem_proxima),
            "completados_anio": Reimplante.objects.filter(
                activo=True, fecha_aplicada__year=anio_actual
            ).count(),
            "lotes_en_programa": Lote.objects.filter(activo=True).count(),
        }
        ctx["pendientes"] = pendientes
        ctx["historial"] = historial
        ctx["semana_actual"] = sem_actual
        return ctx


class RegistrarReimplanteView(CatalogoMixin, CreateView):
    model = Reimplante
    form_class = ReimplanteForm
    template_name = "operacion/registrar_reimplante.html"
    permission_required = "operacion.add_reimplante"
    success_url = reverse_lazy("operacion:reimplantes")

    def get_initial(self):
        initial = super().get_initial()
        # Preseleccionar lote/numero/fecha desde la query string
        lote_pk = self.request.GET.get("lote")
        numero = self.request.GET.get("numero")
        if lote_pk:
            initial["lote"] = lote_pk
            try:
                lote = Lote.objects.get(pk=lote_pk, activo=True)
                initial["cabezas_aplicadas"] = lote.cabezas_iniciales
                if numero and numero.isdigit():
                    n = int(numero)
                    initial["numero"] = n
                    if n >= 1:
                        initial["fecha_aplicada"] = lote.fecha_reimplante(n)
                    else:
                        initial["fecha_aplicada"] = lote.fecha_inicio
            except Lote.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Reimplante registrado: {self.object}",
        )
        return response


class TransicionesCalendarioView(CatalogoMixin, TemplateView):
    template_name = "operacion/transiciones_calendario.html"
    permission_required = "operacion.view_transicion"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        sem_actual = hoy.isocalendar()[1]

        # "Pendientes" se calcula a partir de Lote.fecha_entrada_zilpaterol y los días de transición
        # del programa: lotes que entran a transición F1→FT en las próximas semanas.
        pendientes = []
        for lote in Lote.objects.filter(activo=True).select_related(
            "tipo_ganado", "corral"
        ):
            p = lote.programa
            if not p:
                continue
            dias_a_FT = p.dias_recepcion + p.dias_f1
            fecha_FT = lote.fecha_inicio + timedelta(days=dias_a_FT)
            dias_a_F3 = dias_a_FT + p.dias_transicion
            fecha_F3 = lote.fecha_inicio + timedelta(days=dias_a_F3)

            for transicion_label, fecha_proy in (
                ("F1→FT", fecha_FT),
                ("FT→F3", fecha_F3),
            ):
                if fecha_proy and fecha_proy >= hoy - timedelta(days=14):
                    pendientes.append(
                        {
                            "lote": lote,
                            "transicion": transicion_label,
                            "fecha_proyectada": fecha_proy,
                            "semana": fecha_proy.isocalendar()[1],
                            "vencido": fecha_proy < hoy,
                        }
                    )
        pendientes.sort(key=lambda p: p["fecha_proyectada"])

        historial = (
            Transicion.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "lote__tipo_ganado")
            .order_by("-fecha", "-created_at")[:20]
        )

        ctx["kpis"] = {
            "esta_sem": sum(1 for p in pendientes if p["semana"] == sem_actual),
            "proxima": sum(1 for p in pendientes if p["semana"] == sem_actual + 1),
            "completadas_anio": Transicion.objects.filter(
                activo=True, fecha__year=hoy.year
            ).count(),
            "lotes_activos": Lote.objects.filter(activo=True).count(),
        }
        ctx["pendientes"] = pendientes
        ctx["historial"] = historial
        ctx["semana_actual"] = sem_actual
        return ctx


class RegistrarTransicionView(CatalogoMixin, CreateView):
    model = Transicion
    form_class = TransicionForm
    template_name = "operacion/registrar_transicion.html"
    permission_required = "operacion.add_transicion"
    success_url = reverse_lazy("operacion:transiciones")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            initial["fecha"] = date.today()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Transición registrada: {self.object}")
        return response


class ZilpaterolCalendarioView(CatalogoMixin, TemplateView):
    template_name = "operacion/zilpaterol_calendario.html"
    permission_required = "operacion.view_entradazilpaterol"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        sem_actual = hoy.isocalendar()[1]

        # Activos en zilpaterol (lotes con EntradaZilpaterol activa, fecha_entrada hasta hoy)
        activos = (
            EntradaZilpaterol.objects.filter(activo=True, fecha_entrada__lte=hoy)
            .select_related("lote", "lote__corral", "lote__tipo_ganado")
            .order_by("fecha_entrada")
        )
        # Lotes que NO han entrado todavía pero están proyectados a entrar (lote.fecha_entrada_zilpaterol)
        pendientes = []
        registrados_pks = set(activos.values_list("lote_id", flat=True))
        for lote in Lote.objects.filter(activo=True).exclude(pk__in=registrados_pks):
            fecha_proy = lote.fecha_entrada_zilpaterol
            if fecha_proy and fecha_proy >= hoy - timedelta(days=14):
                pendientes.append(
                    {
                        "lote": lote,
                        "fecha_proyectada": fecha_proy,
                        "semana": fecha_proy.isocalendar()[1],
                        "vencido": fecha_proy < hoy,
                    }
                )
        pendientes.sort(key=lambda p: p["fecha_proyectada"])

        cabezas_activas = sum(e.lote.cabezas_iniciales for e in activos)
        listos = sum(1 for e in activos if e.listo_para_venta)

        ctx["kpis"] = {
            "activos": activos.count(),
            "cabezas_activas": cabezas_activas,
            "listos": listos,
            "pendientes": len(pendientes),
        }
        ctx["activos"] = activos
        ctx["pendientes"] = pendientes
        ctx["semana_actual"] = sem_actual
        return ctx


class RegistrarEntradaZilpaterolView(CatalogoMixin, CreateView):
    model = EntradaZilpaterol
    form_class = EntradaZilpaterolForm
    template_name = "operacion/registrar_zilpaterol.html"
    permission_required = "operacion.add_entradazilpaterol"
    success_url = reverse_lazy("operacion:zilpaterol")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            try:
                lote = Lote.objects.get(pk=lote_pk, activo=True)
                proy = lote.fecha_entrada_zilpaterol
                if proy:
                    initial["fecha_entrada"] = proy
            except Lote.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Entrada a Zilpaterol registrada: {self.object}")
        return response
