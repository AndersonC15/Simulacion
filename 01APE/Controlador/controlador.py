"""Coordinación del menú: la vista presenta y el modelo calcula."""

from collections.abc import Callable
from pathlib import Path

from Modelo.modelo import AJUSTADO, ORIGINAL, ModeloLluvia, RegistroMeteorologico, ResultadoLluvia
from Vista.consola import VistaConsola


class ControladorLluvia:
    def __init__(self, modelo: ModeloLluvia, vista: VistaConsola,
                 graficar: Callable[[list[ResultadoLluvia], list[ResultadoLluvia]], list[Path]],
                 registros: tuple[RegistroMeteorologico, ...]) -> None:
        self.modelo = modelo
        self.vista = vista
        self.graficar = graficar
        self.registros = registros

    def ejecutar(self) -> None:
        try:
            self._ejecutar_menu()
        except EOFError:
            self.vista.mostrar_mensaje("\nFin de entrada. Programa finalizado.")
        except KeyboardInterrupt:
            self.vista.mostrar_mensaje("\nOperación interrumpida. Programa finalizado.")

    def _ejecutar_menu(self) -> None:
        originales = self.modelo.evaluar_tabla(self.registros, ORIGINAL)
        ajustados = self.modelo.evaluar_tabla(self.registros, AJUSTADO)
        while True:
            opcion = self.vista.leer_opcion()
            if opcion == "1":
                self.vista.mostrar_tabla(originales, ORIGINAL.descripcion)
            elif opcion == "2":
                self.vista.mostrar_tabla(ajustados, AJUSTADO.descripcion)
            elif opcion == "3":
                rutas = self.graficar(originales, ajustados)
                self.vista.mostrar_mensaje("Gráficas generadas correctamente:")
                for ruta in rutas:
                    self.vista.mostrar_mensaje(str(ruta))
            elif opcion == "4":
                registro = self.vista.leer_registro()
                self.vista.mostrar_resultado(self.modelo.evaluar(registro))
            elif opcion == "0":
                self.vista.mostrar_mensaje("Programa finalizado.")
                return
            else:
                self.vista.mostrar_mensaje("Opción no válida.")
