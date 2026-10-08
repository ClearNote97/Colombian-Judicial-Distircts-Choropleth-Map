# AGENTS.md — contrato de trabajo + contexto del proyecto

## Cómo trabajamos
La dinámica genérica (Dev Container desechable, `uv`, `docker exec`, convención
`sandbox/ → tests/ → output/`, estados 0/N) vive en **[`README_AGENTS.md`](README_AGENTS.md)**.
Es la fuente de verdad del *cómo*; esto de abajo es el *qué* de ESTE proyecto.

## Qué es
Pipeline que construye los archivos de mapa de los **distritos judiciales de Colombia** a nivel
municipio/circuito/distrito (geojson + xlsx) para Power BI/Dash. Tesis: la geografía judicial
**no coincide** con la división político-administrativa. Ver [`README.md`](README.md).

## Stack y ejecución
- Python **3.14** en Dev Container (`uv`). Paquete en **`src/judicial_map/`** (src-layout; el
  devcontainer fija `PYTHONPATH=src`).
- Un comando: **`python -m judicial_map`** (orquesta `ingest → homologate → merge → export → viz`).
- Tests: **`uv run pytest tests/`** (el gate).
- Correr/verificar siempre dentro del contenedor vía `docker exec` (ver README_AGENTS §4).

## Dónde está la verdad
- **Decisiones de diseño:** [`docs/bitacora-decisiones.md`](docs/bitacora-decisiones.md) (D-001…D-006).
  **Fuente única**; la memoria del agente apunta aquí, no guarda copia divergente.
- **Hallazgos de investigación:** [`docs/hallazgos-geograficos.md`](docs/hallazgos-geograficos.md).
- **Diccionario de datos:** [`docs/diccionario-de-datos.md`](docs/diccionario-de-datos.md).
- **Homologación municipio → código DANE:** [`data/homologacion/`](data/homologacion/).
- **Legado (notebook original, intacto):** [`docs/legado/`](docs/legado/).

## Reglas del proyecto
- El **producto** son los archivos de mapa en `output/`; los `.xlsx` de eficiencia (DB1/DB2) son
  **datos de ejemplo** para verificar, no el producto.
- El **departamento no es un nivel de salida** (D-006): los niveles son judiciales.
- No tocar `docs/legado/` (memoria del punto de partida).
- El código DANE es la llave de unión; la homologación por nombre vive en `data/homologacion/`,
  no hardcodeada.
