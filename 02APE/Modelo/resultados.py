from dataclasses import dataclass
from decimal import Decimal

from Modelo.numeros import ErrorValidacion, MAX_PUNTOS, comprobar_resultado
from Modelo.parametros import Parametros


@dataclass(frozen=True)
class Serie:
    nombre: str
    tiempos: tuple[Decimal, ...]
    poblaciones: tuple[Decimal, ...]

    def __post_init__(self):
        if not isinstance(self.tiempos, tuple) or not isinstance(self.poblaciones, tuple):
            raise ErrorValidacion("Los resultados deben ser tuplas inmutables.")
        if not 1 <= len(self.tiempos) == len(self.poblaciones) <= MAX_PUNTOS:
            raise ErrorValidacion("Tiempos y poblaciones deben tener igual longitud, entre 1 y 10001.")
        for valor in self.tiempos + self.poblaciones:
            if not isinstance(valor, Decimal):
                raise ErrorValidacion("Los resultados deben contener Decimal.")
            comprobar_resultado(valor)
            if valor < 0:
                raise ErrorValidacion("Tiempos y poblaciones deben ser no negativos.")
        if self.tiempos[0] != 0 or any(b <= a for a, b in zip(self.tiempos, self.tiempos[1:])):
            raise ErrorValidacion("El tiempo debe empezar en cero y crecer estrictamente.")


@dataclass(frozen=True)
class Experimento:
    parametros: Parametros
    series: tuple[Serie, ...]
    observaciones: tuple[Decimal, ...]
    escenario: str = "personalizado"
