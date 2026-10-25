"""Strategy: cada algoritmo recibe parámetros y devuelve una serie inmutable."""
from decimal import Decimal, DecimalException, localcontext
from typing import Protocol

from Modelo.numeros import ErrorValidacion, comprobar_resultado, multiplicar
from Modelo.resultados import Serie
from Modelo.tiempo import malla


class EstrategiaSimulacion(Protocol):
    def simular(self, parametros) -> Serie:
        ...


class Deterministico:
    def simular(self, parametros):
        tiempos = malla(parametros)
        poblaciones = []
        for tiempo in tiempos:
            exponente = multiplicar(parametros.tasa, tiempo)
            if abs(exponente) > 500:
                raise ErrorValidacion("El exponente r*t supera ±500; reduzca tasa u horizonte.")
            try:
                with localcontext() as contexto:
                    contexto.prec = parametros.precision
                    factor = exponente.exp()
            except DecimalException as error:
                raise ErrorValidacion("No se pudo aproximar la exponencial.") from error
            poblaciones.append(comprobar_resultado(multiplicar(parametros.p0, factor)))
        return Serie("Determinístico exponencial", tiempos, tuple(poblaciones))
