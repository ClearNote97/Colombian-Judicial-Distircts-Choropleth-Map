"""Tests de merge: geometría por código DANE y agregación por nivel judicial."""
from judicial_map import merge


def test_levels(resolution, geometries):
    muni = merge.attach_geometry(resolution.resolved, geometries)
    levels = merge.aggregate_levels(muni)

    assert levels["distrito"].shape[0] == 33
    assert levels["circuito"].shape[0] > 190
    assert levels["municipio"].shape[0] >= 1100

    # cada distrito y circuito tiene geometría válida
    assert levels["distrito"].geometry.notna().all()
    assert levels["circuito"].geometry.notna().all()

    # los conteos de municipios por distrito suman ~la jerarquía con geometría
    total = levels["distrito"]["n_municipios"].sum()
    assert total >= 1100


def test_missing_geometry_is_small(resolution, geometries):
    muni = merge.attach_geometry(resolution.resolved, geometries)
    assert len(merge.missing_geometry(muni)) <= 5
