"""Tests para la pantalla de Disponibilidad."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.fixture
def admin_c(db):
    group, _ = Group.objects.get_or_create(name="Administrador")
    group.permissions.set(Permission.objects.all())
    u = User.objects.create_user(username="admin_c", email="ac@x.com", password="p", is_staff=True)
    u.groups.add(group)
    return u


@pytest.fixture
def setup(db):
    from apps.catalogos.models import Corral, ProgramaReimplante, TipoCorral, TipoGanado
    from apps.lotes.models import Lote

    ProgramaReimplante.objects.all().delete()
    Lote.objects.all().delete()

    macho = TipoGanado.objects.get_or_create(nombre="Macho")[0]
    hembra = TipoGanado.objects.get_or_create(nombre="Hembra")[0]
    tipo_corral = TipoCorral.objects.get_or_create(nombre="Engorda")[0]

    c1 = Corral.objects.create(
        clave="CL-D1", nombre="D1", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    c2 = Corral.objects.create(
        clave="CL-D2", nombre="D2", tipo_corral=tipo_corral, capacidad_maxima=300
    )
    c3_libre = Corral.objects.create(
        clave="CL-D3", nombre="D3 Libre", tipo_corral=tipo_corral, capacidad_maxima=300
    )

    Lote.objects.create(
        folio="CH-D1",
        corral=c1,
        tipo_ganado=macho,
        cabezas_iniciales=200,
        fecha_inicio=date.today() - timedelta(days=30),
        peso_inicial_promedio=Decimal("250.00"),
        peso_salida_objetivo=Decimal("580.00"),
        gdp_esperada=Decimal("1.30"),
    )
    Lote.objects.create(
        folio="CH-D2",
        corral=c2,
        tipo_ganado=hembra,
        cabezas_iniciales=150,
        fecha_inicio=date.today() - timedelta(days=10),
        peso_inicial_promedio=Decimal("220.00"),
        peso_salida_objetivo=Decimal("540.00"),
        gdp_esperada=Decimal("1.20"),
    )
    return {"macho": macho, "hembra": hembra, "c1": c1, "c2": c2, "c3_libre": c3_libre}


@pytest.mark.django_db(transaction=True)
def test_anonimo_redirige_a_login(client):
    response = client.get(reverse("disponibilidad:home"))
    assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_root_redirige_a_disponibilidad(client, admin_c):
    client.force_login(admin_c)
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/disponibilidad/"


@pytest.mark.django_db(transaction=True)
def test_home_carga_con_2_lotes_activos(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:home"))
    assert response.status_code == 200
    assert b"CH-D1" in response.content
    assert b"CH-D2" in response.content


@pytest.mark.django_db(transaction=True)
def test_kpi_lotes_activos_correcto(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:home"))
    # 2 lotes activos
    assert b">2<" in response.content or b"2</div>" in response.content


@pytest.mark.django_db(transaction=True)
def test_filtro_tipo_ganado(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:home"), {"tipo_ganado": setup["macho"].pk})
    assert response.status_code == 200
    assert b"CH-D1" in response.content
    # CH-D2 es Hembra, no debe aparecer
    assert b"CH-D2" not in response.content


@pytest.mark.django_db(transaction=True)
def test_libres_no_se_muestran_por_default(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:home"))
    # CL-D3 está libre, no debe aparecer
    assert b"CL-D3" not in response.content


@pytest.mark.django_db(transaction=True)
def test_libres_se_muestran_con_filtro(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:home"), {"ver_libres": "1"})
    assert response.status_code == 200
    assert b"CL-D3" in response.content
    assert b"Libre" in response.content


@pytest.mark.django_db(transaction=True)
def test_export_csv(client, admin_c, setup):
    client.force_login(admin_c)
    response = client.get(reverse("disponibilidad:export_csv"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert b"Corral,Lote,Tipo" in response.content
    assert b"CH-D1" in response.content
    assert b"CH-D2" in response.content
    assert b"Libre" in response.content  # CL-D3
