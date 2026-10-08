"""Modelo matemático del índice de lluvia descrito en la guía."""

from dataclasses import dataclass
from math import isclose

import numpy as np


@dataclass(frozen=True)
class ParametrosModelo:
    """Pesos de las variables normalizadas del modelo."""
    humedad: float
    nubosidad: float
    temperatura: float
    nombre: str

    def __post_init__(self) -> None:
        pesos = (self.humedad, self.nubosidad, self.temperatura)
        if any(peso < 0 for peso in pesos):
            raise ValueError("Los pesos del modelo no pueden ser negativos.")
        if not isclose(sum(pesos), 1.0, abs_tol=1e-9):
            raise ValueError("La suma de los tres parámetros debe ser 1.0.")


# Parámetros predefinidos por la guía.
ORIGINAL = ParametrosModelo(0.50, 0.30, 0.20, "Modelo original")
# Ajuste: la nubosidad recibe 0.10 del peso de la humedad por ser una señal
# directa de formación de lluvia. 0.40 + 0.40 + 0.20 = 1.00.
AJUSTADO = ParametrosModelo(0.40, 0.40, 0.20, "Modelo ajustado")

TEMPERATURAS = np.array([10, 12, 14, 16, 18, 20, 22, 24, 26, 28], dtype=float)
FACTORES_TEMPERATURA = np.array(
    [1.00, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10], dtype=float
)


def normalizar_porcentaje(valor: float) -> float:
    if not 0 <= valor <= 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100.")
    return valor / 100


def calcular_factor_temperatura(temperatura: float) -> float:
    """Interpola valores intermedios y aplica los extremos de la tabla."""
    return float(np.interp(temperatura, TEMPERATURAS, FACTORES_TEMPERATURA))


def calcular_indice(h: float, n: float, tf: float, parametros: ParametrosModelo) -> float:
    return parametros.humedad * h + parametros.nubosidad * n + parametros.temperatura * tf

def clasificar_indice(indice: float) -> str:
    if indice < 0.40:
        return "Sin lluvia"
    if indice < 0.60:
        return "Baja posibilidad"
    if indice < 0.75:
        return "Lluvia probable"
    return "Lluvia"
