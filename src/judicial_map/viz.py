"""Mapas de ejemplo/verificación (Plotly), 100% offline.

Usa ``go.Choropleth`` / ``px.choropleth`` (proyección geográfica, **sin tiles ni
basemap externo**): dibuja los polígonos directo del GeoJSON, así el HTML funciona
sin internet y sin WebGL/MapLibre (que quedaba en blanco al abrir el archivo).

- Choropleths de **eficiencia** por distrito (datos de ejemplo DB1/DB2).
- Mapa de la **división por distritos judiciales** (categórico) — el nivel distrito del producto.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config, homologate

# El nombre del distrito en el PDF vs en los datos de eficiencia solo difiere en
# tildes/abreviaturas (que apply_rules normaliza), salvo este alias.
_DISTRICT_ALIAS = {"ARCH SAN ANDRES": "SAN ANDRES"}


def _district_key(name: str) -> str:
    key = homologate.apply_rules(name)
    return _DISTRICT_ALIAS.get(key, key)


def _fit(fig: go.Figure, title: str) -> go.Figure:
    """Ajusta la vista a los polígonos, oculta el globo base y pone el título."""
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title_text=title, title_x=0.5, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig


def build_efficiency_map(
    distrito_gdf: gpd.GeoDataFrame,
    efficiency: pd.DataFrame,
    *,
    value_col: str = "AVG_Eff",
    title: str = "",
    out_html: Path | None = None,
) -> go.Figure:
    """Choropleth de distritos judiciales coloreados por eficiencia (continuo)."""
    g = distrito_gdf.copy()
    g["key"] = g["district"].map(_district_key)
    eff = efficiency.copy()
    eff["key"] = eff["District"].map(_district_key)
    g = g.merge(eff[["key", value_col]], on="key", how="left")

    fig = go.Figure(
        go.Choropleth(
            geojson=json.loads(g.to_json()),
            locations=g["key"],
            featureidkey="properties.key",
            z=g[value_col],
            text=g["district"],
            colorscale="Viridis",
            zmin=config.EFF_ZMIN,
            zmax=config.EFF_ZMAX,
            marker_line_width=0.4,
            marker_line_color="white",
            colorbar_title="Eficiencia",
        )
    )
    _fit(fig, title)
    if out_html:
        fig.write_html(out_html, include_plotlyjs=True)
    return fig


def build_division_map(
    gdf: gpd.GeoDataFrame,
    *,
    name_col: str,
    title: str = "",
    out_html: Path | None = None,
) -> go.Figure:
    """Mapa categórico de la división judicial (cada unidad con su color).

    Un solo trace ``go.Choropleth`` con colorscale discreto (evita que px duplique
    el GeoJSON por categoría) -> HTML liviano y offline.
    """
    g = gdf.reset_index(drop=True).copy()
    g["fid"] = g.index.astype(str)
    n = len(g)
    base = px.colors.qualitative.Light24
    palette = [base[i % len(base)] for i in range(n)]
    colorscale: list = []
    for i, color in enumerate(palette):
        colorscale += [[i / n, color], [(i + 1) / n, color]]

    fig = go.Figure(
        go.Choropleth(
            geojson=json.loads(g.to_json()),
            locations=g["fid"],
            featureidkey="properties.fid",
            z=list(range(n)),
            zmin=0,
            zmax=n,
            colorscale=colorscale,
            showscale=False,
            text=g[name_col].astype(str),
            hoverinfo="text",
            marker_line_width=0.4,
            marker_line_color="white",
        )
    )
    _fit(fig, title)
    if out_html:
        fig.write_html(out_html, include_plotlyjs=True)
    return fig


def generate_example_maps(distrito_gdf: gpd.GeoDataFrame, outdir: Path = config.OUTPUT) -> list[Path]:
    """Genera los mapas de ejemplo: eficiencia (municipal/circuito) + división por distritos."""
    from . import ingest

    written: list[Path] = []
    eff_specs = [
        (config.DB_MUNICIPAL, "Eficiencia promedio — Juzgados Penales Municipales (2012–2016)",
         "choropleth_eficiencia_municipal.html"),
        (config.DB_CIRCUIT, "Eficiencia promedio — Juzgados Penales del Circuito (2012–2016)",
         "choropleth_eficiencia_circuito.html"),
    ]
    for db_path, title, fname in eff_specs:
        if db_path.exists():
            out = outdir / fname
            build_efficiency_map(distrito_gdf, ingest.load_efficiency(db_path), title=title, out_html=out)
            written.append(out)

    # Nivel distrito del producto: la división judicial como tal.
    out = outdir / "mapa_distritos_judiciales.html"
    build_division_map(distrito_gdf, name_col="district",
                       title="División por Distritos Judiciales de Colombia", out_html=out)
    written.append(out)
    return written
