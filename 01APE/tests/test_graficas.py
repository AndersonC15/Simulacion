import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image

from Controlador.controlador import ControladorLluvia
from Modelo.datos import REGISTROS
from Modelo.modelo import AJUSTADO, ORIGINAL, ModeloLluvia
from Vista.consola import VistaConsola
from Vista.graficas import VistaGraficas, backend_interactivo


class PruebasGraficas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        modelo = ModeloLluvia()
        cls.original = modelo.evaluar_tabla(REGISTROS, ORIGINAL)
        cls.ajustado = modelo.evaluar_tabla(REGISTROS, AJUSTADO)

    def test_registro_real_de_backends(self):
        self.assertFalse(backend_interactivo("Agg"))
        self.assertTrue(backend_interactivo("TkAgg"))
        self.assertTrue(backend_interactivo("QtAgg"))

    def test_png_curvas_umbrales_y_cierre_de_figuras(self):
        with tempfile.TemporaryDirectory() as carpeta:
            vista = VistaGraficas(Path(carpeta))
            with patch.object(plt, "show") as mostrar, patch.object(plt, "close", wraps=plt.close) as cerrar:
                entrega = vista.generar(self.original, self.ajustado)
            mostrar.assert_not_called()
            self.assertIn("sin ventanas", entrega.mensaje)
            for ruta in entrega.rutas:
                with Image.open(ruta) as imagen:
                    self.assertEqual(imagen.format, "PNG")
                    self.assertGreater(imagen.width, 1000)
                    imagen.verify()
            figuras = [llamada.args[0] for llamada in cerrar.call_args_list if isinstance(llamada.args[0], Figure)]
            variables, comparacion = [figura.axes[0] for figura in figuras]
            self.assertEqual(len(variables.lines), 3)
            self.assertEqual(list(variables.lines[0].get_ydata()), [.65, .70, .68, .60, .75, .85, .92, .88, .80])
            self.assertEqual(list(variables.lines[1].get_ydata()), [.40, .50, .45, .30, .70, .85, .95, .90, .75])
            self.assertEqual(list(variables.lines[2].get_ydata()), [.80, .70, .60, .40, .50, .60, .70, .65, .75])
            self.assertEqual(len(comparacion.lines), 5)
            self.assertEqual(list(comparacion.lines[0].get_ydata()), [.605, .640, .595, .470, .685, .800, .885, .840, .775])
            self.assertEqual(list(comparacion.lines[1].get_ydata()), [.580, .620, .572, .440, .680, .800, .888, .842, .770])
            self.assertEqual([list(linea.get_ydata()) for linea in comparacion.lines[2:]], [[.4, .4], [.6, .6], [.75, .75]])
            for eje in (variables, comparacion):
                self.assertEqual([t.get_text() for t in eje.get_xticklabels()], [r.hora for r in REGISTROS])
                self.assertTrue(eje.get_title())
                self.assertEqual(eje.get_xlabel(), "Hora")
                self.assertTrue(eje.get_ylabel())
                self.assertIsNotNone(eje.get_legend())
                self.assertTrue(any(linea.get_visible() for linea in eje.get_xgridlines()))
        self.assertEqual(plt.get_fignums(), [])

    def test_simulacion_de_show_con_tkagg_y_qtagg(self):
        # Renderer Agg real; nombre de backend y show simulados. No prueba ventanas.
        for backend in ("TkAgg", "QtAgg"):
            with self.subTest(backend=backend), tempfile.TemporaryDirectory() as carpeta:
                with patch.object(plt, "get_backend", return_value=backend), patch.object(plt, "show") as mostrar:
                    VistaGraficas(Path(carpeta)).generar(self.original, self.ajustado)
                mostrar.assert_called_once_with(block=True)
        self.assertEqual(plt.get_fignums(), [])

    def test_repeticion_y_figuras_ajenas(self):
        ajena = plt.figure()
        try:
            with tempfile.TemporaryDirectory() as carpeta:
                vista = VistaGraficas(Path(carpeta))
                for _ in range(2):
                    vista.generar(self.original, self.ajustado)
                    self.assertEqual(plt.get_fignums(), [ajena.number])
        finally:
            plt.close(ajena)

    def test_error_de_directorio_y_error_de_escritura(self):
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "ocupado"
            archivo.touch()
            with self.assertRaises(FileExistsError):
                VistaGraficas(archivo).generar(self.original, self.ajustado)
            with patch.object(Path, "mkdir", side_effect=PermissionError("sin permisos")):
                with self.assertRaises(PermissionError):
                    VistaGraficas(Path(carpeta)).generar(self.original, self.ajustado)
            with patch.object(Figure, "savefig", side_effect=OSError("disco lleno")):
                with self.assertRaises(OSError):
                    VistaGraficas(Path(carpeta)).generar(self.original, self.ajustado)
        self.assertEqual(plt.get_fignums(), [])

    def test_controlador_no_anuncia_exito_si_falla_el_guardado(self):
        salida = []
        vista = VistaConsola(Mock(side_effect=["3", "0"]), salida.append)
        ControladorLluvia(ModeloLluvia(), vista, Mock(side_effect=PermissionError("sin permisos")), REGISTROS).ejecutar()
        self.assertIn("No se completó", "\n".join(salida))
        self.assertNotIn("generadas correctamente", "\n".join(salida))
        self.assertEqual(salida[-1], "Programa finalizado.")

    def test_fallback_simulado_si_no_inicia_el_backend(self):
        crear_real = plt.subplots
        llamadas = 0

        def crear(*args, **kwargs):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 1:
                raise ImportError("toolkit ausente (simulado)")
            return crear_real(*args, **kwargs)

        with tempfile.TemporaryDirectory() as carpeta, patch.object(plt, "subplots", side_effect=crear):
            entrega = VistaGraficas(Path(carpeta)).generar(self.original, self.ajustado)
            self.assertIn("toolkit ausente (simulado)", entrega.mensaje)
            self.assertTrue(all(ruta.is_file() for ruta in entrega.rutas))

    def test_fallo_simulado_de_show_conserva_png_y_cierra_figuras(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with patch.object(plt, "get_backend", return_value="TkAgg"), patch.object(plt, "show", side_effect=RuntimeError("fallo GUI simulado")):
                entrega = VistaGraficas(Path(carpeta)).generar(self.original, self.ajustado)
            self.assertTrue(all(ruta.is_file() for ruta in entrega.rutas))
            self.assertIn("no se pudieron mostrar", entrega.mensaje)
        self.assertEqual(plt.get_fignums(), [])


if __name__ == "__main__":
    unittest.main()
