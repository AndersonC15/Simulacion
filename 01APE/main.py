"""Punto de entrada: construye y conecta los componentes MVC."""

from Controlador.controlador import ControladorLluvia
from Modelo.datos import REGISTROS
from Modelo.modelo import ModeloLluvia
from Vista.consola import VistaConsola
from Vista.graficas import generar_graficas


def main() -> None:
    modelo = ModeloLluvia()
    vista = VistaConsola()
    controlador = ControladorLluvia(modelo, vista, generar_graficas, REGISTROS)
    controlador.ejecutar()


if __name__ == "__main__":
    main()
