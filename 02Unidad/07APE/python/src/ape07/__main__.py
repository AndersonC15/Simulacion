"""Composición de las dependencias y validación de la entrada CLI."""

import argparse
from pathlib import Path
import sys

from ape07.controlador import ControladorExperimento
from ape07.modelo import EstimadorPi, MedidorRendimiento, Parametros
from ape07.vista import VistaResultados


def main() -> int:
    parser = argparse.ArgumentParser(description="APE 07: estimación de pi mediante Monte Carlo")
    parser.add_argument("--semilla", type=int, default=123457)
    parser.add_argument("--tamanos", default="1000,10000,100000,1000000")
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--salida", type=Path, default=Path("resultados/python"))
    argumentos = parser.parse_args()
    try:
        parametros = Parametros(argumentos.semilla)
        tamanos = tuple(int(valor) for valor in argumentos.tamanos.split(","))
        controlador = ControladorExperimento(MedidorRendimiento(EstimadorPi()), VistaResultados())
        controlador.ejecutar(parametros, tamanos, argumentos.repeticiones, argumentos.salida)
    except (ValueError, OSError, OverflowError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
