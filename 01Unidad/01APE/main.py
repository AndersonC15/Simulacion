"""Punto de entrada: construye y conecta los componentes MVC."""

from Controlador.controlador import ControladorLluvia
from Modelo.datos import REGISTROS
from Modelo.modelo import ModeloLluvia
from Vista.consola import VistaConsola
from Vista.graficas import VistaGraficas


def main() -> None:
    modelo = ModeloLluvia()
    vista = VistaConsola()
    graficas = VistaGraficas()
    controlador = ControladorLluvia(modelo, vista, graficas.generar, REGISTROS)
    controlador.ejecutar()


if __name__ == "__main__":
    main()
