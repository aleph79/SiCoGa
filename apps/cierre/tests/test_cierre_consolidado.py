"""Tests para el cierre consolidado del lote (Spec E.5)."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_e5(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_e5", email="ae5@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def lote_completo(db):
    """Un lote con compra, alimentación, medicación, venta — listo para cerrar."""
    from apps.catalogos.models import (
        Corral,
        Formula,
        Medicamento,
        ProgramaReimplante,
        TipoCorral,
        TipoGanado,
    )
    from apps.cierre.models import (
        Alimentacion,
        CostoHotelComponente,
        Medicacion,
        Venta,
    )
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    formula = Formula.objects.get_or_create(nombre="F1 sin melaza")[0]
    formula.costo_kg = Decimal("3.20")
    formula.save()
    medicamento = Medicamento.objects.create(
        nombre="Test Med", unidad_dosis="ml/cab", costo_unitario=Decimal("10.00")
    )
    c = Corral.objects.create(
        clave="CL-CIE", nombre="Cie", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-CIE",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date(2026, 1, 1),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
        kilos_recibo=Decimal("50000"),
        costo_compra=Decimal("2000000"),
    )
    Alimentacion.objects.create(
        lote=lote,
        formula=formula,
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 4, 30),
        kg_consumidos=Decimal("100000"),
    )
    Medicacion.objects.create(
        lote=lote,
        medicamento=medicamento,
        tipo="recepcion",
        fecha=date(2026, 1, 2),
        cabezas=200,
    )
    Venta.objects.create(
        lote=lote,
        fecha=date(2026, 5, 1),
        cliente="Rastro X",
        cabezas=200,
        kilos=Decimal("116000"),
        precio_kg=Decimal("52.00"),
    )

    if CostoHotelComponente.objects.count() == 0:
        CostoHotelComponente.objects.create(
            nombre="Hotel test",
            costo_dia_animal=Decimal("10.00"),
            habilitado=True,
        )

    return lote


def test_costo_alimentacion_total(lote_completo):
    # 100,000 kg × $3.20 = $320,000
    assert lote_completo.costo_alimentacion_total == Decimal("320000")


def test_kg_alimento_total(lote_completo):
    assert lote_completo.kg_alimento_total == Decimal("100000")


def test_costo_medicacion_total(lote_completo):
    # 200 cab × $10 = $2,000
    assert lote_completo.costo_medicacion_total == Decimal("2000")


def test_kilos_vendidos(lote_completo):
    assert lote_completo.kilos_vendidos == Decimal("116000")


def test_kg_ganados(lote_completo):
    # 116,000 vendidos − 50,000 recibidos = 66,000
    assert lote_completo.kg_ganados == Decimal("66000")


def test_conversion_alimenticia(lote_completo):
    # 100,000 kg alim / 66,000 kg ganados = 1.515...
    assert lote_completo.conversion_alimenticia == pytest.approx(
        Decimal("1.515"), abs=Decimal("0.01")
    )


def test_costo_total_y_margen(lote_completo):
    # Costos: compra 2M + alim 320k + medi 2k + hotel = 2.322M + hotel
    # Ingresos: 116k × $52 = $6,032,000
    # No nos importa el valor exacto del hotel, sólo que el margen sea ingreso − costo
    margen_calc = lote_completo.ingreso_total_ventas - lote_completo.costo_total
    assert lote_completo.margen_bruto == margen_calc


def test_margen_pct(lote_completo):
    if lote_completo.ingreso_total_ventas:
        expected = (
            lote_completo.margen_bruto
            / lote_completo.ingreso_total_ventas
            * Decimal("100")
        )
        assert lote_completo.margen_pct == expected


@pytest.mark.django_db(transaction=True)
def test_view_cierre_carga(client, admin_e5, lote_completo):
    client.force_login(admin_e5)
    response = client.get(reverse("cierre:cierre_lote", args=[lote_completo.pk]))
    assert response.status_code == 200
    assert b"CH-CIE" in response.content
    assert b"GDP real" in response.content
    assert b"MARGEN BRUTO" in response.content


@pytest.mark.django_db(transaction=True)
def test_view_export_csv(client, admin_e5, lote_completo):
    client.force_login(admin_e5)
    response = client.get(reverse("cierre:cierre_lote_csv", args=[lote_completo.pk]))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert b"COSTO TOTAL" in response.content
    assert b"MARGEN BRUTO" in response.content
    assert b"CH-CIE" in response.content


@pytest.mark.django_db(transaction=True)
def test_anonimo_no_puede_ver_cierre(client, lote_completo):
    response = client.get(reverse("cierre:cierre_lote", args=[lote_completo.pk]))
    assert response.status_code == 302
