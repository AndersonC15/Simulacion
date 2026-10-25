"""Strategy: cada algoritmo recibe parámetros y devuelve una serie inmutable."""
from decimal import Decimal, DecimalException, localcontext
from typing import Protocol

from Modelo.numeros import ErrorValidacion, comprobar_resultado, decimal_desde_entrada, multiplicar, sumar
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


class Discreto:
    def simular(self, parametros):
        tiempos = malla(parametros, periodica=True)
        if len(tiempos) > 1 and parametros.tasa < -1:
            raise ErrorValidacion("Discreto requiere r >= -1 para no producir población negativa.")
        poblaciones = [parametros.p0]
        for _ in tiempos[1:]:
            actual = poblaciones[-1]
            poblaciones.append(sumar(actual, multiplicar(parametros.tasa, actual)))
        return Serie("Discreto", tiempos, tuple(poblaciones))


class Estocastico:
    def __init__(self, ruido=None):
        self._ruido = ruido

    def simular(self, parametros):
        import numpy as np

        tiempos = malla(parametros, periodica=True)
        generador = np.random.default_rng(parametros.semilla)
        poblaciones = [parametros.p0]
        for _ in tiempos[1:]:
            if self._ruido is not None:
                ruido = decimal_desde_entrada(self._ruido())
            elif parametros.sigma == 0:
                ruido = Decimal(0)
            else:
                # Frontera float64 explícita: no recupera dígitos del generador.
                normal_estandar = Decimal(str(generador.normal(0, 1)))
                ruido = multiplicar(parametros.sigma, normal_estandar)
            actual = poblaciones[-1]
            siguiente = sumar(sumar(actual, multiplicar(parametros.tasa, actual)), ruido)
            poblaciones.append(max(Decimal(0), siguiente))
        return Serie("Estocástico", tiempos, tuple(poblaciones))


class ContinuoEuler:
    def simular(self, parametros):
        tiempos = malla(parametros)
        poblaciones = [parametros.p0]
        for anterior, actual in zip(tiempos, tiempos[1:]):
            paso = sumar(actual, anterior.copy_negate())
            factor = sumar(Decimal(1), multiplicar(paso, parametros.tasa))
            if factor < 0:
                raise ErrorValidacion("Euler requiere 1 + h*r >= 0 en cada paso; reduzca dt para decrecimiento.")
            incremento = multiplicar(paso, multiplicar(parametros.tasa, poblaciones[-1]))
            poblaciones.append(sumar(poblaciones[-1], incremento))
        return Serie("Continuo (Euler, aproximación)", tiempos, tuple(poblaciones))
