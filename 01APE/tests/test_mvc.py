import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

from Controlador.controlador import ControladorLluvia
from Modelo.datos import REGISTROS
from Modelo.modelo import ModeloLluvia, RegistroMeteorologico
from Vista.consola import VistaConsola, texto_decimal


class PruebasMVC(unittest.TestCase):
    def test_controlador_coordina_todas_las_opciones(self):
        vista = Mock(spec=VistaConsola)
        vista.leer_opcion.side_effect = ["1", "2", "3", "4", "0"]
        vista.leer_registro.return_value = RegistroMeteorologico("Manual", 90, 80, 18)
        graficar = Mock(return_value=[Path("variables.png"), Path("comparacion.png")])
        ControladorLluvia(ModeloLluvia(), vista, graficar, REGISTROS).ejecutar()
        self.assertEqual(vista.mostrar_tabla.call_count, 2)
        self.assertEqual(len(vista.mostrar_tabla.call_args.args[0]), 9)
        graficar.assert_called_once()
        self.assertEqual(vista.mostrar_resultado.call_args.args[0].indice, Decimal(".81"))

    def test_tabla_adapta_anchos_y_no_recorta_decimales(self):
        salida = []
        largo = "35.123456789012345678901234567890123456789"
        resultado = ModeloLluvia().evaluar(RegistroMeteorologico("Prueba", largo, largo, 17))
        VistaConsola(escribir=salida.append).mostrar_tabla([resultado], "Tabla")
        self.assertIn(largo, "\n".join(salida))
        self.assertIn(texto_decimal(resultado.indice), "\n".join(salida))
        cabecera, fila = salida[1:3]
        self.assertEqual([i for i, c in enumerate(cabecera) if c == "|"],
                         [i for i, c in enumerate(fila) if c == "|"])

    def test_modelo_no_depende_de_la_interfaz(self):
        for archivo in Path("Modelo").glob("*.py"):
            arbol = ast.parse(archivo.read_text())
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.ImportFrom):
                    self.assertFalse((nodo.module or "").startswith(("Vista", "Controlador", "matplotlib", "numpy")))
                if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                    self.assertNotIn(nodo.func.id, ("input", "print", "float", "round"))


if __name__ == "__main__":
    unittest.main()
