import os
import signal
import subprocess
import sys
import unittest
from decimal import Decimal
from unittest.mock import Mock

from Controlador.controlador import ControladorLluvia
from Modelo.datos import REGISTROS
from Modelo.modelo import ModeloLluvia, RegistroMeteorologico
from Modelo.precision import convertir_decimal
from Vista.consola import VistaConsola


class PruebasEntradas(unittest.TestCase):
    def test_formatos_validos_y_extremos(self):
        for texto, esperado in ((" 35,25 ", "35.25"), ("+1.5e1", "15"), (".5", ".5"), ("0", "0"), ("100", "100")):
            self.assertEqual(convertir_decimal(texto), Decimal(esperado))
        for h, n, t in ((0, 100, -50), (100, 0, 60)):
            ModeloLluvia().evaluar(RegistroMeteorologico("Extremo", h, n, t))

    def test_recupera_todos_los_errores_y_conserva_el_texto(self):
        invalidos = ["hola", "", " ", "1,2.3", "1.2,3", "1,2,3", "1 000", "-1", "101",
                     "NaN", "nan", "sNaN", "+Inf", "-Infinity", "∞", "9" * 257, "9" * 121,
                     "1e121", "1e-121", "0e999", " " * 257 + "1"]
        largo = "35.123456789012345678901234567890123456789"
        leer = Mock(side_effect=[*invalidos, largo])
        salida = []
        self.assertEqual(VistaConsola(leer, salida.append).leer_numero("H: ", "humedad"), Decimal(largo))
        self.assertEqual(len(salida), len(invalidos))
        self.assertTrue(all("Entrada inválida:" in linea for linea in salida))

    def test_validacion_directa_del_registro(self):
        for campo in ("humedad", "nubosidad", "temperatura"):
            for valor in ("NaN", "Infinity", Decimal("sNaN"), "1e121", "9" * 257, 0.5):
                datos = dict(humedad=50, nubosidad=50, temperatura=20)
                datos[campo] = valor
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    RegistroMeteorologico("Prueba", **datos)

    def test_menu_invalido_y_operaciones_repetidas(self):
        salida = []
        leer = Mock(side_effect=["99", "", " 1 ", "2", "4", "mal", "35,0", "35", "18", "4", "70", "100", "20", "0"])
        vista = VistaConsola(leer, salida.append)
        ControladorLluvia(ModeloLluvia(), vista, Mock(), REGISTROS).ejecutar()
        texto = "\n".join(salida)
        self.assertEqual(texto.count("Opción no válida."), 2)
        self.assertIn("Índice I = 0.4 (40%)", texto)
        self.assertIn("Índice I = 0.75 (75%)", texto)
        self.assertEqual(salida[-1], "Programa finalizado.")

    def test_eof_y_ctrl_c_en_menu_y_cada_campo(self):
        for interrupcion in (EOFError, KeyboardInterrupt):
            for previos in ([], ["4"], ["4", "35"], ["4", "35", "35"]):
                salida = []
                vista = VistaConsola(Mock(side_effect=[*previos, interrupcion]), salida.append)
                ControladorLluvia(ModeloLluvia(), vista, Mock(), REGISTROS).ejecutar()
                self.assertIn("Programa finalizado.", salida[-1])

    def test_eof_en_proceso_real(self):
        resultado = subprocess.run([sys.executable, "main.py"], input="4\n35\n", text=True,
                                   capture_output=True, timeout=30,
                                   env={**os.environ, "MPLBACKEND": "Agg"})
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Fin de entrada.", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stderr)

    @unittest.skipUnless(os.name == "posix", "La señal SIGINT se verifica en POSIX")
    def test_ctrl_c_en_proceso_real(self):
        # Espera el menú: SIGINT se envía cuando el controlador ya está leyendo.
        with subprocess.Popen([sys.executable, "-u", "main.py"], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              env={**os.environ, "MPLBACKEND": "Agg"}) as proceso:
            while True:
                linea = proceso.stdout.readline()
                if "0. Salir" in linea or not linea:
                    break
            proceso.send_signal(signal.SIGINT)
            salida, errores = proceso.communicate(timeout=10)
        self.assertEqual(proceso.returncode, 0, errores)
        self.assertIn("Operación interrumpida.", salida)
        self.assertNotIn("Traceback", errores)


if __name__ == "__main__":
    unittest.main()
