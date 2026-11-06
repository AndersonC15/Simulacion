"""Objetos de datos del modelo, sin dependencias de la vista."""

from dataclasses import dataclass, field
import re

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class ParametrosLCG:
    nombre: str
    semilla: int
    a: int
    c: int
    m: int
    fuente: str = "Configuracion del usuario"

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", self.nombre):
            raise ValueError("El nombre debe usar letras minusculas, numeros y guion bajo.")
        if any(type(x) is not int for x in (self.semilla, self.a, self.c, self.m)):
            raise ValueError("Los parametros del LCG deben ser enteros.")
        if not 1 <= self.m <= 2**53:
            raise ValueError("Se requiere 1 <= m <= 2^53 para normalizar con double sin obtener 1.")
        if any(not 0 <= x < self.m for x in (self.semilla, self.a, self.c)):
            raise ValueError("Se requiere 0 <= semilla, a, c < m.")


@dataclass(frozen=True)
class Muestra:
    parametros: ParametrosLCG
    estados: NDArray[np.int64]
    valores: NDArray[np.float64]


@dataclass(frozen=True)
class Intervalo:
    inferior: float
    superior: float
    observada: int
    esperada: float
    aporte: float


@dataclass(frozen=True)
class ResultadoPrueba:
    nombre: str
    hipotesis: str
    estadistico: float | None
    valor_p: float | None
    critico: float | None
    alfa: float
    metodo: str
    detalles: dict[str, float] = field(default_factory=dict)
    intervalos: tuple[Intervalo, ...] = ()
    nota: str = ""

    @property
    def decision(self) -> str:
        if self.valor_p is None:
            return "No aplicable"
        return "Se rechaza H0" if self.valor_p < self.alfa else "No se rechaza H0"


@dataclass(frozen=True)
class Analisis:
    muestra: Muestra
    pruebas: tuple[ResultadoPrueba, ...]
    minimo: float
    maximo: float
    media: float
    varianza: float
    distintos: int
    periodo_observado: int | None


@dataclass(frozen=True)
class ResultadoPi:
    puntos: int
    dentro: int
    estimacion: float
    error_absoluto: float


@dataclass(frozen=True)
class Medicion:
    parametros: ParametrosLCG
    resultado: ResultadoPi
    segundos: tuple[float, ...]
