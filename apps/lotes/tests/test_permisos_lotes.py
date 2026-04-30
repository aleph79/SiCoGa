"""Tests de permisos por rol sobre Lote y LoteFusion."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def capturista(db):
    group, _ = Group.objects.get_or_create(name="Capturista")
    perms = Permission.objects.filter(
        codename__in={
            "view_tipocorral",
            "view_tipoganado",
            "view_tipoorigen",
            "view_proveedor",
            "view_corral",
            "view_programareimplante",
            "add_lote",
            "change_lote",
            "view_lote",
            "add_lotefusion",
            "view_lotefusion",
        }
    )
    group.permissions.set(perms)
    u = User.objects.create_user(username="capt_b", email="cb@x.com", password="p")
    u.groups.add(group)
    return u


@pytest.fixture
def lectura(db):
    group, _ = Group.objects.get_or_create(name="Solo Lectura")
    view_perms = Permission.objects.filter(codename__startswith="view_")
    group.permissions.set(view_perms)
    u = User.objects.create_user(username="lec_b", email="lb@x.com", password="p")
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()
    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]
    c = Corral.objects.create(
        clave="CL-PER", nombre="Per", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    lote = Lote.objects.create(
        folio="CH-PER",
        corral=c,
        tipo_ganado=macho,
        cabezas_iniciales=100,
        fecha_inicio=date(2026, 4, 30),
        peso_inicial_promedio=Decimal("250.00"),
    )
    return {"corral": c, "lote": lote, "macho": macho, "tipo_corral": tipo_corral}


@pytest.mark.django_db(transaction=True)
def test_capturista_puede_listar(client, capturista):
    client.force_login(capturista)
    assert client.get(reverse("lotes:lote_list")).status_code == 200


@pytest.mark.django_db(transaction=True)
def test_capturista_puede_crear(client, capturista, setup):
    from apps.catalogos.models import Corral

    libre = Corral.objects.create(
        clave="CL-LIBRE",
        nombre="Libre",
        tipo_corral=setup["tipo_corral"],
        capacidad_maxima=100,
    )
    client.force_login(capturista)
    response = client.post(
        reverse("lotes:lote_create"),
        {
            "folio": "CH-CAPT",
            "corral": libre.pk,
            "tipo_ganado": setup["macho"].pk,
            "cabezas_iniciales": "50",
            "fecha_inicio": "2026-04-30",
            "peso_inicial_promedio": "250.00",
            "peso_salida_objetivo": "580.00",
            "gdp_esperada": "1.30",
            "activo": "on",
        },
    )
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_capturista_no_puede_eliminar(client, capturista, setup):
    client.force_login(capturista)
    response = client.get(reverse("lotes:lote_delete", args=[setup["lote"].pk]))
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_capturista_puede_fusionar(client, capturista, setup):
    client.force_login(capturista)
    response = client.get(reverse("lotes:lote_fusionar", args=[setup["lote"].pk]))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_lectura_puede_ver(client, lectura, setup):
    client.force_login(lectura)
    assert client.get(reverse("lotes:lote_list")).status_code == 200


@pytest.mark.django_db(transaction=True)
def test_lectura_no_puede_crear(client, lectura):
    client.force_login(lectura)
    assert client.get(reverse("lotes:lote_create")).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_lectura_no_puede_fusionar(client, lectura, setup):
    client.force_login(lectura)
    assert client.get(reverse("lotes:lote_fusionar", args=[setup["lote"].pk])).status_code == 403
