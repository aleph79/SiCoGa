"""Operación views — calendario de reimplantes y captura."""

from datetime import date, timedelta

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from apps.core.mixins import CatalogoMixin
from apps.lotes.models import Lote

from .forms import EntradaZilpaterolForm, PesajeForm, ReimplanteForm, TransicionForm
from .models import EntradaZilpaterol, Pesaje, Reimplante, Transicion


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


class PesajesListView(CatalogoMixin, TemplateView):
    template_name = "operacion/pesajes_list.html"
    permission_required = "operacion.view_pesaje"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Lista todos los pesajes ordenados por fecha desc, con info del lote
        ctx["pesajes"] = (
            Pesaje.objects.filter(activo=True)
            .select_related("lote", "lote__corral", "lote__tipo_ganado")
            .order_by("-fecha", "-created_at")[:100]
        )
        # Lotes activos sin pesaje reciente (>30 días o nunca)
        sin_pesaje = []
        for lote in Lote.objects.filter(activo=True).select_related("corral", "tipo_ganado"):
            ultimo = lote.pesajes.filter(activo=True).order_by("-fecha").first()
            dias_sin = (date.today() - ultimo.fecha).days if ultimo else None
            if dias_sin is None or dias_sin > 30:
                sin_pesaje.append({"lote": lote, "ultimo": ultimo, "dias_sin": dias_sin})
        ctx["sin_pesaje"] = sin_pesaje
        return ctx


class RegistrarPesajeView(CatalogoMixin, CreateView):
    model = Pesaje
    form_class = PesajeForm
    template_name = "operacion/registrar_pesaje.html"
    permission_required = "operacion.add_pesaje"
    success_url = reverse_lazy("operacion:pesajes")

    def get_initial(self):
        initial = super().get_initial()
        lote_pk = self.request.GET.get("lote")
        if lote_pk:
            initial["lote"] = lote_pk
            initial["fecha"] = date.today()
            try:
                lote = Lote.objects.get(pk=lote_pk, activo=True)
                initial["cabezas_pesadas"] = lote.cabezas_iniciales
            except Lote.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Pesaje registrado: {self.object}")
        return response


# ===== D.4 — Reportes operativos =====


class InventarioGeneralView(CatalogoMixin, TemplateView):
    template_name = "operacion/inventario_general.html"
    permission_required = "lotes.view_lote"

    def get_context_data(self, **kwargs):
        from apps.catalogos.models import Corral

        ctx = super().get_context_data(**kwargs)

        # Separar corrales y potreros por TipoCorral.nombre
        todos_corrales = Corral.objects.filter(activo=True).select_related("tipo_corral")
        corrales = [c for c in todos_corrales if c.tipo_corral.nombre != "Potrero"]
        potreros = [c for c in todos_corrales if c.tipo_corral.nombre == "Potrero"]

        # Lotes activos por corral/potrero
        lotes_activos = list(
            Lote.objects.filter(activo=True).select_related("tipo_ganado", "corral")
        )
        lotes_por_corral = {l.corral_id: l for l in lotes_activos}

        def _build_filas(unidades):
            filas = []
            for u in unidades:
                lote = lotes_por_corral.get(u.id)
                filas.append({"unidad": u, "lote": lote})
            return filas

        filas_corrales = _build_filas(corrales)
        filas_potreros = _build_filas(potreros)

        total_corrales_inv = sum(
            f["lote"].cabezas_iniciales for f in filas_corrales if f["lote"]
        )
        total_potreros_inv = sum(
            f["lote"].cabezas_iniciales for f in filas_potreros if f["lote"]
        )
        ocupados = sum(1 for f in filas_corrales if f["lote"])

        ctx["filas_corrales"] = filas_corrales
        ctx["filas_potreros"] = filas_potreros
        ctx["kpis"] = {
            "total_corrales_inv": total_corrales_inv,
            "total_potreros_inv": total_potreros_inv,
            "total_chamizal": total_corrales_inv + total_potreros_inv,
            "ocupados": ocupados,
            "total_corrales_count": len(corrales),
        }
        return ctx


class ProyeccionAnualView(CatalogoMixin, TemplateView):
    template_name = "operacion/proyeccion_anual.html"
    permission_required = "lotes.view_lote"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        anio = int(self.request.GET.get("anio") or date.today().year)

        # 1 fila por semana del año (1..52). Cada semana lista los lotes que salen ese
        # año-semana proyectado. "Sin salida" si no hay lotes para esa semana.
        salidas_por_semana = {sem: [] for sem in range(1, 53)}
        for lote in (
            Lote.objects.filter(activo=True)
            .select_related("tipo_ganado", "corral")
        ):
            f_venta = lote.fecha_proyectada_venta
            if f_venta and f_venta.year == anio:
                sem = f_venta.isocalendar()[1]
                if 1 <= sem <= 52:
                    salidas_por_semana[sem].append(lote)

        # Convertir a lista para template (semana, lotes, fecha_inicio_sem)
        from datetime import datetime

        filas = []
        for sem in range(1, 53):
            try:
                fecha_lunes = datetime.fromisocalendar(anio, sem, 1).date()
            except ValueError:
                fecha_lunes = None
            filas.append(
                {
                    "semana": sem,
                    "fecha_inicio": fecha_lunes,
                    "lotes": salidas_por_semana[sem],
                    "cabezas": sum(l.cabezas_iniciales for l in salidas_por_semana[sem]),
                }
            )

        semanas_con_salida = sum(1 for f in filas if f["lotes"])
        cabezas_total = sum(f["cabezas"] for f in filas)
        ctx["filas"] = filas
        ctx["anio"] = anio
        ctx["kpis"] = {
            "con_salida": semanas_con_salida,
            "sin_salida": 52 - semanas_con_salida,
            "cabezas_total": cabezas_total,
            "promedio_semana": cabezas_total // 52 if cabezas_total else 0,
        }
        # Selector de años: el actual y los próximos 2
        anio_act = date.today().year
        ctx["anios_disponibles"] = [anio_act - 1, anio_act, anio_act + 1, anio_act + 2]
        return ctx


class SalidasSemanalesView(CatalogoMixin, TemplateView):
    template_name = "operacion/salidas_semanales.html"
    permission_required = "lotes.view_lote"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        sem_actual = hoy.isocalendar()[1]

        # Próximas 8 semanas
        from datetime import datetime, timedelta

        filas = []
        for offset in range(0, 8):
            fecha_objetivo = hoy + timedelta(weeks=offset)
            anio_obj, sem_obj, _ = fecha_objetivo.isocalendar()
            try:
                fecha_lunes = datetime.fromisocalendar(anio_obj, sem_obj, 1).date()
            except ValueError:
                fecha_lunes = None

            lotes_sem = []
            for lote in Lote.objects.filter(activo=True).select_related(
                "tipo_ganado", "corral"
            ):
                f_venta = lote.fecha_proyectada_venta
                if f_venta and f_venta.isocalendar()[:2] == (anio_obj, sem_obj):
                    lotes_sem.append(lote)

            filas.append(
                {
                    "anio": anio_obj,
                    "semana": sem_obj,
                    "fecha_inicio": fecha_lunes,
                    "lotes": lotes_sem,
                    "cabezas": sum(l.cabezas_iniciales for l in lotes_sem),
                    "kilos": sum(
                        (l.kilos_proyectados_venta or 0) for l in lotes_sem
                    ),
                    "es_actual": sem_obj == sem_actual,
                }
            )

        sem_sin_salida = [f for f in filas if not f["lotes"]]
        ctx["filas"] = filas
        ctx["kpis"] = {
            "esta_sem_cab": filas[0]["cabezas"] if filas else 0,
            "esta_sem_kg": filas[0]["kilos"] if filas else 0,
            "siguiente_cab": filas[1]["cabezas"] if len(filas) > 1 else 0,
            "siguiente_kg": filas[1]["kilos"] if len(filas) > 1 else 0,
            "sin_salida": len(sem_sin_salida),
            "total_8sem": sum(f["cabezas"] for f in filas),
        }
        ctx["semana_actual"] = sem_actual
        return ctx
