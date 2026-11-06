"""Casos de uso del modelo: validacion y tabla de rendimiento con pi."""

import math
from time import perf_counter

import numpy as np

from .datos import Analisis, Medicion, ParametrosLCG, ResultadoPi
from .lcg import GeneradorLCG
from .pruebas import PruebaEstadistica


class ServicioSimulacion:
    def __init__(self, pruebas: tuple[PruebaEstadistica, ...]) -> None:
        self._pruebas = pruebas

    def analizar(self, parametros: ParametrosLCG, cantidad: int, alfa: float) -> Analisis:
        if cantidad < 50:
            raise ValueError("La practica necesita N >= 50 para los diez intervalos de Chi-cuadrado.")
        muestra = GeneradorLCG(parametros).generar(cantidad)
        pruebas = tuple(prueba.evaluar(muestra.valores, alfa) for prueba in self._pruebas)
        vistos = {parametros.semilla: 0}
        periodo = None
        for i, estado in enumerate(muestra.estados, 1):
            entero = int(estado)
            if entero in vistos:
                periodo = i - vistos[entero]
                break
            vistos[entero] = i
        return Analisis(
            muestra, pruebas, float(np.min(muestra.valores)), float(np.max(muestra.valores)),
            float(np.mean(muestra.valores)), float(np.var(muestra.valores)),
            len(np.unique(muestra.estados)), periodo,
        )


class EstimadorPi:
    """N puntos, 2N valores consecutivos de un LCG reiniciado con la semilla indicada."""

    def estimar(self, parametros: ParametrosLCG, puntos: int) -> ResultadoPi:
        if type(puntos) is not int or puntos < 1:
            raise ValueError("La cantidad de puntos debe ser un entero positivo.")
        generador = GeneradorLCG(parametros)
        dentro = 0
        for _ in range(puntos):
            x, y = generador.siguiente(), generador.siguiente()
            if x * x + y * y <= 1.0:
                dentro += 1
        estimacion = 4.0 * dentro / puntos
        return ResultadoPi(puntos, dentro, estimacion, abs(estimacion - math.pi))


class MedidorRendimiento:
    def __init__(self, estimador: EstimadorPi) -> None:
        self._estimador = estimador

    def medir(self, parametros: ParametrosLCG, puntos: int, repeticiones: int) -> Medicion:
        if repeticiones < 1:
            raise ValueError("Se requiere al menos una repeticion.")
        # Mismo calentamiento en ambos lenguajes; no se cuenta en los tiempos.
        for _ in range(3):
            self._estimador.estimar(parametros, min(puntos, 10000))
        tiempos = []
        resultado = None
        for _ in range(repeticiones):
            inicio = perf_counter()
            resultado = self._estimador.estimar(parametros, puntos)
            tiempos.append(perf_counter() - inicio)
        assert resultado is not None
        return Medicion(parametros, resultado, tuple(tiempos))
