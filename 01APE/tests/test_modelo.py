import unittest
from decimal import Decimal, localcontext
from fractions import Fraction

from Modelo.datos import REGISTROS
from Modelo.modelo import (
    AJUSTADO, ORIGINAL, ModeloLluvia, RegistroMeteorologico, ParametrosModelo, calcular_factor_temperatura,
    calcular_indice, clasificar_indice, normalizar_porcentaje,
)
from Modelo.precision import convertir_decimal, multiplicar, sumar


class PruebasModelo(unittest.TestCase):
    def setUp(self):
        self.modelo = ModeloLluvia()

    def evaluar(self, h, n, t, parametros=ORIGINAL):
        return self.modelo.evaluar(RegistroMeteorologico("Prueba", h, n, t), parametros)

    def test_tablas_de_referencia(self):
        originales = (".605", ".640", ".595", ".470", ".685", ".800", ".885", ".840", ".775")
        ajustados = (".580", ".620", ".572", ".440", ".680", ".800", ".888", ".842", ".770")
        for parametros, esperados in ((ORIGINAL, originales), (AJUSTADO, ajustados)):
            self.assertEqual([f.indice for f in self.modelo.evaluar_tabla(REGISTROS, parametros)],
                             [Decimal(v) for v in esperados])

    def test_ejemplo_y_regresiones(self):
        for h, n, t, esperado, estado in (
            (90, 80, 18, ".81", "Lluvia"),
            (35, 35, 18, ".40", "Baja posibilidad"),
            (70, 100, 20, ".75", "Lluvia"),
        ):
            resultado = self.evaluar(h, n, t)
            self.assertEqual(resultado.indice, Decimal(esperado))
            self.assertEqual(resultado.estado, estado)

    def test_tabla_termica_e_interpolacion(self):
        for t, esperado in zip(range(10, 29, 2), ("1", ".9", ".8", ".7", ".6", ".5", ".4", ".3", ".2", ".1")):
            self.assertEqual(calcular_factor_temperatura(t), Decimal(esperado))
        for t, esperado in ((-50, "1"), (60, ".1"), (15, ".75"), (17, ".65")):
            self.assertEqual(calcular_factor_temperatura(t), Decimal(esperado))

    def test_limites_y_vecinos_muy_proximos(self):
        for limite, inferior, superior, antes, desde in (
            (".40", ".399999999999999999999999999999999999", ".400000000000000000000000000000000001", "Sin lluvia", "Baja posibilidad"),
            (".60", ".599999999999999999999999999999999999", ".600000000000000000000000000000000001", "Baja posibilidad", "Lluvia probable"),
            (".75", ".749999999999999999999999999999999999", ".750000000000000000000000000000000001", "Lluvia probable", "Lluvia"),
        ):
            self.assertEqual(clasificar_indice(inferior), antes)
            self.assertEqual(clasificar_indice(limite), desde)
            self.assertEqual(clasificar_indice(superior), desde)

    def test_mas_de_28_digitos_con_referencia_racional(self):
        h = "35.123456789012345678901234567890123456789"
        n = "35.987654321098765432109876543210987654321"
        t = "17.123456789012345678901234567890123456789"
        esperado_tf = (Fraction(30) - Fraction(t)) / 20
        esperado = Fraction(h) / 200 + 3 * Fraction(n) / 1000 + esperado_tf / 5
        with localcontext() as contexto:
            contexto.prec = 3
            resultado = self.evaluar(h, n, t)
        self.assertEqual(Fraction(resultado.indice), esperado)
        self.assertEqual(Fraction(resultado.factor_temperatura), esperado_tf)

    def test_precision_maxima_admitida_y_pesos_largos(self):
        a = "0." + "3" * 120
        c = "0." + "3" * 119 + "4"
        parametros = ParametrosModelo(a, a, c, "Pesos de 120 dígitos")
        h, n, t = "99." + "9" * 118, "0." + "1" * 120, "17." + "1" * 118
        esperado_tf = (Fraction(30) - Fraction(t)) / 20
        esperado = Fraction(a) * Fraction(h) / 100 + Fraction(a) * Fraction(n) / 100 + Fraction(c) * esperado_tf
        with localcontext() as contexto:
            contexto.prec = 2
            resultado = self.evaluar(h, n, t, parametros)
            porcentaje = resultado.porcentaje
        self.assertEqual(Fraction(resultado.indice), esperado)
        self.assertEqual(Fraction(porcentaje), esperado * 100)
        self.assertGreater(len(resultado.indice.as_tuple().digits), 120)

    def test_exponente_minimo_y_resultados_con_mas_decimales(self):
        parametros = ParametrosModelo("1e-120", "0." + "9" * 120, "0", "Extremos")
        resultado = self.evaluar("1e-120", "0", "60", parametros)
        self.assertEqual(resultado.indice, Decimal("1e-242"))
        self.assertEqual(resultado.porcentaje, Decimal("1e-240"))

    def test_calculo_completo_a_ambos_lados_de_los_umbrales(self):
        for h, n, t, antes, desde in (
            (35, 35, 18, "Sin lluvia", "Baja posibilidad"),
            (75, 35, 18, "Baja posibilidad", "Lluvia probable"),
            (70, 100, 20, "Lluvia probable", "Lluvia"),
        ):
            for humedad, estado in ((f"{h - 1}." + "9" * 100, antes),
                                     (str(h), desde), (f"{h}." + "0" * 99 + "1", desde)):
                resultado = self.evaluar(humedad, n, t)
                tf = (Fraction(30) - t) / 20
                esperado = Fraction(humedad) / 200 + Fraction(3 * n, 1000) + tf / 5
                self.assertEqual(Fraction(resultado.indice), esperado)
                self.assertEqual(resultado.estado, estado)

    def test_operaciones_y_pesos_exactos(self):
        self.assertEqual(sumar(ORIGINAL.humedad, ORIGINAL.nubosidad, ORIGINAL.temperatura), Decimal(1))
        self.assertEqual(sumar(AJUSTADO.humedad, AJUSTADO.nubosidad, AJUSTADO.temperatura), Decimal(1))
        self.assertEqual(multiplicar(Decimal("1e-120"), Decimal("1e-120")), Decimal("1e-240"))
        for pesos in (("-.1", ".9", ".2"), ("NaN", "0", "1"), ("Infinity", "0", "0"), (".5", ".3", ".200000000000000000000000000000000001")):
            with self.subTest(pesos=pesos), self.assertRaises(ValueError):
                ParametrosModelo(*pesos, "Inválido")

    def test_modelo_rechaza_datos_invalidos(self):
        for valor in ("-1", "101", "NaN", "Infinity", "texto", "", 0.1, True):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                normalizar_porcentaje(valor)
        for valor in ("-51", "61", "sNaN", "-Infinity"):
            with self.assertRaises(ValueError):
                calcular_factor_temperatura(valor)
        with self.assertRaises(ValueError):
            calcular_indice("1.1", ".5", ".5", ORIGINAL)
        with self.assertRaises(ValueError):
            clasificar_indice(Decimal("NaN"))

    def test_barrido_independiente_de_946_casos(self):
        casos = 0
        errores = []
        # Referencia entera independiente: 1000I = 5h + 3n + 300 - 10t.
        for h in range(101):
            for n in range(101):
                for t in range(10, 29):
                    numerador = 5 * h + 3 * n + 300 - 10 * t
                    if numerador not in (400, 600, 750):
                        continue
                    casos += 1
                    esperado = {400: "Baja posibilidad", 600: "Lluvia probable", 750: "Lluvia"}[numerador]
                    resultado = self.evaluar(h, n, t)
                    if resultado.estado != esperado or Fraction(resultado.indice) != Fraction(numerador, 1000):
                        errores.append((h, n, t))
        self.assertEqual(casos, 946)
        self.assertEqual(errores, [])

    def test_politica_de_entrada(self):
        self.assertEqual(convertir_decimal(" 35,25 "), Decimal("35.25"))
        for valor in ("1,2.3", "1,2,3", "1e121", "1e-121", "0e999", "9" * 121, " " + "1" * 257):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                convertir_decimal(valor)


if __name__ == "__main__":
    unittest.main()
