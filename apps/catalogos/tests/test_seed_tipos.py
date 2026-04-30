import pytest


@pytest.mark.django_db
def test_tipo_corral_seeded():
    from apps.catalogos.models import TipoCorral

    nombres = set(TipoCorral.objects.values_list("nombre", flat=True))
    assert {"Recepción", "Engorda", "Zilpaterol"}.issubset(nombres)


@pytest.mark.django_db
def test_tipo_ganado_seeded():
    from apps.catalogos.models import TipoGanado

    nombres = set(TipoGanado.objects.values_list("nombre", flat=True))
    assert {"Macho", "Hembra", "Vaca"}.issubset(nombres)


@pytest.mark.django_db
def test_tipo_origen_seeded():
    from apps.catalogos.models import TipoOrigen

    nombres = set(TipoOrigen.objects.values_list("nombre", flat=True))
    assert {"Corral", "Potrero"}.issubset(nombres)
