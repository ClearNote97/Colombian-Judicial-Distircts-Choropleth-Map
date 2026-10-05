"""Ingesta de fuentes: PDF del Mapa Judicial, DIVIPOLA, geometría y datos de ejemplo.

Todas las descargas de red se cachean en ``config.CACHE`` para reproducibilidad
y arranque offline: si el archivo ya existe en caché, no se vuelve a descargar.
"""
from __future__ import annotations

import ssl
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from . import config

_UA = {"User-Agent": "Mozilla/5.0 (judicial_map ingest)"}


def _download(url: str, dest: Path) -> Path:
    """Descarga ``url`` a ``dest`` (crea el directorio padre si hace falta)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        dest.write_bytes(resp.read())
    return dest


def fetch_cached(url: str, filename: str, *, refresh: bool = False) -> Path:
    """Devuelve la ruta en caché de ``url``; descarga solo si falta o ``refresh``."""
    dest = config.CACHE / filename
    if refresh or not dest.exists():
        _download(url, dest)
    return dest


# --------------------------------------------------------------------------- #
# PDF del Mapa Judicial -> jerarquía Distrito / Circuito / Municipio
# --------------------------------------------------------------------------- #
_MARKERS = {"CIRCUITOS JUDICIALES", "TOTAL CIRCUITOS", "MUNICIPIOS", ""}


def load_judicial_hierarchy(pdf_path: Path | None = None, *, refresh: bool = False) -> pd.DataFrame:
    """Extrae la jerarquía Distrito -> Circuito -> Municipio del PDF.

    El distrito y el circuito se propagan hacia abajo (``ffill``) porque el PDF
    solo los imprime en su fila de cabecera. El ordinal de municipio del PDF se
    descarta: camelo lo deja vacío en ~1/3 de las filas y, además, es un ordinal
    por circuito sin relación con el código DANE.

    Returns:
        DataFrame con columnas ``district``, ``circuit``, ``municipality``.
    """
    import camelot

    if pdf_path is None:
        pdf_path = fetch_cached(config.PDF_URL, config.PDF_CACHE_NAME, refresh=refresh)

    tables = camelot.read_pdf(
        str(pdf_path), pages="all", flavor="stream", row_tol=0, edge_tol=900
    )
    frames = [t.df for t in tables if t.df.shape[1] == 6]
    if not frames:
        raise ValueError("camelot no extrajo tablas de 6 columnas del PDF")
    df = pd.concat(frames).reset_index(drop=True)
    df.columns = [
        "district_no", "district", "circuit_no", "circuit", "municipality_no", "municipality",
    ]

    # limpiar espacios y propagar distrito/circuito hacia abajo
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    for col in ("district", "circuit"):
        df[col] = df[col].replace("", pd.NA).ffill()

    # quedarse solo con filas de municipio reales (nombre no-marcador)
    df = df[~df["circuit"].isin(_MARKERS)]
    df = df[~df["municipality"].isin(_MARKERS)]
    df = df[~df["municipality"].str.contains("TOTAL", na=False)]

    return (
        df[["district", "circuit", "municipality"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


# --------------------------------------------------------------------------- #
# DIVIPOLA municipios (DANE) -> código DANE + departamento
# --------------------------------------------------------------------------- #
def load_divipola(path: Path | None = None, *, refresh: bool = False) -> pd.DataFrame:
    """Carga DIVIPOLA (hoja ``Municipios``) con el código DANE zero-padded a 5.

    Returns:
        DataFrame con ``cod_dane`` (5 díg.), ``cod_depto`` (2 díg.),
        ``departamento``, ``municipio``, ``tipo``.
    """
    if path is None:
        path = fetch_cached(config.DIVIPOLA_URL, config.DIVIPOLA_CACHE_NAME, refresh=refresh)

    df = pd.read_excel(
        path, sheet_name="Municipios", skiprows=10,
        names=["cod_depto", "departamento", "cod_dane", "municipio", "tipo", "lon", "lat", "nota"],
    )
    df = df[df["cod_dane"].notna()].copy()
    df["cod_dane"] = df["cod_dane"].astype(float).astype(int).astype(str).str.zfill(5)
    df["cod_depto"] = df["cod_dane"].str[:2]
    df["departamento"] = df["departamento"].astype(str).str.strip()
    df["municipio"] = df["municipio"].astype(str).str.strip()
    return df[["cod_dane", "cod_depto", "departamento", "municipio", "tipo"]].reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Datos de ejemplo: eficiencia de juzgados (nivel distrito)
# --------------------------------------------------------------------------- #
def load_efficiency(path: Path) -> pd.DataFrame:
    """Carga un archivo de eficiencia (DB1/DB2): columna ``District`` + años + ``AVG_Eff``."""
    return pd.read_excel(path)


# --------------------------------------------------------------------------- #
# Geometría municipal (DANE/MGN 2024) -> polígonos por código DANE
# --------------------------------------------------------------------------- #
def _fetch_mgn_department(dept_code: str):
    """Descarga los municipios de un departamento del FeatureServer como GeoDataFrame."""
    import geopandas as gpd

    params = {
        "where": f"DPTO_CCDGO='{dept_code}'",
        "outFields": config.MGN_OUTFIELDS,
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    url = f"{config.MGN_QUERY_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=120, context=ssl.create_default_context()) as resp:
        payload = resp.read()
    # pyogrio no acepta el stream de ArcGIS por URL (range requests) -> archivo temporal
    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    return gpd.read_file(tmp_path)


def load_municipal_geometries(dept_codes, *, refresh: bool = False):
    """Geometrías municipales del DANE/MGN con código DANE (``cod_dane``).

    Pagina por departamento (el server no soporta ``resultRecordCount``) y cachea
    el resultado concatenado en ``config.CACHE``.

    Returns:
        GeoDataFrame con ``cod_dane``, ``municipio_dane``, ``departamento_dane``,
        ``tipo`` y ``geometry`` (EPSG:4326).
    """
    import geopandas as gpd

    cache = config.CACHE / config.MGN_CACHE_NAME
    if cache.exists() and not refresh:
        return gpd.read_file(cache)

    frames = [_fetch_mgn_department(str(dd)) for dd in dept_codes]
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    gdf = gdf.rename(columns={
        "MPIO_CDPMP": "cod_dane", "MPIO_CNMBRE": "municipio_dane",
        "DPTO_CNMBRE": "departamento_dane", "MPIO_TIPO": "tipo",
    })
    gdf["cod_dane"] = gdf["cod_dane"].astype(str).str.zfill(5)
    cache.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(cache, driver="GeoJSON")
    return gdf
