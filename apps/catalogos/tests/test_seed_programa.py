import pytest


@pytest.mark.django_db
def test_programa_seeded_at_least_40_rows():
    from apps.catalogos.models import ProgramaReimplante

    assert ProgramaReimplante.objects.count() >= 40


@pytest.mark.django_db
def test_programa_vacas_have_null_origen():
    from apps.catalogos.models import ProgramaReimplante, TipoGanado

    vaca = TipoGanado.objects.get(nombre="Vaca")
    assert (
        ProgramaReimplante.objects.filter(tipo_ganado=vaca, tipo_origen__isnull=True).count() >= 2
    )


@pytest.mark.django_db
def test_machos_corral_has_about_14_rows():
    from apps.catalogos.models import ProgramaReimplante, TipoGanado, TipoOrigen

    macho = TipoGanado.objects.get(nombre="Macho")
    corral = TipoOrigen.objects.get(nombre="Corral")
    count = ProgramaReimplante.objects.filter(tipo_ganado=macho, tipo_origen=corral).count()
    assert 12 <= count <= 16
