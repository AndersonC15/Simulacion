"""Modelo matemático sin dependencias de consola, archivos o bibliotecas gráficas."""

from dataclasses import dataclass
import math
from statistics import median
from time import perf_counter
from typing import Protocol


TAMANOS_GUIA = (1_000, 10_000, 100_000, 1_000_000)
LIMITE_PUNTOS = 1_000_000


@dataclass(frozen=True)
class Parametros:
    semilla: int = 123_457

    def __post_init__(self) -> None:
        if type(self.semilla) is not int or not 1 <= self.semilla < self.modulo:
            raise ValueError("La semilla debe ser un entero entre 1 y 2147483646.")

    @property
    def multiplicador(self) -> int:
        return 16_807

    @property
    def incremento(self) -> int:
        return 0

    @property
    def modulo(self) -> int:
        return 2_147_483_647


class FuenteUniforme(Protocol):
    def siguiente(self) -> float: ...


class GeneradorLCG:
    def __init__(self, parametros: Parametros) -> None:
        self.parametros = parametros
        self.estado = parametros.semilla

    def siguiente_entero(self) -> int:
        self.estado = self.parametros.multiplicador * self.estado % self.parametros.modulo
        return self.estado

    def siguiente(self) -> float:
        return self.siguiente_entero() / self.parametros.modulo


@dataclass(frozen=True)
class Resultado:
    puntos: int
    dentro: int

    @property
    def estimacion(self) -> float:
        return 4.0 * self.dentro / self.puntos

    @property
    def error_absoluto(self) -> float:
        return abs(self.estimacion - math.pi)


class EstimadorPi:
    def estimar(self, puntos: int, fuente: FuenteUniforme) -> Resultado:
        if type(puntos) is not int or not 1 <= puntos <= LIMITE_PUNTOS:
            raise ValueError("La cantidad de puntos debe estar entre 1 y 1000000.")
        dentro = 0
        for _ in range(puntos):
            uniforme_x, uniforme_y = fuente.siguiente(), fuente.siguiente()
            if not (0 <= uniforme_x < 1 and 0 <= uniforme_y < 1):
                raise ValueError("La fuente debe producir valores finitos en [0,1).")
            coordenada_x, coordenada_y = 2.0 * uniforme_x - 1.0, 2.0 * uniforme_y - 1.0
            if coordenada_x * coordenada_x + coordenada_y * coordenada_y <= 1.0:
                dentro += 1
        return Resultado(puntos, dentro)


@dataclass(frozen=True)
class Medicion:
    resultado: Resultado
    segundos: tuple[float, ...]

    @property
    def mediana(self) -> float:
        return median(self.segundos)


class MedidorRendimiento:
    def __init__(self, estimador: EstimadorPi) -> None:
        self.estimador = estimador

    def medir(self, parametros: Parametros, puntos: int, repeticiones: int) -> Medicion:
        if type(repeticiones) is not int or not 1 <= repeticiones <= 30:
            raise ValueError("Las repeticiones deben estar entre 1 y 30.")
        for _ in range(3):
            self.estimador.estimar(min(puntos, 10_000), GeneradorLCG(parametros))
        tiempos = []
        resultados = []
        for _ in range(repeticiones):
            inicio = perf_counter()
            resultado = self.estimador.estimar(puntos, GeneradorLCG(parametros))
            tiempos.append(perf_counter() - inicio)
            resultados.append(resultado)
        if any(resultado != resultados[0] for resultado in resultados):
            raise ValueError("El experimento no fue reproducible entre repeticiones.")
        return Medicion(resultados[0], tuple(tiempos))


def validar_tamanos(tamanos: tuple[int, ...]) -> None:
    if not tamanos or any(type(valor) is not int or not 1 <= valor <= LIMITE_PUNTOS for valor in tamanos):
        raise ValueError("Los tamaños deben ser enteros entre 1 y 1000000.")
    if tuple(sorted(set(tamanos))) != tamanos:
        raise ValueError("Los tamaños deben estar ordenados y no repetirse.")
