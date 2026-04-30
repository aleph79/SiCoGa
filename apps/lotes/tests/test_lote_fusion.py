"""Tests para fusión de lotes (modelo, servicio y vista)."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_b(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(
        username="admin_fus", email="af@x.com", password="p", is_staff=True
    )
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()  # asegura corrales libres
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    c1 = Corral.objects.create(
        clave="CL-F1", nombre="F1", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    c2 = Corral.objects.create(
        clave="CL-F2", nombre="F2", tipo_corral=tipo_corral, capacidad_maxima=300
    )

    a = Lote.objects.create(
        folio="CH-A",
        corral=c1,
        tipo_ganado=macho,
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 1, 1),
        peso_inicial_promedio=Decimal("250.00"),
    )
    b = Lote.objects.create(
        folio="CH-B",
        corral=c2,
        tipo_ganado=macho,
        cabezas_iniciales=80,
        fecha_inicio=date(2026, 1, 1),
        peso_inicial_promedio=Decimal("260.00"),
    )
    return {"a": a, "b": b, "c1": c1, "c2": c2, "macho": macho, "tipo_corral": tipo_corral}


# ----- Modelo -----


def test_fusion_str(setup):
    from apps.lotes.models import LoteFusion

    f = LoteFusion.objects.create(
        lote_destino=setup["b"],
        lote_origen=setup["a"],
        cabezas_movidas=100,
        fecha_fusion=date(2026, 4, 30),
    )
    assert str(f) == "CH-A → CH-B (100 cab.)"


@pytest.mark.django_db(transaction=True)
def test_fusion_destino_distinto_de_origen_db_constraint(setup):
    from django.db import IntegrityError

    from apps.lotes.models import LoteFusion

    with pytest.raises(IntegrityError):
        LoteFusion.objects.create(
            lote_destino=setup["a"],
            lote_origen=setup["a"],
            cabezas_movidas=10,
            fecha_fusion=date(2026, 4, 30),
        )


# ----- Servicio -----


@pytest.mark.django_db(transaction=True)
def test_fusionar_suma_cabezas_y_marca_origen_inactivo(setup):
    from apps.lotes.services import fusionar

    fusionar(destino=setup["b"], origen=setup["a"], fecha_fusion=date(2026, 4, 30))

    setup["a"].refresh_from_db()
    setup["b"].refresh_from_db()
    assert setup["b"].cabezas_iniciales == 180
    assert setup["a"].activo is False


@pytest.mark.django_db(transaction=True)
def test_fusionar_genera_registro(setup):
    from apps.lotes.models import LoteFusion
    from apps.lotes.services import fusionar

    fusionar(destino=setup["b"], origen=setup["a"], fecha_fusion=date(2026, 4, 30))
    assert LoteFusion.objects.filter(lote_destino=setup["b"], lote_origen=setup["a"]).count() == 1


@pytest.mark.django_db(transaction=True)
def test_fusionar_libera_corral_del_origen(setup):
    """Tras fusionar, el corral del origen debe poder aceptar otro lote activo."""
    from apps.lotes.models import Lote
    from apps.lotes.services import fusionar

    fusionar(destino=setup["b"], origen=setup["a"], fecha_fusion=date(2026, 4, 30))

    nuevo = Lote.objects.create(
        folio="CH-NEW",
        corral=setup["c1"],  # mismo corral que tenía 'a'
        tipo_ganado=setup["macho"],
        cabezas_iniciales=50,
        fecha_inicio=date(2026, 5, 1),
        peso_inicial_promedio=Decimal("280.00"),
    )
    assert nuevo.pk


def test_fusionar_origen_inactivo_falla(setup):
    from apps.lotes.services import fusionar

    setup["a"].activo = False
    setup["a"].save()

    with pytest.raises(ValueError, match="origen ya está inactivo"):
        fusionar(destino=setup["b"], origen=setup["a"], fecha_fusion=date(2026, 4, 30))


def test_fusionar_consigo_mismo_falla(setup):
    from apps.lotes.services import fusionar

    with pytest.raises(ValueError, match="consigo mismo"):
        fusionar(destino=setup["a"], origen=setup["a"], fecha_fusion=date(2026, 4, 30))


# ----- Vista -----


@pytest.mark.django_db(transaction=True)
def test_admin_fusiona_via_view(client, admin_b, setup):
    from apps.lotes.models import LoteFusion

    client.force_login(admin_b)
    response = client.post(
        reverse("lotes:lote_fusionar", args=[setup["b"].pk]),
        {
            "lote_origen": setup["a"].pk,
            "fecha_fusion": "2026-04-30",
            "notas": "Junté las dos jaulas",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert LoteFusion.objects.filter(lote_destino=setup["b"]).count() == 1
    setup["b"].refresh_from_db()
    assert setup["b"].cabezas_iniciales == 180


@pytest.mark.django_db(transaction=True)
def test_anonimo_no_puede_fusionar(client, setup):
    response = client.get(reverse("lotes:lote_fusionar", args=[setup["b"].pk]))
    assert response.status_code == 302  # redirect a login
