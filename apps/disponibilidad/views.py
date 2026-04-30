"""Disponibilidad views."""

import csv
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponse
from django.views.generic import TemplateView, View

from apps.catalogos.models import Corral, TipoGanado
from apps.lotes.models import Lote

ETAPAS = [
    "Recepción",
    "F1",
    "Transición",
    "F3",
    "Zilpaterol",
    "Post-Zilpaterol",
    "Sin programa",
]


def _build_filas(filtros):
    """Devuelve (filas, kpis_dict). Cada fila es {'corral': c, 'lote': l_or_None}."""
    corrales = (
        Corral.objects.filter(activo=True)
        .prefetch_related(Prefetch("lotes", queryset=Lote.objects.filter(activo=True)))
        .order_by("clave")
    )

    filas = []
    for c in corrales:
        lotes_activos = list(c.lotes.all())
        lote = lotes_activos[0] if lotes_activos else None

        if filtros.get("tipo_ganado"):
            if not lote or str(lote.tipo_ganado_id) != filtros["tipo_ganado"]:
                continue
        if filtros.get("etapa"):
            if not lote or lote.etapa != filtros["etapa"]:
                continue
        if not filtros.get("ver_libres") and not lote:
            continue

        filas.append({"corral": c, "lote": lote})

    sem_actual = date.today().isocalendar()[1]
    activos = Lote.objects.filter(activo=True)
    kpis = {
        "lotes_activos": activos.count(),
        "inventario": sum(lote.cabezas_iniciales for lote in activos),
        "salen_semana": sum(
            lote.cabezas_iniciales for lote in activos if lote.semana_proyectada_venta == sem_actual
        ),
        "corrales_libres": (Corral.objects.filter(activo=True).count() - activos.count()),
        "semana_actual": sem_actual,
    }
    return filas, kpis


class DisponibilidadView(LoginRequiredMixin, TemplateView):
    template_name = "disponibilidad/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filtros = {
            "tipo_ganado": self.request.GET.get("tipo_ganado") or "",
            "etapa": self.request.GET.get("etapa") or "",
            "ver_libres": self.request.GET.get("ver_libres") == "1",
        }
        filas, kpis = _build_filas(filtros)
        ctx["filas"] = filas
        ctx["kpis"] = kpis
        ctx["filtros"] = filtros
        ctx["tipos_ganado"] = TipoGanado.objects.filter(activo=True)
        ctx["etapas"] = ETAPAS
        return ctx


class ExportCsvView(LoginRequiredMixin, View):
    def get(self, request):
        filas, _ = _build_filas({"ver_libres": True})
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="disponibilidad-{date.today().isoformat()}.csv"'
        )
        w = csv.writer(response)
        w.writerow(
            [
                "Corral",
                "Lote",
                "Tipo",
                "Origen",
                "Inventario",
                "Fecha Inicio",
                "Peso Inicial",
                "Días Trans.",
                "Días Eng. Proy.",
                "Peso Act. Proy.",
                "GDP",
                "Peso Salida",
                "F. 1er Reimp.",
                "Etapa",
                "Sem. Venta",
            ]
        )
        for f in filas:
            c = f["corral"]
            lote = f["lote"]
            if lote:
                w.writerow(
                    [
                        c.clave,
                        lote.folio,
                        lote.tipo_ganado.nombre,
                        lote.tipo_origen.nombre if lote.tipo_origen else "",
                        lote.cabezas_iniciales,
                        lote.fecha_inicio.isoformat(),
                        lote.peso_inicial_promedio,
                        lote.dias_transcurridos,
                        lote.dias_engorda_proyectados or "",
                        lote.peso_actual_proyectado or "",
                        lote.gdp_efectiva or "",
                        lote.peso_objetivo_efectivo or "",
                        lote.fecha_reimplante_1.isoformat() if lote.fecha_reimplante_1 else "",
                        lote.etapa,
                        lote.semana_proyectada_venta or "",
                    ]
                )
            else:
                w.writerow([c.clave, "Libre"] + [""] * 13)
        return response
