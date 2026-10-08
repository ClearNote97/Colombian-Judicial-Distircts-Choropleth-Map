"""Tests de ingesta: jerarquía del PDF y DIVIPOLA."""


def test_hierarchy_has_all_municipios(hierarchy):
    # regresión: el filtro por número de municipio botaba ~314 filas (camelot deja
    # vacío ese número en ~1/3 de las páginas). Debe haber ~1100 municipios.
    assert len(hierarchy) >= 1100
    assert hierarchy["district"].nunique() == 33
    assert {"district", "circuit", "municipality"} <= set(hierarchy.columns)
    assert hierarchy["municipality"].notna().all()


def test_divipola_codes(divipola):
    assert len(divipola) > 1100
    assert (divipola["cod_dane"].str.len() == 5).all()
    assert (divipola["cod_depto"].str.len() == 2).all()
    # las capitales terminan en 001 (una por departamento)
    assert (divipola["cod_dane"].str[-3:] == "001").sum() >= 32
