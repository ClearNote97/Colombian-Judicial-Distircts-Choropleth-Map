"""Escribe los archivos de mapa multinivel (el producto) a ``output/``.

Por cada nivel judicial produce:
- ``.geojson`` con geometría (simplificada) — para Dash, web, SIG.
- ``.topojson`` con topología compartida — para el **Shape Map** de Power BI (compacto,
  sin huecos entre regiones). Clave de enlace: ``cod_dane`` (municipio) o ``district``.
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


def write_topojson(gdf: gpd.GeoDataFrame, path: Path, tolerance: float | None) -> None:
    """Escribe TopoJSON con simplificación topológica (bordes compartidos, sin huecos).

    Conserva las propiedades (``cod_dane``, ``district``, …) como claves de enlace para
    el Shape Map de Power BI.
    """
    import topojson as tp

    topo = tp.Topology(gdf, toposimplify=tolerance) if tolerance else tp.Topology(gdf)
    path.write_text(topo.to_json(), encoding="utf-8")


def write_all(
    levels: dict[str, gpd.GeoDataFrame],
    outdir: Path = config.OUTPUT,
    *,
    tolerance: float | None = config.SIMPLIFY_TOLERANCE,
    prefix: str = config.OUTPUT_PREFIX,
) -> list[Path]:
    """Escribe geojson + topojson + xlsx por nivel. Devuelve las rutas generadas."""
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, gdf in levels.items():
        g = simplify(gdf, tolerance)
        geo_path = outdir / f"{prefix}_{name}.geojson"
        topo_path = outdir / f"{prefix}_{name}.topojson"
        xlsx_path = outdir / f"{prefix}_{name}.xlsx"
        g.to_file(geo_path, driver="GeoJSON")
        write_topojson(gdf, topo_path, tolerance)
        g.drop(columns=g.geometry.name).to_excel(xlsx_path, index=False)
        written.extend([geo_path, topo_path, xlsx_path])
    return written
