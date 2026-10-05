"""Mapas de ejemplo/verificación (Plotly), 100% offline.

Usa ``go.Choropleth`` (proyección geográfica, sin tiles ni basemap externo) para que
el HTML funcione sin internet. Cada mapa dibuja:
- una **base gris con la figura completa del país** (para que los municipios sin juzgado
  se vean como vacíos dentro del contorno nacional, no como ausencia total);
- la capa de datos (eficiencia por distrito, o la división por distritos) encima;
- un **inset con zoom al Archipiélago de San Andrés, Providencia y Santa Catalina**,
  que de otro modo quedaría diminuto y lejos del continente.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config, homologate

# Rangos de vista: continente (excluye el archipiélago) e inset del archipiélago.
_MAINLAND_LON = [-79.3, -66.7]
_MAINLAND_LAT = [-4.4, 13.0]
_SA_LON = [-82.0, -81.2]
_SA_LAT = [12.4, 13.5]
_BASE_FILL = "#ededed"
_BASE_LINE = "#c9c9c9"

_DISTRICT_ALIAS = {"ARCH SAN ANDRES": "SAN ANDRES"}


def _district_key(name: str) -> str:
    key = homologate.apply_rules(name)
    return _DISTRICT_ALIAS.get(key, key)


# --------------------------------------------------------------------------- #
# Capas base (figura del país + archipiélago)
# --------------------------------------------------------------------------- #
def _country_outline(geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Contorno del país: une todos los municipios DANE en un polígono (simplificado)."""
    merged = geometries.geometry.simplify(0.01).union_all()
    return gpd.GeoDataFrame({"bid": ["co"]}, geometry=[merged], crs=geometries.crs)


def _archipelago(geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    g = geometries[geometries["cod_dane"].str.startswith("88")].copy()
    g["geometry"] = g.geometry.simplify(0.001)
    return g


def _base_trace(gdf: gpd.GeoDataFrame, id_col: str, geo: str) -> go.Choropleth:
    g = gdf.reset_index(drop=True).copy()
    g["__id"] = g[id_col].astype(str)
    return go.Choropleth(
        geojson=json.loads(g.to_json()),
        locations=g["__id"],
        featureidkey="properties.__id",
        z=[0] * len(g),
        colorscale=[[0, _BASE_FILL], [1, _BASE_FILL]],
        showscale=False,
        marker_line_color=_BASE_LINE,
        marker_line_width=0.3,
        hoverinfo="skip",
        geo=geo,
    )


# --------------------------------------------------------------------------- #
# Trazas de datos
# --------------------------------------------------------------------------- #
def _eff_trace(gdf: gpd.GeoDataFrame, value_col: str, geo: str, showscale: bool) -> go.Choropleth:
    return go.Choropleth(
        geojson=json.loads(gdf.to_json()),
        locations=gdf["key"],
        featureidkey="properties.key",
        z=gdf[value_col],
        text=gdf["district"],
        colorscale="Viridis",
        zmin=config.EFF_ZMIN,
        zmax=config.EFF_ZMAX,
        marker_line_width=0.4,
        marker_line_color="white",
        colorbar_title="Eficiencia",
        showscale=showscale,
        geo=geo,
    )


def _div_trace(gdf: gpd.GeoDataFrame, cats: list[str], colorscale: list, geo: str) -> go.Choropleth:
    n = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    g = gdf.reset_index(drop=True).copy()
    g["fid"] = g.index.astype(str)
    return go.Choropleth(
        geojson=json.loads(g.to_json()),
        locations=g["fid"],
        featureidkey="properties.fid",
        z=[idx[d] for d in g["district"]],
        zmin=0,
        zmax=n,
        colorscale=colorscale,
        showscale=False,
        text=g["district"],
        hoverinfo="text",
        marker_line_width=0.4,
        marker_line_color="white",
        geo=geo,
    )


# --------------------------------------------------------------------------- #
# Composición (continente + inset del archipiélago)
# --------------------------------------------------------------------------- #
def _compose(title: str, traces_main: list, traces_inset: list,
             country: gpd.GeoDataFrame, arch: gpd.GeoDataFrame, out_html: Path | None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(_base_trace(country, "bid", "geo"))
    for t in traces_main:
        fig.add_trace(t)
    fig.add_trace(_base_trace(arch, "cod_dane", "geo2"))
    for t in traces_inset:
        fig.add_trace(t)

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        geo={"visible": False, "projection_type": "mercator",
             "lonaxis_range": _MAINLAND_LON, "lataxis_range": _MAINLAND_LAT,
             "domain": {"x": [0, 1], "y": [0, 1]}},
        geo2={"projection_type": "mercator",
              "lonaxis_range": _SA_LON, "lataxis_range": _SA_LAT,
              "domain": {"x": [0.0, 0.24], "y": [0.56, 0.95]},
              "showframe": True, "framecolor": "#999", "framewidth": 1,
              "showland": False, "showcoastlines": False, "bgcolor": "rgba(255,255,255,0.9)"},
        annotations=[{"text": "San Andrés, Providencia<br>y Santa Catalina",
                      "x": 0.12, "y": 0.96, "xref": "paper", "yref": "paper",
                      "showarrow": False, "font": {"size": 9}, "align": "center"}],
    )
    if out_html:
        fig.write_html(out_html, include_plotlyjs=True)
    return fig


def _prep_efficiency(distrito_gdf: gpd.GeoDataFrame, efficiency: pd.DataFrame, value_col: str) -> gpd.GeoDataFrame:
    g = distrito_gdf.copy()
    g["key"] = g["district"].map(_district_key)
    eff = efficiency.copy()
    eff["key"] = eff["District"].map(_district_key)
    return g.merge(eff[["key", value_col]], on="key", how="left")


def generate_example_maps(
    distrito_gdf: gpd.GeoDataFrame,
    geometries: gpd.GeoDataFrame,
    outdir: Path = config.OUTPUT,
) -> list[Path]:
    """Mapas de ejemplo: eficiencia (municipal/circuito) + división por distritos."""
    from . import ingest

    country = _country_outline(geometries)
    arch = _archipelago(geometries)
    is_sa = distrito_gdf["district"] == "ARCH SAN ANDRES"
    written: list[Path] = []

    for db_path, title, fname, value_col in [
        (config.DB_MUNICIPAL, "Eficiencia promedio — Juzgados Penales Municipales (2012–2016)",
         "choropleth_eficiencia_municipal.html", "AVG_Eff"),
        (config.DB_CIRCUIT, "Eficiencia promedio — Juzgados Penales del Circuito (2012–2016)",
         "choropleth_eficiencia_circuito.html", "AVG_Eff"),
    ]:
        if not db_path.exists():
            continue
        g = _prep_efficiency(distrito_gdf, ingest.load_efficiency(db_path), value_col)
        main = [_eff_trace(g, value_col, "geo", showscale=True)]
        inset = [_eff_trace(g[g["district"] == "ARCH SAN ANDRES"], value_col, "geo2", showscale=False)]
        out = outdir / fname
        _compose(title, main, inset, country, arch, out)
        written.append(out)

    # División por distritos judiciales (categórico)
    cats = sorted(distrito_gdf["district"].unique())
    base = px.colors.qualitative.Light24
    colorscale: list = []
    for i in range(len(cats)):
        c = base[i % len(base)]
        colorscale += [[i / len(cats), c], [(i + 1) / len(cats), c]]
    main = [_div_trace(distrito_gdf, cats, colorscale, "geo")]
    inset = [_div_trace(distrito_gdf[is_sa], cats, colorscale, "geo2")]
    out = outdir / "mapa_distritos_judiciales.html"
    _compose("División por Distritos Judiciales de Colombia", main, inset, country, arch, out)
    written.append(out)
    return written
