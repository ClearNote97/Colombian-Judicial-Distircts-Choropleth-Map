"""Mapas de ejemplo/verificación (Plotly), 100% offline.

Usa ``go.Choropleth`` (proyección geográfica, sin tiles ni basemap externo) con
``fitbounds="locations"`` para encuadrar automáticamente. Cada mapa dibuja:
- una **base gris con la figura del país** (continente), para que los municipios sin
  juzgado se vean como vacíos dentro del contorno nacional;
- la capa de datos (eficiencia por distrito, o la división por distritos) encima;
- un **inset con zoom al Archipiélago de San Andrés, Providencia y Santa Catalina**.

El continente y el archipiélago van en subplots geo separados (el archipiélago está
lejos del continente y lo achicaría todo si fueran el mismo encuadre).
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config, homologate

_BASE_FILL = "#ededed"       # sin juzgado: municipio que NO está en el Mapa Judicial
_BASE_LINE = "#c9c9c9"
_NODATA_FILL = "#a6bddb"     # distrito EN el Mapa Judicial pero sin dato de eficiencia
_INSET_DOMAIN = {"x": [0.0, 0.24], "y": [0.55, 0.95]}
_SA_DISTRICT = "ARCH SAN ANDRES"
_DISTRICT_ALIAS = {_SA_DISTRICT: "SAN ANDRES"}


def _district_key(name: str) -> str:
    key = homologate.apply_rules(name)
    return _DISTRICT_ALIAS.get(key, key)


# --------------------------------------------------------------------------- #
# Capas base
# --------------------------------------------------------------------------- #
def _mainland_outline(geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Contorno del país continental (excluye el archipiélago, dpto 88)."""
    g = geometries[~geometries["cod_dane"].str.startswith("88")]
    merged = g.geometry.simplify(0.01).union_all()
    return gpd.GeoDataFrame({"bid": ["co"]}, geometry=[merged], crs=geometries.crs)


def _archipelago(geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    g = geometries[geometries["cod_dane"].str.startswith("88")].copy()
    g["geometry"] = g.geometry.simplify(0.001)
    return g


def _base_trace(gdf: gpd.GeoDataFrame, id_col: str, geo: str) -> go.Choropleth:
    g = gdf.reset_index(drop=True).copy()
    g["__id"] = g[id_col].astype(str)
    return go.Choropleth(
        geojson=json.loads(g.to_json()), locations=g["__id"], featureidkey="properties.__id",
        z=[0] * len(g), colorscale=[[0, _BASE_FILL], [1, _BASE_FILL]], showscale=False,
        marker_line_color=_BASE_LINE, marker_line_width=0.3, hoverinfo="skip", geo=geo,
    )


def _nodata_trace(gdf: gpd.GeoDataFrame, geo: str) -> go.Choropleth:
    """Distritos que están en el Mapa Judicial pero no tienen dato de eficiencia."""
    g = gdf.reset_index(drop=True).copy()
    g["fid"] = g.index.astype(str)
    return go.Choropleth(
        geojson=json.loads(g.to_json()), locations=g["fid"], featureidkey="properties.fid",
        z=[0] * len(g), colorscale=[[0, _NODATA_FILL], [1, _NODATA_FILL]], showscale=False,
        marker_line_color="white", marker_line_width=0.4,
        text=g["district"], hoverinfo="text", geo=geo,
    )


# --------------------------------------------------------------------------- #
# Trazas de datos
# --------------------------------------------------------------------------- #
def _eff_trace(gdf: gpd.GeoDataFrame, value_col: str, geo: str, showscale: bool) -> go.Choropleth:
    return go.Choropleth(
        geojson=json.loads(gdf.to_json()), locations=gdf["key"], featureidkey="properties.key",
        z=gdf[value_col], text=gdf["district"], colorscale="Viridis",
        zmin=config.EFF_ZMIN, zmax=config.EFF_ZMAX,
        marker_line_width=0.4, marker_line_color="white",
        colorbar_title="Eficiencia", showscale=showscale, geo=geo,
    )


def _div_trace(gdf: gpd.GeoDataFrame, cats: list[str], colorscale: list, geo: str) -> go.Choropleth:
    idx = {c: i for i, c in enumerate(cats)}
    g = gdf.reset_index(drop=True).copy()
    g["fid"] = g.index.astype(str)
    return go.Choropleth(
        geojson=json.loads(g.to_json()), locations=g["fid"], featureidkey="properties.fid",
        z=[idx[d] for d in g["district"]], zmin=0, zmax=len(cats), colorscale=colorscale,
        showscale=False, text=g["district"], hoverinfo="text",
        marker_line_width=0.4, marker_line_color="white", geo=geo,
    )


# --------------------------------------------------------------------------- #
# Composición (continente + inset)
# --------------------------------------------------------------------------- #
def _compose(title: str, traces_main: list, traces_inset: list, out_html: Path | None,
             legend_items: list[tuple[str, str]] | None = None) -> go.Figure:
    fig = go.Figure()
    for t in traces_main + traces_inset:
        fig.add_trace(t)

    shapes = [{"type": "rect", "xref": "paper", "yref": "paper",
               "x0": _INSET_DOMAIN["x"][0], "x1": _INSET_DOMAIN["x"][1],
               "y0": _INSET_DOMAIN["y"][0], "y1": _INSET_DOMAIN["y"][1],
               "line": {"color": "#999", "width": 1}}]
    annotations = [{"text": "San Andrés, Providencia<br>y Santa Catalina",
                    "x": sum(_INSET_DOMAIN["x"]) / 2, "y": _INSET_DOMAIN["y"][1] + 0.02,
                    "xref": "paper", "yref": "paper", "showarrow": False,
                    "font": {"size": 9}, "align": "center"}]
    for i, (color, label) in enumerate(legend_items or []):
        y = 0.03 + i * 0.05
        shapes.append({"type": "rect", "xref": "paper", "yref": "paper",
                       "x0": 0.02, "x1": 0.035, "y0": y, "y1": y + 0.03,
                       "fillcolor": color, "line": {"color": "#999", "width": 0.5}})
        annotations.append({"text": label, "x": 0.042, "y": y + 0.015,
                            "xref": "paper", "yref": "paper", "showarrow": False,
                            "xanchor": "left", "font": {"size": 10}})

    fig.update_layout(
        title_text=title, title_x=0.5, margin={"r": 0, "t": 40, "l": 0, "b": 0},
        geo={"visible": False, "fitbounds": "locations", "domain": {"x": [0, 1], "y": [0, 1]}},
        geo2={"visible": False, "fitbounds": "locations", "domain": _INSET_DOMAIN,
              "bgcolor": "rgba(0,0,0,0)"},
        shapes=shapes, annotations=annotations,
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

    mainland = _mainland_outline(geometries)
    arch = _archipelago(geometries)
    is_sa = distrito_gdf["district"] == _SA_DISTRICT
    written: list[Path] = []

    for db_path, title, fname in [
        (config.DB_MUNICIPAL, "Eficiencia promedio — Juzgados Penales Municipales (2012–2016)",
         "choropleth_eficiencia_municipal.html"),
        (config.DB_CIRCUIT, "Eficiencia promedio — Juzgados Penales del Circuito (2012–2016)",
         "choropleth_eficiencia_circuito.html"),
    ]:
        if not db_path.exists():
            continue
        g = _prep_efficiency(distrito_gdf, ingest.load_efficiency(db_path), "AVG_Eff")
        gm = g[~is_sa.values]
        gm_data = gm[gm["AVG_Eff"].notna()]
        gm_nodata = gm[gm["AVG_Eff"].isna()]
        main = [_base_trace(mainland, "bid", "geo")]
        if len(gm_nodata):
            main.append(_nodata_trace(gm_nodata, "geo"))
        main.append(_eff_trace(gm_data, "AVG_Eff", "geo", showscale=True))
        inset = [_base_trace(arch, "cod_dane", "geo2"),
                 _eff_trace(g[is_sa.values], "AVG_Eff", "geo2", showscale=False)]
        legend = [(_BASE_FILL, "Municipio sin juzgado"),
                  (_NODATA_FILL, "Distrito sin dato de eficiencia")]
        out = outdir / fname
        _compose(title, main, inset, out, legend_items=legend)
        written.append(out)

    cats = sorted(distrito_gdf["district"].unique())
    base = px.colors.qualitative.Light24
    colorscale: list = []
    for i in range(len(cats)):
        c = base[i % len(base)]
        colorscale += [[i / len(cats), c], [(i + 1) / len(cats), c]]
    main = [_base_trace(mainland, "bid", "geo"),
            _div_trace(distrito_gdf[~is_sa], cats, colorscale, "geo")]
    inset = [_base_trace(arch, "cod_dane", "geo2"),
             _div_trace(distrito_gdf[is_sa], cats, colorscale, "geo2")]
    out = outdir / "mapa_distritos_judiciales.html"
    _compose("División por Distritos Judiciales de Colombia", main, inset, out)
    written.append(out)
    return written
