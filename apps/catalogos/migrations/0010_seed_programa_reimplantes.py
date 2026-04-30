"""Seed ProgramaReimplante from docs/DISPONIBILIDAD 2026 1.xlsx."""

from pathlib import Path

from django.conf import settings
from django.db import migrations


def forwards(apps, schema_editor):
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    TipoGanado = apps.get_model("catalogos", "TipoGanado")
    TipoOrigen = apps.get_model("catalogos", "TipoOrigen")
    ProgramaReimplante = apps.get_model("catalogos", "ProgramaReimplante")

    path = Path(settings.BASE_DIR) / "docs" / "DISPONIBILIDAD 2026 1.xlsx"
    if not path.exists():
        return

    rows = leer_programa_excel(path)

    cache_ganado = {t.nombre: t for t in TipoGanado.objects.all()}
    cache_origen = {t.nombre: t for t in TipoOrigen.objects.all()}

    for r in rows:
        ProgramaReimplante.objects.create(
            tipo_ganado=cache_ganado[r["tipo_ganado"]],
            tipo_origen=cache_origen.get(r["tipo_origen"]) if r["tipo_origen"] else None,
            peso_min=r["peso_min"],
            peso_max=r["peso_max"],
            gdp_esperada=r["gdp_esperada"],
            peso_objetivo_salida=r["peso_objetivo_salida"],
            implante_inicial=r["implante_inicial"],
            reimplante_1=r["reimplante_1"],
            reimplante_2=r["reimplante_2"],
            reimplante_3=r["reimplante_3"],
            reimplante_4=r["reimplante_4"],
            dias_recepcion=r["dias_recepcion"],
            dias_f1=r["dias_f1"],
            dias_transicion=r["dias_transicion"],
            dias_f3=r["dias_f3"],
            dias_zilpaterol=r["dias_zilpaterol"],
        )


def backwards(apps, schema_editor):
    ProgramaReimplante = apps.get_model("catalogos", "ProgramaReimplante")
    ProgramaReimplante.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("catalogos", "0009_seed_tipo_origen")]
    operations = [migrations.RunPython(forwards, backwards)]
