"""Mapas de ejemplo/verificación en **matplotlib** (PNG + PDF).

Se usa matplotlib (no plotly) porque plotly.js no renderiza en el navegador las
geometrías de las áreas no municipalizadas de la Amazonía (dejaba el mapa en blanco);
matplotlib las dibuja sin problema y, además, produce figuras estáticas de alta
calidad listas para publicaciones.

Cada mapa dibuja:
- la **figura completa del país** (todos los municipios) en gris de fondo;
- los **distritos judiciales** coloreados por la eficiencia de sus juzgados (Viridis);
- **distrito sin dato -> negro**; **municipio sin juzgado -> gris** (queda el fondo);
- un **inset con zoom al Archipiélago de San Andrés, Providencia y Santa Catalina**.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.cm import ScalarMappable  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from . import config, homologate  # noqa: E402

_NODATA = "black"
_BASE = "#ededed"
_BASE_EDGE = "#cfcfcf"
_CMAP = "viridis"
_SA_DISTRICT = "ARCH SAN ANDRES"
_DISTRICT_ALIAS = {_SA_DISTRICT: "SAN ANDRES"}


def _district_key(name: str) -> str:
    key = homologate.apply_rules(name)
    return _DISTRICT_ALIAS.get(key, key)


def _prep_efficiency(distrito_gdf: gpd.GeoDataFrame, efficiency: pd.DataFrame, value_col: str) -> gpd.GeoDataFrame:
    g = distrito_gdf.copy()
    g["key"] = g["district"].map(_district_key)
    eff = efficiency.copy()
    eff["key"] = eff["District"].map(_district_key)
    return g.merge(eff[["key", value_col]], on="key", how="left")


def _mainland(geometries: gpd.GeoDataFrame, tol: float = 0.008) -> gpd.GeoDataFrame:
    g = geometries[~geometries["cod_dane"].str.startswith("88")].copy()
    g["geometry"] = g.geometry.simplify(tol)
    return g


def _inset_islands(geometries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """San Andrés (88001) y Providencia (88564) agrandadas y acercadas para el inset.

    NO respeta la distancia real: escala las islas y apila Providencia justo encima
    de San Andrés, para que se vean grandes y juntas en una caja compacta.
    """
    from shapely.affinity import scale, translate

    g = geometries[geometries["cod_dane"].str.startswith("88")].copy()
    g["geometry"] = g.geometry.simplify(0.001)
    sa = g.loc[g["cod_dane"] == "88001", "geometry"].iloc[0]
    pr = g.loc[g["cod_dane"] == "88564", "geometry"].iloc[0]
    factor, gap = 3.5, 0.28
    sa = scale(sa, factor, factor, origin=sa.centroid)
    pr = scale(pr, factor, factor, origin=pr.centroid)
    pr = translate(pr, xoff=sa.centroid.x - pr.centroid.x,
                   yoff=(sa.centroid.y + gap) - pr.centroid.y)
    return gpd.GeoDataFrame({"cod_dane": ["88001", "88564"]}, geometry=[sa, pr], crs=g.crs)


def _draw_inset(ax, islands: gpd.GeoDataFrame, **plot_kw) -> None:
    axins = ax.inset_axes([0.02, 0.72, 0.15, 0.24])
    islands.plot(ax=axins, edgecolor="white", linewidth=0.5, **plot_kw)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_xlabel("")
    axins.set_ylabel("")
    axins.margins(0.12)
    axins.set_title("San Andrés y\nProvidencia", fontsize=7)


def build_efficiency_map(distrito_gdf, geometries, efficiency, title: str, out_png: Path) -> None:
    """Choropleth de distritos por eficiencia, sobre la figura del país, con inset."""
    g = _prep_efficiency(distrito_gdf, efficiency, "AVG_Eff")
    is_sa = (g["district"] == _SA_DISTRICT).values
    main, sa = g[~is_sa], g[is_sa]
    base = _mainland(geometries)

    fig, ax = plt.subplots(figsize=(11, 11))
    base.plot(ax=ax, color=_BASE, edgecolor=_BASE_EDGE, linewidth=0.2)
    main[main["AVG_Eff"].notna()].plot(
        column="AVG_Eff", cmap=_CMAP, vmin=config.EFF_ZMIN, vmax=config.EFF_ZMAX,
        ax=ax, edgecolor="white", linewidth=0.4,
    )
    if main["AVG_Eff"].isna().any():
        main[main["AVG_Eff"].isna()].plot(ax=ax, color=_NODATA, edgecolor="white", linewidth=0.4)
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, pad=10)

    sm = ScalarMappable(cmap=_CMAP, norm=Normalize(config.EFF_ZMIN, config.EFF_ZMAX))
    sm.set_array([])
    fig.colorbar(sm, ax=ax, shrink=0.45, pad=0.01, label="Eficiencia promedio")
    ax.legend(
        handles=[Patch(facecolor=_NODATA, edgecolor="white", label="Distrito sin dato de eficiencia"),
                 Patch(facecolor=_BASE, edgecolor=_BASE_EDGE, label="Municipio sin juzgado")],
        loc="lower left", fontsize=9, frameon=False,
    )

    eff = sa["AVG_Eff"].iloc[0] if len(sa) else None
    if eff is not None and pd.notna(eff):
        color = matplotlib.colormaps[_CMAP](Normalize(config.EFF_ZMIN, config.EFF_ZMAX)(eff))
    else:
        color = _NODATA
    _draw_inset(ax, _inset_islands(geometries), color=color)
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_png.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def build_division_map(distrito_gdf, geometries, out_png: Path) -> None:
    """Mapa categórico de la división judicial, sobre la figura del país, con inset."""
    is_sa = (distrito_gdf["district"] == _SA_DISTRICT).values
    base = _mainland(geometries)

    fig, ax = plt.subplots(figsize=(11, 11))
    base.plot(ax=ax, color=_BASE, edgecolor=_BASE_EDGE, linewidth=0.2)
    distrito_gdf[~is_sa].plot(column="district", categorical=True, cmap="tab20",
                              ax=ax, edgecolor="white", linewidth=0.5)
    ax.set_axis_off()
    ax.set_title("División por Distritos Judiciales de Colombia", fontsize=13, pad=10)

    _draw_inset(ax, _inset_islands(geometries), color="#4c78a8")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_png.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def generate_example_maps(distrito_gdf, geometries, outdir: Path = config.OUTPUT) -> list[Path]:
    """Genera los mapas de ejemplo (PNG + PDF): eficiencia + división por distritos."""
    from . import ingest

    written: list[Path] = []
    for db_path, title, fname in [
        (config.DB_MUNICIPAL, "Eficiencia promedio — Juzgados Penales Municipales (2012–2016)",
         "choropleth_eficiencia_municipal.png"),
        (config.DB_CIRCUIT, "Eficiencia promedio — Juzgados Penales del Circuito (2012–2016)",
         "choropleth_eficiencia_circuito.png"),
    ]:
        if db_path.exists():
            out = outdir / fname
            build_efficiency_map(distrito_gdf, geometries, ingest.load_efficiency(db_path), title, out)
            written += [out, out.with_suffix(".pdf")]

    out = outdir / "mapa_distritos_judiciales.png"
    build_division_map(distrito_gdf, geometries, out)
    written += [out, out.with_suffix(".pdf")]
    return written
