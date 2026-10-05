"""Entry point: ``python -m judicial_map`` corre el pipeline completo."""
from __future__ import annotations

import argparse
import logging

from . import config, pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="judicial_map",
        description="Genera los archivos de mapa judicial de Colombia (municipio/circuito/distrito).",
    )
    parser.add_argument("--refresh", action="store_true",
                        help="Re-descargar las fuentes de red (ignora la caché).")
    parser.add_argument("--tolerance", type=float, default=config.SIMPLIFY_TOLERANCE,
                        help="Tolerancia de simplificación de geometría en grados (0 = sin simplificar).")
    parser.add_argument("--no-viz", action="store_true",
                        help="No generar los choropleths de ejemplo (solo los archivos de mapa).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    summary = pipeline.run(
        refresh=args.refresh, tolerance=args.tolerance or None, make_viz=not args.no_viz
    )

    print("\n== Resumen ==")
    print("Niveles:", summary["niveles"])
    print("Homologación:", summary["match"])
    print("Municipios sin geometría:", summary["municipios_sin_geometria"])
    print("Archivos generados:")
    for p in summary["archivos"]:
        print("  -", p)


if __name__ == "__main__":
    main()
