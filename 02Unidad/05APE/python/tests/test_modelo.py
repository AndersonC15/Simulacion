import unittest
from pathlib import Path

from lcg_practica.controlador import ControladorExperimento
from lcg_practica.modelo import AnalizadorPeriodo, GeneradorLCG, ParametrosLCG


class PruebasLCG(unittest.TestCase):
    def test_vector_conocido_y_continuidad(self):
        generador = GeneradorLCG(ParametrosLCG())
        self.assertEqual([generador.siguiente() for _ in range(5)],
                         [87_628_868, 71_072_467, 2_332_836_374, 2_726_892_157, 3_908_547_000])
        self.assertEqual(generador.siguiente(), 483_019_191)

    def test_reproducibilidad_rango_y_cambio_de_semilla(self):
        p = ParametrosLCG()
        uno, dos = GeneradorLCG(p), GeneradorLCG(p)
        secuencia = [uno.siguiente() for _ in range(10_000)]
        self.assertEqual(secuencia, [dos.siguiente() for _ in range(10_000)])
        self.assertTrue(all(0 <= x < p.m and 0 <= x / p.m < 1 for x in secuencia))
        self.assertNotEqual(secuencia[0], GeneradorLCG(ParametrosLCG(semilla=54_321)).siguiente())

    def test_limites_y_aritmetica_exacta(self):
        for semilla in (-1, 2**32, 1.5, True):
            with self.subTest(semilla=semilla), self.assertRaises(ValueError):
                ParametrosLCG(semilla=semilla)
        with self.assertRaises(ValueError):
            ParametrosLCG(m=0)
        with self.assertRaises(ValueError):
            ParametrosLCG(a=2**32)
        extremo = GeneradorLCG(ParametrosLCG(a=2**32 - 1, c=2**32 - 1, semilla=2**32 - 1))
        self.assertEqual(extremo.siguiente(), 0)

    def test_hull_dobell_no_confunde_muestra_y_periodo(self):
        p = ParametrosLCG()
        generador = GeneradorLCG(p)
        analisis = AnalizadorPeriodo().analizar(p, tuple(generador.siguiente() for _ in range(10_000)))
        self.assertEqual(analisis.periodo_teorico, 4_294_967_296)
        self.assertIsNone(analisis.periodo_observado)

    def test_ciclo_pequeno_completo_y_preperiodo(self):
        p = ParametrosLCG(a=5, c=1, m=16, semilla=0)
        g = GeneradorLCG(p)
        analisis = AnalizadorPeriodo().analizar(p, tuple(g.siguiente() for _ in range(16)))
        self.assertEqual((analisis.periodo_teorico, analisis.preperiodo_observado, analisis.periodo_observado), (16, 0, 16))
        p = ParametrosLCG(a=2, c=0, m=8, semilla=1)
        g = GeneradorLCG(p)
        analisis = AnalizadorPeriodo().analizar(p, tuple(g.siguiente() for _ in range(5)))
        self.assertEqual((analisis.periodo_teorico, analisis.preperiodo_observado, analisis.periodo_observado), (None, 3, 1))

    def test_cada_condicion_hull_dobell(self):
        analizador = AnalizadorPeriodo()
        self.assertFalse(analizador.analizar(ParametrosLCG(a=5, c=2, m=16, semilla=0), ()).coprimos)
        self.assertFalse(analizador.analizar(ParametrosLCG(a=2, c=1, m=9, semilla=0), ()).factores_dividen)
        self.assertFalse(analizador.analizar(ParametrosLCG(a=3, c=1, m=8, semilla=0), ()).regla_cuatro)

    def test_controlador_admite_estrategia_y_vista_inyectadas(self):
        class GeneradorFijo:
            def siguiente(self):
                return 1

        class VistaMemoria:
            resultado = None

            def presentar(self, resultado, destino):
                self.resultado = resultado

        vista = VistaMemoria()
        controlador = ControladorExperimento(AnalizadorPeriodo(), vista)
        resultado = controlador.ejecutar(ParametrosLCG(), GeneradorFijo(), 3, Path("sin_archivos"))
        self.assertEqual(resultado.estados, (1, 1, 1))
        self.assertIs(vista.resultado, resultado)
        for cantidad in (0, -1, 1_000_001, True):
            with self.subTest(cantidad=cantidad), self.assertRaises(ValueError):
                controlador.ejecutar(ParametrosLCG(), GeneradorFijo(), cantidad, Path("."))


if __name__ == "__main__":
    unittest.main()

