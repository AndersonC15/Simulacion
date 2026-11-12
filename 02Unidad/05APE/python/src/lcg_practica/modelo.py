"""Dominio matemático: no depende de archivos, consola ni gráficas."""

from dataclasses import dataclass
from math import gcd
from typing import Protocol


@dataclass(frozen=True)
class ParametrosLCG:
    a: int = 1_664_525
    c: int = 1_013_904_223
    m: int = 2**32
    semilla: int = 12_345

    def __post_init__(self) -> None:
        valores = (self.a, self.c, self.m, self.semilla)
        if any(type(valor) is not int for valor in valores):
            raise ValueError("Los parámetros deben ser enteros.")
        if not 1 <= self.m <= 2**32:
            raise ValueError("El módulo debe estar entre 1 y 2^32 en esta práctica.")
        if not all(0 <= valor < self.m for valor in (self.a, self.c, self.semilla)):
            raise ValueError("Se requiere 0 <= a, c y semilla < m.")


class GeneradorPseudoaleatorio(Protocol):
    """Contrato de la estrategia de generación usada por el controlador."""

    def siguiente(self) -> int: ...


class GeneradorLCG:
    def __init__(self, parametros: ParametrosLCG) -> None:
        self._parametros = parametros
        self._estado = parametros.semilla

    def siguiente(self) -> int:
        p = self._parametros
        self._estado = (p.a * self._estado + p.c) % p.m
        return self._estado


@dataclass(frozen=True)
class AnalisisPeriodo:
    coprimos: bool
    factores_dividen: bool
    regla_cuatro: bool
    periodo_teorico: int | None
    preperiodo_observado: int | None
    periodo_observado: int | None


class AnalizadorPeriodo:
    @staticmethod
    def _factores_primos(numero: int) -> tuple[int, ...]:
        factores = []
        divisor = 2
        while divisor * divisor <= numero:
            if numero % divisor == 0:
                factores.append(divisor)
                while numero % divisor == 0:
                    numero //= divisor
            divisor += 1
        if numero > 1:
            factores.append(numero)
        return tuple(factores)

    def analizar(self, p: ParametrosLCG, estados: tuple[int, ...]) -> AnalisisPeriodo:
        coprimos = gcd(p.c, p.m) == 1
        factores = all((p.a - 1) % primo == 0 for primo in self._factores_primos(p.m))
        regla_cuatro = p.m % 4 != 0 or (p.a - 1) % 4 == 0
        teorico = p.m if coprimos and factores and regla_cuatro else None
        # X0 participa en la detección, pero no se incluye como salida generada.
        vistos = {p.semilla: 0}
        for indice, estado in enumerate(estados, start=1):
            if estado in vistos:
                inicio = vistos[estado]
                return AnalisisPeriodo(
                    coprimos, factores, regla_cuatro, teorico, inicio, indice - inicio
                )
            vistos[estado] = indice
        return AnalisisPeriodo(coprimos, factores, regla_cuatro, teorico, None, None)


@dataclass(frozen=True)
class ResultadoExperimento:
    parametros: ParametrosLCG
    estados: tuple[int, ...]
    periodo: AnalisisPeriodo

    @property
    def normalizados(self) -> tuple[float, ...]:
        return tuple(estado / self.parametros.m for estado in self.estados)

