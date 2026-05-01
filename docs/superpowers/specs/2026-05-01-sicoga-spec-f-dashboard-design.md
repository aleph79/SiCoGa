# SiCoGa — Spec F: Dashboard ejecutivo (Diseño)

**Fecha:** 2026-05-01
**Estado:** Ejecutando — sin draft separado porque es view-only sobre datos existentes.
**Spec previo:** [E — Cierre del Lote](./2026-04-30-sicoga-spec-e-cierre-design.md) ✅ entregado

## Contexto

Specs A-E construyeron operación completa de un lote. Spec F entrega la **vista del gerente**: agregados, gráficas, mapas y KPIs financieros en una sola pantalla `/dashboard/`. Sin modelos nuevos — sólo agregaciones de los datos existentes.

## Alcance

Pantalla única `/dashboard/` con:

1. **4 KPIs gerenciales**:
   - Venta esta semana (cabezas + lotes que salen)
   - Kilos proyectados esta semana
   - Inventario total rancho (corrales + potreros)
   - Semanas sin salida (en próximas 8)

2. **Salidas proyectadas por semana** — gráfica de barras CSS para las próximas 13 semanas, distinguiendo: con salida / semana actual / sin salida.

3. **Mapa de corrales** — grid CSS con un cuadrito por corral, coloreado según etapa del lote (libre / ocupado normal / sale esta sem / zilpaterol).

4. **Indicadores operativos** — barras de progreso para:
   - GDP proyectada promedio
   - GDP real promedio (de lotes con ventas cerradas)
   - Mortalidad acumulada %
   - Conversión alimenticia promedio (lotes cerrados)

5. **Actividad de la semana** — timeline de últimos eventos (reimplantes, transiciones, entradas zilp, ventas) ordenados por fecha.

## Decisiones

- **App nueva**: `apps.dashboard` (sólo views).
- **URL**: `/dashboard/` (no toca la home `/` que sigue siendo `/disponibilidad/`).
- **Permisos**: `view_lote` (cualquier autenticado). Realmente el dashboard agrega info que ya es accesible.
- **Gráficas**: HTML+CSS simples (barras con altura proporcional), sin JS chart libraries para no añadir dependencias.

## Tests

Smoke tests de la vista cargando + presencia de los bloques principales en el HTML.
