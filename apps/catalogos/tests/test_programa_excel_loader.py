"""Tests for the Excel reader that produces programa rows."""

from pathlib import Path


def test_loader_reads_machos_section():
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    path = Path("docs/DISPONIBILIDAD 2026 1.xlsx")
    rows = leer_programa_excel(path)
    machos = [r for r in rows if r["categoria"] == "MACHOS"]
    assert len(machos) >= 13
    assert all(r["peso_min"] is not None and r["peso_max"] is not None for r in machos)


def test_loader_reads_vacas_with_null_origen():
    from apps.catalogos.seeds.programa_excel import leer_programa_excel

    path = Path("docs/DISPONIBILIDAD 2026 1.xlsx")
    rows = leer_programa_excel(path)
    vacas = [r for r in rows if r["categoria"] == "VACAS"]
    assert len(vacas) == 2
    assert all(r["tipo_origen"] is None for r in vacas)
