"""Punto de composicion de dependencias y entrada de consola."""

import argparse
from pathlib import Path
import sys

from ape06.controlador.simulacion import ControladorSimulacion
from ape06.infraestructura.archivos import RepositorioResultados, leer_parametros
from ape06.modelo.experimentos import EstimadorPi, MedidorRendimiento, ServicioSimulacion
from ape06.modelo.pruebas import ChiCuadrado, KolmogorovSmirnov, Rachas
from ape06.vista.consola import VistaConsola
from ape06.vista.graficas import VistaGraficas


def main() -> int:
    parser = argparse.ArgumentParser(description="APE 06: LCG, Chi-cuadrado, KS y rachas")
    parser.add_argument("comando", choices=("ejecutar", "benchmark"))
    parser.add_argument("--config", type=Path, default=Path("config/generadores.csv"))
    parser.add_argument("--generadores", default="minstd,glibc,zx81", help="Nombres separados por comas")
    parser.add_argument("--salida", type=Path, default=Path("resultados/python"))
    parser.add_argument("--n", type=int, default=10000, help="Cantidad de valores para validacion")
    parser.add_argument("--alfa", type=float, default=0.05)
    parser.add_argument("--tamanos", default="1000,10000,100000,1000000", help="Puntos para pi")
    parser.add_argument("--repeticiones", type=int, default=5)
    args = parser.parse_args()
    try:
        parametros = leer_parametros(args.config, tuple(args.generadores.split(",")))
        if args.n < 50 or not 0 < args.alfa < 1:
            raise ValueError("Se requiere N >= 50 y 0 < alfa < 1.")
        tamanos = tuple(int(n) for n in args.tamanos.split(","))
        if not tamanos or any(n < 1 for n in tamanos) or len(set(tamanos)) != len(tamanos) or args.repeticiones < 1:
            raise ValueError("Los tamanos deben ser positivos, sin duplicados, y las repeticiones >= 1.")
        controlador = ControladorSimulacion(
            ServicioSimulacion((ChiCuadrado(), KolmogorovSmirnov(), Rachas())),
            MedidorRendimiento(EstimadorPi()), VistaConsola(), VistaGraficas(),
            RepositorioResultados(args.salida),
        )
        if args.comando == "ejecutar":
            controlador.ejecutar(parametros, args.n, args.alfa)
        else:
            controlador.benchmark(parametros, tamanos, args.repeticiones)
    except (ValueError, OSError, KeyError, OverflowError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
