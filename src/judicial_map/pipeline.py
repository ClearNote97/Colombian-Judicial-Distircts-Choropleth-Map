"""Orquestación del pipeline: ingest -> homologate -> merge -> export."""
from __future__ import annotations

import logging

from . import config, export, homologate, ingest, merge, viz

log = logging.getLogger("judicial_map")


def run(
    *,
    refresh: bool = False,
    tolerance: float | None = config.SIMPLIFY_TOLERANCE,
    make_viz: bool = True,
) -> dict:
    """Ejecuta el pipeline completo y genera los archivos de mapa en ``output/``.

    Args:
        refresh: re-descargar las fuentes de red ignorando la caché.
        tolerance: tolerancia de simplificación de geometría (grados).

    Returns:
        Resumen con conteos por nivel, municipios sin geometría y rutas escritas.
    """
    log.info("1/4 Ingesta: PDF, DIVIPOLA, geometría MGN")
    hierarchy = ingest.load_judicial_hierarchy(refresh=refresh)
    divipola = ingest.load_divipola(refresh=refresh)
    geometries = ingest.load_municipal_geometries(
        sorted(divipola["cod_depto"].unique()), refresh=refresh
    )

    log.info("2/4 Homologación: municipio -> código DANE")
    overrides = homologate.load_overrides(config.OVERRIDE_MUNICIPIOS_YAML)
    resolution = homologate.resolve(hierarchy, divipola, overrides=overrides)
    if resolution.unresolved:
        log.warning("%d municipios sin código DANE", len(resolution.unresolved))

    log.info("3/4 Merge: geometría + dissolve por nivel judicial")
    municipios = merge.attach_geometry(resolution.resolved, geometries)
    missing = merge.missing_geometry(municipios)
    if len(missing):
        log.warning("%d municipios sin geometría: %s", len(missing),
                    ", ".join(missing["municipality"].tolist()))
    levels = merge.aggregate_levels(municipios)

    log.info("4/4 Export: archivos de mapa a %s", config.OUTPUT)
    written = export.write_all(levels, tolerance=tolerance)

    viz_files: list = []
    if make_viz:
        log.info("Viz: choropleths de ejemplo (eficiencia)")
        distrito = export.simplify(levels["distrito"], tolerance)
        viz_files = viz.generate_example_maps(distrito, geometries)

    return {
        "niveles": {name: len(g) for name, g in levels.items()},
        "municipios_sin_geometria": len(missing),
        "match": resolution.resolved["match"].value_counts().to_dict(),
        "archivos": [str(p) for p in written] + [str(p) for p in viz_files],
    }
