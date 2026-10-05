"""Configuración central del pipeline: rutas, fuentes de datos y constantes."""
from __future__ import annotations

from pathlib import Path

# --- Rutas del proyecto (raíz = dos niveles arriba de src/judicial_map/) ---
ROOT: Path = Path(__file__).resolve().parents[2]
DATA: Path = ROOT / "data"
DATA_OTHER: Path = DATA / "other"
CACHE: Path = DATA_OTHER / "cache"
HOMOLOG: Path = DATA / "homologacion"
OUTPUT: Path = ROOT / "output"

# --- Datos de ejemplo (eficiencia de juzgados, nivel distrito) ---
DB_MUNICIPAL: Path = DATA_OTHER / "DB1 - Municipal Courts Efficiency.xlsx"
DB_CIRCUIT: Path = DATA_OTHER / "DB2 - Circuits Courts Efficiency.xlsx"

# --- Tablas de homologación (versionadas, YAML) ---
DISTRITO_DEPARTAMENTO_YAML: Path = HOMOLOG / "distrito_departamento.yaml"
OVERRIDE_MUNICIPIOS_YAML: Path = HOMOLOG / "override_municipios.yaml"

# --- Fuentes de red (se cachean en CACHE en la primera corrida) ---
# PDF oficial del Mapa Judicial (Rama Judicial).
PDF_URL: str = (
    "https://www.ramajudicial.gov.co/documents/10228/64622/"
    "MAPA+JUDICIAL%282%29.pdf/cab3506e-a815-4fac-bb08-288b7ad54d69"
)
# DIVIPOLA municipios (DANE geoportal).
DIVIPOLA_URL: str = (
    "https://geoportal.dane.gov.co/descargas/divipola/DIVIPOLA_Municipios.xlsx"
)
# Geometría municipal oficial (DANE/MGN 2024), vía FeatureServer ArcGIS del geoportal.
# El server no soporta resultRecordCount/offset, así que se pagina por departamento
# (DPTO_CCDGO). El código DANE completo del municipio viene en MPIO_CDPMP.
MGN_QUERY_URL: str = (
    "https://geoportal.dane.gov.co/mparcgis/rest/services/"
    "MMRA2024/Serv_CapasMMRA_2024/FeatureServer/317/query"
)
MGN_OUTFIELDS: str = "MPIO_CDPMP,MPIO_CNMBRE,DPTO_CNMBRE,MPIO_TIPO"
MGN_CACHE_NAME: str = "mgn_municipios.geojson"

# Nombres de archivo en caché
PDF_CACHE_NAME: str = "mapa_judicial.pdf"
DIVIPOLA_CACHE_NAME: str = "DIVIPOLA_Municipios.xlsx"

# --- Niveles de agregación del producto (JUDICIALES; el depto no es nivel de salida) ---
# El corazón del proyecto: la geografía judicial NO coincide con la división
# político-administrativa. DIVIPOLA/geometría son instrumentales (código DANE ->
# geometría) para luego agregar por unidad JUDICIAL.
LEVELS: tuple[str, ...] = ("municipio", "circuito", "distrito")

# --- Export ---
# Tolerancia de simplificación de geometría (grados). ~0.001 ≈ 100 m: aligera
# mucho los archivos de salida con pérdida visual mínima. None = sin simplificar.
SIMPLIFY_TOLERANCE: float | None = 0.001
OUTPUT_PREFIX: str = "mapa_judicial"

# --- Parámetros del mapa (viz, secundario) ---
MAP_CENTER: dict[str, float] = {"lat": 4.1156735, "lon": -72.9301367}
MAP_ZOOM: float = 4.5
EFF_ZMIN: float = 0.65
EFF_ZMAX: float = 1.0
