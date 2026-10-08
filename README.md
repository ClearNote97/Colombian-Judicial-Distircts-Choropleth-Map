# 🗺️ Mapa Judicial de Colombia — Choropleth multinivel

Pipeline reproducible que construye los **archivos de mapa de los distritos judiciales de
Colombia** a distintos niveles (municipio → circuito → distrito), listos para importar en
**Power BI, Dash** u otras herramientas. Nace como herramienta para la investigación en
**análisis económico del derecho (Law & Economics)**.

> **La tesis del proyecto:** la **geografía judicial no coincide** con la división
> político-administrativa de Colombia. Los distritos y circuitos judiciales **cruzan fronteras
> departamentales**. Visualizar esa geografía propia es el aporte de este mapa.
> Ver [`docs/hallazgos-geograficos.md`](docs/hallazgos-geograficos.md).

> La primera versión (un notebook monolítico, primer proyecto de programación del autor) se
> conserva intacta en [`docs/legado/`](docs/legado/).

---

## 🚀 Cómo correr

Requiere **Docker** + **VS Code** con la extensión **Dev Containers** (ver
[`README_AGENTS.md`](README_AGENTS.md)).

1. Abre el proyecto en VS Code → **Reopen in Container** (espera al `postCreateCommand`).
2. Un solo comando genera todo:

```bash
python -m judicial_map
```

Opciones: `--refresh` (re-descarga las fuentes), `--tolerance 0` (sin simplificar geometría),
`--no-viz` (omite los choropleths de ejemplo).

---

## 📦 Qué produce (en `output/`)

El **producto principal** son los archivos de mapa, en dos formatos por nivel:

| Nivel | GeoJSON (geometría) | XLSX (atributos) |
|---|---|---|
| Municipio judicial | `mapa_judicial_municipio.geojson` | `mapa_judicial_municipio.xlsx` |
| Circuito judicial | `mapa_judicial_circuito.geojson` | `mapa_judicial_circuito.xlsx` |
| Distrito judicial | `mapa_judicial_distrito.geojson` | `mapa_judicial_distrito.xlsx` |

Además, **mapas de verificación** (PNG + PDF, hechos con matplotlib) sobre la figura completa del
país: la división por distritos (`mapa_distritos_judiciales`) y dos choropleths de eficiencia de
los juzgados (`choropleth_eficiencia_municipal`, `choropleth_eficiencia_circuito`), con inset del
Archipiélago de San Andrés. *(Se usa matplotlib y no Plotly porque plotly.js no renderiza las
geometrías de las áreas no municipalizadas de la Amazonía; ver `docs/bitacora-decisiones.md` D-007.)*

---

## 🔗 Fuentes de datos

| Fuente | Qué aporta |
|---|---|
| **PDF Mapa Judicial** (Rama Judicial) | Jerarquía distrito → circuito → municipio (vía `camelot`) |
| **DIVIPOLA** (DANE) | Código DANE de 5 dígitos por municipio |
| **MGN 2024** (DANE, FeatureServer) | Geometría municipal por código DANE |
| `data/other/DB1/DB2 *.xlsx` | **Datos de ejemplo**: eficiencia de juzgados (para verificar) |

El PDF y DIVIPOLA se cachean y versionan (sus URLs pueden caer); la geometría MGN (~250 MB) se
cachea pero **no** se versiona (se regenera). La homologación de nombres municipio → código DANE
vive en [`data/homologacion/`](data/homologacion/) (ver `docs/bitacora-decisiones.md`, D-004).

---

## 🧱 Estructura

```
src/judicial_map/   ingest → homologate → merge → export (+ viz) · pipeline · __main__
data/other/         datos de ejemplo + caché de fuentes
data/homologacion/  tablas de homologación (override YAML)
output/             el producto (geojson/xlsx multinivel + choropleths)
tests/              pytest (el gate)
docs/               bitácora de decisiones, diccionario de datos, hallazgos, legado/
```

---

## ⚖️ Licencia · ✍️ Autor

[MIT](LICENSE). **MSc. Nicolás Enrique Valencia Santiago.** Proyecto de acceso abierto; se agradece
la referencia a esta obra en trabajos derivados.
