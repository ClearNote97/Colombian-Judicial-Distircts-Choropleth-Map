"""Une la jerarquía judicial (con código DANE) a la geometría y agrega por nivel.

El código DANE es la llave: cada municipio judicial hereda el polígono de su
código, y luego se hace ``dissolve`` por unidad JUDICIAL (circuito, distrito).
"""
from __future__ import annotations

import geopandas as gpd
import pandas as pd


def attach_geometry(resolved: pd.DataFrame, geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Pega el polígono de cada código DANE a la jerarquía judicial resuelta.

    Args:
        resolved: salida de ``homologate.resolve`` (district, circuit, municipality, cod_dane).
        geometries: salida de ``ingest.load_municipal_geometries`` (cod_dane + geometry).

    Returns:
        GeoDataFrame a nivel municipio judicial. Los municipios sin geometría
        quedan con ``geometry`` nula (se pueden inspeccionar por separado).
    """
    geo = geometries[["cod_dane", "municipio_dane", "geometry"]].drop_duplicates("cod_dane")
    merged = resolved.merge(geo, on="cod_dane", how="left")
    return gpd.GeoDataFrame(merged, geometry="geometry", crs=geometries.crs)


def missing_geometry(municipios: gpd.GeoDataFrame) -> pd.DataFrame:
    """Municipios judiciales que no encontraron polígono (para control de calidad)."""
    m = municipios[municipios.geometry.isna()]
    return m[["district", "circuit", "municipality", "cod_dane"]].reset_index(drop=True)


def aggregate_levels(municipios: gpd.GeoDataFrame) -> dict[str, gpd.GeoDataFrame]:
    """Genera las capas judiciales: municipio, circuito, distrito (por ``dissolve``)."""
    muni = municipios[municipios.geometry.notna()].copy()

    municipio = muni[
        ["district", "circuit", "municipality", "cod_dane", "municipio_dane", "geometry"]
    ].reset_index(drop=True)

    circuito = (
        muni.dissolve(by=["district", "circuit"], aggfunc={"cod_dane": "count"})
        .rename(columns={"cod_dane": "n_municipios"})
        .reset_index()
    )
    distrito = (
        muni.dissolve(by=["district"], aggfunc={"cod_dane": "count"})
        .rename(columns={"cod_dane": "n_municipios"})
        .reset_index()
    )
    return {"municipio": municipio, "circuito": circuito, "distrito": distrito}
