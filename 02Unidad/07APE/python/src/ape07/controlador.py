"""Coordina el modelo y la vista, sin implementar la fórmula Monte Carlo."""

from pathlib import Path

from ape07.modelo import Medicion, MedidorRendimiento, Parametros, validar_tamanos
from ape07.vista import VistaResultados


class ControladorExperimento:
    def __init__(self, medidor: MedidorRendimiento, vista: VistaResultados) -> None:
        self.medidor = medidor
        self.vista = vista

    def ejecutar(self, parametros: Parametros, tamanos: tuple[int, ...], repeticiones: int,
                 salida: Path) -> tuple[Medicion, ...]:
        validar_tamanos(tamanos)
        mediciones = tuple(self.medidor.medir(parametros, puntos, repeticiones) for puntos in tamanos)
        self.vista.guardar(parametros, mediciones, salida)
        self.vista.mostrar(mediciones, salida)
        return mediciones
