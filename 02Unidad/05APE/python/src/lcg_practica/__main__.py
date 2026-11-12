"""Punto de entrada y composición de dependencias de la aplicación."""

import argparse
from pathlib import Path

from lcg_practica.controlador import ControladorExperimento
from lcg_practica.modelo import AnalizadorPeriodo, GeneradorLCG, ParametrosLCG
from lcg_practica.vista import VistaArchivosConsola


def main() -> None:
    parser = argparse.ArgumentParser(description="APE 05: LCG de la guía de Simulación.")
    parser.add_argument("--semilla", type=int, default=12_345)
    parser.add_argument("--cantidad", type=int, default=10_000)
    parser.add_argument("--salida", type=Path, default=Path("resultados/python"))
    args = parser.parse_args()
    try:
        parametros = ParametrosLCG(semilla=args.semilla)
        ControladorExperimento(AnalizadorPeriodo(), VistaArchivosConsola()).ejecutar(
            parametros, GeneradorLCG(parametros), args.cantidad, args.salida
        )
    except (ValueError, OSError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()

