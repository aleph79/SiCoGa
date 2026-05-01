"""Dashboard ejecutivo — vista única con agregados de todos los specs anteriores."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.catalogos.models import Corral
from apps.cierre.models import Venta
from apps.lotes.models import Lote
from apps.operacion.models import EntradaZilpaterol, Reimplante, Transicion


def _semana_iso(d):
    return d.isocalendar()[:2]


class DashboardEjecutivoView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/ejecutivo.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = date.today()
        sem_actual = hoy.isocalendar()[1]
        anio_actual, _ = _semana_iso(hoy)

        lotes_activos = list(
            Lote.objects.filter(activo=True).select_related(
                "corral", "corral__tipo_corral", "tipo_ganado"
            )
        )

        # ------ 4 KPIs ------
        salen_sem_lotes = [
            l for l in lotes_activos if l.semana_proyectada_venta == sem_actual
        ]
        kpi_venta_sem_cab = sum(l.cabezas_iniciales for l in salen_sem_lotes)
        kpi_kilos_sem = sum(
            (l.kilos_proyectados_venta or Decimal("0")) for l in salen_sem_lotes
        )
        kpi_inventario_total = sum(l.cabezas_iniciales for l in lotes_activos)

        # Próximas 8 semanas — semanas sin salida
        sem_sin_salida = 0
        for offset in range(8):
            fecha_sem = hoy + timedelta(weeks=offset)
            sem, anio = fecha_sem.isocalendar()[1], fecha_sem.isocalendar()[0]
            if not any(
                l.fecha_proyectada_venta
                and l.fecha_proyectada_venta.isocalendar()[:2] == (anio, sem)
                for l in lotes_activos
            ):
                sem_sin_salida += 1

        ctx["kpis"] = {
            "venta_sem_cab": kpi_venta_sem_cab,
            "venta_sem_lotes": [l.folio for l in salen_sem_lotes],
            "kilos_sem": kpi_kilos_sem,
            "inventario_total": kpi_inventario_total,
            "sem_sin_salida": sem_sin_salida,
            "semana_actual": sem_actual,
        }

        # ------ Salidas proyectadas próximas 13 semanas ------
        salidas = []
        max_cab = 1
        for offset in range(13):
            fecha_sem = hoy + timedelta(weeks=offset)
            anio_sem, sem_sem, _ = fecha_sem.isocalendar()
            cabezas_sem = sum(
                l.cabezas_iniciales
                for l in lotes_activos
                if l.fecha_proyectada_venta
                and l.fecha_proyectada_venta.isocalendar()[:2] == (anio_sem, sem_sem)
            )
            salidas.append(
                {
                    "semana": sem_sem,
                    "cabezas": cabezas_sem,
                    "es_actual": offset == 0,
                }
            )
            if cabezas_sem > max_cab:
                max_cab = cabezas_sem

        # Calcular % de la barra (altura)
        for s in salidas:
            s["pct"] = int(s["cabezas"] / max_cab * 100) if s["cabezas"] else 0
        ctx["salidas"] = salidas

        # ------ Mapa de corrales ------
        corrales_qs = (
            Corral.objects.filter(activo=True)
            .select_related("tipo_corral")
            .order_by("clave")
        )
        lotes_por_corral = {l.corral_id: l for l in lotes_activos}
        mapa = []
        for c in corrales_qs:
            lote = lotes_por_corral.get(c.id)
            if not lote:
                estado = "libre"
            elif lote.semana_proyectada_venta == sem_actual:
                estado = "sale_sem"
            elif lote.etapa == "Zilpaterol":
                estado = "zilpaterol"
            else:
                estado = "ocupado"
            mapa.append({"corral": c, "lote": lote, "estado": estado})
        ctx["mapa_corrales"] = mapa

        # ------ Indicadores operativos ------
        # GDP proyectada promedio (de lotes activos)
        gdps_proy = [l.gdp_efectiva for l in lotes_activos if l.gdp_efectiva]
        gdp_proy = (
            sum(gdps_proy) / Decimal(len(gdps_proy)) if gdps_proy else Decimal("0")
        )

        # GDP real promedio (lotes con ventas)
        lotes_cerrados = [l for l in lotes_activos if l.kilos_vendidos]
        if lotes_cerrados:
            gdp_real = sum(l.gdp_real for l in lotes_cerrados) / Decimal(
                len(lotes_cerrados)
            )
        else:
            # Considerar también lotes inactivos con ventas
            from django.db.models import Sum

            lotes_con_venta = (
                Lote.objects.annotate(kv=Sum("ventas__kilos"))
                .filter(kv__isnull=False)
                .select_related("tipo_ganado")
            )
            gdps_reales = [l.gdp_real for l in lotes_con_venta if l.gdp_real]
            gdp_real = (
                sum(gdps_reales) / Decimal(len(gdps_reales))
                if gdps_reales
                else Decimal("0")
            )

        # Mortalidad acumulada (todos los lotes activos)
        if kpi_inventario_total:
            muertes_total = sum(l.cabezas_muertas for l in lotes_activos)
            mortalidad_pct = Decimal(muertes_total) / Decimal(
                kpi_inventario_total
            ) * Decimal("100")
        else:
            mortalidad_pct = Decimal("0")

        # Conversión alimenticia promedio (lotes con conversion no-cero)
        convs = [l.conversion_alimenticia for l in lotes_activos if l.conversion_alimenticia]
        conversion_prom = (
            sum(convs) / Decimal(len(convs)) if convs else Decimal("0")
        )

        ctx["indicadores"] = {
            "gdp_proy": gdp_proy,
            "gdp_real": gdp_real,
            "mortalidad_pct": mortalidad_pct,
            "conversion": conversion_prom,
        }

        # ------ Actividad de la semana ------
        actividad = []
        # Reimplantes
        for r in Reimplante.objects.filter(
            activo=True, fecha_aplicada__gte=hoy - timedelta(days=7)
        ).select_related("lote"):
            actividad.append(
                {
                    "fecha": r.fecha_aplicada,
                    "tipo": "Reimplante",
                    "icono": "💉",
                    "descripcion": f"{r.lote.folio} — {r.get_numero_display()}",
                }
            )
        # Transiciones
        for t in Transicion.objects.filter(
            activo=True, fecha__gte=hoy - timedelta(days=7)
        ).select_related("lote"):
            actividad.append(
                {
                    "fecha": t.fecha,
                    "tipo": "Transición",
                    "icono": "🔄",
                    "descripcion": f"{t.lote.folio} — {t.de_fase}→{t.a_fase}",
                }
            )
        # Entradas zilpaterol
        for e in EntradaZilpaterol.objects.filter(
            activo=True, fecha_entrada__gte=hoy - timedelta(days=7)
        ).select_related("lote"):
            actividad.append(
                {
                    "fecha": e.fecha_entrada,
                    "tipo": "Zilpaterol",
                    "icono": "⚡",
                    "descripcion": f"{e.lote.folio} entró a Zilpaterol",
                }
            )
        # Ventas
        for v in Venta.objects.filter(
            activo=True, fecha__gte=hoy - timedelta(days=7)
        ).select_related("lote"):
            actividad.append(
                {
                    "fecha": v.fecha,
                    "tipo": "Venta",
                    "icono": "💰",
                    "descripcion": f"{v.lote.folio} — {v.cabezas} cab a {v.cliente or '—'}",
                }
            )
        actividad.sort(key=lambda a: a["fecha"], reverse=True)
        ctx["actividad"] = actividad[:15]

        return ctx
