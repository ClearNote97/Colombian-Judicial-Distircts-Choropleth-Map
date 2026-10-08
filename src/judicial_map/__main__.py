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
    parser.add_argument("--niveles", nargs="+", choices=list(config.LEVELS),
                        default=list(config.LEVELS), metavar="NIVEL",
                        help="Niveles de mapa a generar: municipio, circuito, distrito "
                             "(por defecto: los tres).")
    parser.add_argument("--refresh", action="store_true",
                        help="Re-descargar las fuentes de red (PDF, DIVIPOLA, geometría); "
                             "ignora la caché. Úsalo solo si las fuentes se actualizaron.")
    parser.add_argument("--tolerance", type=float, default=config.SIMPLIFY_TOLERANCE,
                        help="Simplificación de geometría en grados (0 = máximo detalle; "
                             f"por defecto {config.SIMPLIFY_TOLERANCE}, archivos más livianos).")
    parser.add_argument("--no-viz", action="store_true",
                        help="No generar los mapas de ejemplo PNG/PDF (solo los archivos de mapa).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    summary = pipeline.run(
        refresh=args.refresh, tolerance=args.tolerance or None,
        make_viz=not args.no_viz, niveles=tuple(args.niveles),
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
