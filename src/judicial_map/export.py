"""Escribe los archivos de mapa multinivel (el producto) a ``output/``.

Por cada nivel judicial produce:
- ``.geojson`` con geometría (simplificada) — para Dash, web, SIG.
- ``.xlsx`` con los atributos (sin geometría) — para Power BI, Excel, joins.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from . import config


def simplify(gdf: gpd.GeoDataFrame, tolerance: float | None) -> gpd.GeoDataFrame:
    """Simplifica la geometría preservando topología por polígono (aligera salida)."""
    if not tolerance:
        return gdf
    out = gdf.copy()
    out["geometry"] = out.geometry.simplify(tolerance, preserve_topology=True)
    return out


def write_all(
    levels: dict[str, gpd.GeoDataFrame],
    outdir: Path = config.OUTPUT,
    *,
    tolerance: float | None = config.SIMPLIFY_TOLERANCE,
    prefix: str = config.OUTPUT_PREFIX,
) -> list[Path]:
    """Escribe geojson + xlsx por nivel. Devuelve las rutas generadas."""
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, gdf in levels.items():
        g = simplify(gdf, tolerance)
        geo_path = outdir / f"{prefix}_{name}.geojson"
        xlsx_path = outdir / f"{prefix}_{name}.xlsx"
        g.to_file(geo_path, driver="GeoJSON")
        g.drop(columns=g.geometry.name).to_excel(xlsx_path, index=False)
        written.extend([geo_path, xlsx_path])
    return written
