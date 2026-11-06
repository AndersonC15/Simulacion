"""Recurrencia y normalizacion de la Semana 5, paginas 7 y 19."""

import numpy as np

from .datos import Muestra, ParametrosLCG


class GeneradorLCG:
    def __init__(self, parametros: ParametrosLCG) -> None:
        self.parametros = parametros
        self._estado = parametros.semilla

    def siguiente_entero(self) -> int:
        p = self.parametros
        self._estado = (p.a * self._estado + p.c) % p.m
        return self._estado

    def siguiente(self) -> float:
        return self.siguiente_entero() / self.parametros.m

    def generar(self, cantidad: int) -> Muestra:
        if type(cantidad) is not int or cantidad < 1:
            raise ValueError("La cantidad debe ser un entero positivo.")
        estados = np.fromiter(
            (self.siguiente_entero() for _ in range(cantidad)), dtype=np.int64, count=cantidad
        )
        valores = estados.astype(np.float64) / self.parametros.m
        estados.flags.writeable = False
        valores.flags.writeable = False
        return Muestra(self.parametros, estados, valores)
