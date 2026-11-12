"""Coordina el experimento mediante contratos pequeños e inyección por constructor."""

from pathlib import Path
from typing import Protocol

from lcg_practica.modelo import (
    AnalizadorPeriodo,
    GeneradorPseudoaleatorio,
    ParametrosLCG,
    ResultadoExperimento,
)


class VistaExperimento(Protocol):
    def presentar(self, resultado: ResultadoExperimento, destino: Path) -> None: ...


class ControladorExperimento:
    def __init__(self, analizador: AnalizadorPeriodo, vista: VistaExperimento) -> None:
        self._analizador = analizador
        self._vista = vista

    def ejecutar(
        self,
        parametros: ParametrosLCG,
        generador: GeneradorPseudoaleatorio,
        cantidad: int,
        destino: Path,
    ) -> ResultadoExperimento:
        if type(cantidad) is not int or not 1 <= cantidad <= 1_000_000:
            raise ValueError("La cantidad debe estar entre 1 y 1 000 000.")
        estados = tuple(generador.siguiente() for _ in range(cantidad))
        resultado = ResultadoExperimento(
            parametros, estados, self._analizador.analizar(parametros, estados)
        )
        self._vista.presentar(resultado, destino)
        return resultado

