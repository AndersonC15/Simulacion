"""Coordina la comparacion y el informe consolidado; no sustituye el programa Java."""

import argparse
from pathlib import Path
import sys

from ape06.infraestructura.comparacion import comparar_todo
from ape06.vista.informe import VistaInforme


def main() -> int:
    parser = argparse.ArgumentParser(description="Comparar las ejecuciones Java/Python y generar el informe")
    parser.add_argument("--python", type=Path, default=Path("resultados/python"))
    parser.add_argument("--java", type=Path, default=Path("resultados/java"))
    parser.add_argument("--salida", type=Path, default=Path("resultados/comparacion"))
    args = parser.parse_args()
    try:
        args.salida.mkdir(parents=True, exist_ok=True)
        (args.salida / "verificacion.json").unlink(missing_ok=True)
        analisis, benchmark = comparar_todo(args.python, args.java, args.salida)
        VistaInforme().guardar(analisis, benchmark, args.python, args.java, args.salida)
        print(f"Comparacion correcta: {sum(a['n'] for a in analisis)} valores y {len(benchmark)} estimaciones de pi.")
        print(f"Informe: {(args.salida / 'informe.pdf').resolve()}")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Error de comparacion: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
