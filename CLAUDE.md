# CLAUDE.md

Puntero fino para Claude Code. **La guía del proyecto vive en [`AGENTS.md`](AGENTS.md)** (contexto
+ cómo correr) y en **[`README_AGENTS.md`](README_AGENTS.md)** (la dinámica de trabajo genérica).
Léelos primero.

Esencial:
- Proyecto: pipeline del **Mapa Judicial de Colombia** (geojson/xlsx multinivel). Ver [`README.md`](README.md).
- Correr: `python -m judicial_map` dentro del Dev Container; ejecutar vía `docker exec`.
- Tests: `uv run pytest tests/`.
- Decisiones (fuente única): [`docs/bitacora-decisiones.md`](docs/bitacora-decisiones.md).
- El producto vive en `output/`; los `.xlsx` DB1/DB2 son datos de ejemplo. No tocar `docs/legado/`.
