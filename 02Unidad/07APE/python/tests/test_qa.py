"""Diez campañas QA, con entradas adversarias e integración real Python/Java."""

import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from ape07.comparacion import auditar, comparar
from ape07.modelo import EstimadorPi, GeneradorLCG, Medicion, Parametros, Resultado, validar_tamanos


BASE = Path(__file__).resolve().parents[2]
JAR = BASE / "java/target/ape07.jar"


class FuenteFija:
    def __init__(self, valores):
        self.valores = iter(valores)

    def siguiente(self):
        return next(self.valores)


class CampanasQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not JAR.is_file():
            raise RuntimeError("Falta el JAR real; ejecuta scripts/preparar.sh antes de verificar.")
        cls.temporal = tempfile.TemporaryDirectory(prefix="ape07-qa-")
        cls.carpeta = Path(cls.temporal.name)
        cls.addClassCleanup(cls.temporal.cleanup)
        for lenguaje in ("python", "java"):
            cls.ejecutar(lenguaje, ["--semilla", "1", "--tamanos", "10,1000", "--repeticiones", "2",
                                    "--salida", str(cls.carpeta / lenguaje)], 0)

    @classmethod
    def ejecutar(cls, lenguaje, argumentos, esperado):
        comando = [sys.executable, "-m", "ape07"] if lenguaje == "python" else ["java", "-jar", str(JAR)]
        resultado = subprocess.run(comando + argumentos, text=True, capture_output=True, timeout=60)
        if resultado.returncode != esperado:
            raise AssertionError((lenguaje, argumentos, resultado.returncode, resultado.stdout, resultado.stderr))
        return resultado

    def copia(self, nombre):
        destino = self.carpeta / nombre
        shutil.copytree(self.carpeta / "python", destino)
        return destino

    def test_01_vector_conocido_y_aritmetica_extrema(self):
        fuente = GeneradorLCG(Parametros(1))
        self.assertEqual([fuente.siguiente_entero() for _ in range(5)],
                         [16807, 282475249, 1622650073, 984943658, 1144108930])
        for semilla in (1, 2147483646):
            fuente = GeneradorLCG(Parametros(semilla))
            self.assertTrue(all(0 < fuente.siguiente() < 1 for _ in range(10000)))

    def test_02_geometria_y_consumo_exacto_2n(self):
        fuente = FuenteFija([.5, .5, 0, .5, .5, 0, 0, 0])
        resultado = EstimadorPi().estimar(4, fuente)
        self.assertEqual((resultado.dentro, resultado.estimacion), (3, 3.0))
        with self.assertRaises(StopIteration):
            fuente.siguiente()
        self.assertEqual(resultado.error_absoluto, abs(3.0 - math.pi))

    def test_03_fuentes_y_parametros_invalidos(self):
        for semilla in (0, -1, 2147483647, True, 1.5, "1", 10**100):
            with self.subTest(semilla=semilla), self.assertRaises(ValueError):
                Parametros(semilla)
        for valor in (-.1, 1, math.inf, math.nan):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                EstimadorPi().estimar(1, FuenteFija([valor, .5]))
        for tamanos in ((), (0,), (-1,), (1000001,), (True,), (10, 1), (10, 10)):
            with self.subTest(tamanos=tamanos), self.assertRaises(ValueError):
                validar_tamanos(tamanos)

    def test_04_reproducibilidad_prefijos_y_semillas(self):
        for semilla in (1, 123457, 2147483646):
            primera, segunda = GeneradorLCG(Parametros(semilla)), GeneradorLCG(Parametros(semilla))
            self.assertEqual([primera.siguiente_entero() for _ in range(20000)],
                             [segunda.siguiente_entero() for _ in range(20000)])
        self.assertNotEqual(GeneradorLCG(Parametros(1)).siguiente_entero(),
                            GeneradorLCG(Parametros(123457)).siguiente_entero())

    def test_05_cli_adversaria_ambos_lenguajes(self):
        casos = (["--semilla", "0"], ["--semilla", "-1"], ["--semilla", "2147483647"],
                 ["--semilla", "abc"], ["--tamanos", ""], ["--tamanos", "1,"],
                 ["--tamanos", "0"], ["--tamanos", "1000001"], ["--tamanos", "10,1"],
                 ["--tamanos", "1,1"], ["--repeticiones", "0"], ["--repeticiones", "31"],
                 ["--desconocido", "1"], ["--salida"])
        for lenguaje in ("python", "java"):
            for argumentos in casos:
                with self.subTest(lenguaje=lenguaje, argumentos=argumentos):
                    respuesta = self.ejecutar(lenguaje, argumentos, 2)
                    self.assertNotIn("Traceback", respuesta.stderr)
                    self.assertNotIn("Exception in thread", respuesta.stderr)

    def test_06_integracion_exacta_y_ruta_con_espacios(self):
        tabla = comparar(self.carpeta / "python", self.carpeta / "java", self.carpeta / "comparacion")
        self.assertEqual(list(tabla["N"]), [10, 1000])
        self.assertTrue(tabla["coinciden"].all())
        for lenguaje in ("python", "java"):
            destino = self.carpeta / (lenguaje + " ruta con espacios")
            self.ejecutar(lenguaje, ["--tamanos", "1", "--repeticiones", "1", "--salida", str(destino)], 0)
            auditar(destino, lenguaje.capitalize() if lenguaje == "python" else "Java")

    def test_07_detectar_manipulacion_estado_incluso_con_hash_actualizado(self):
        carpeta = self.copia("estado_alterado")
        archivo = carpeta / "secuencia.bin"
        contenido = bytearray(archivo.read_bytes())
        contenido[403] ^= 1
        archivo.write_bytes(contenido)
        metadatos = json.loads((carpeta / "entorno.json").read_text())
        metadatos["sha256_secuencia"] = hashlib.sha256(contenido).hexdigest()
        (carpeta / "entorno.json").write_text(json.dumps(metadatos))
        with self.assertRaisesRegex(ValueError, "Recurrencia"):
            auditar(carpeta, "Python")
        archivo.write_bytes(contenido[:-1])
        with self.assertRaisesRegex(ValueError, "Longitud"):
            auditar(carpeta, "Python")

    def test_08_detectar_resultados_tiempos_y_metadatos_incoherentes(self):
        for nombre, archivo, columna, valor in (
            ("pi", "resumen.csv", "pi_estimado", "3.141592653589793"),
            ("conteo", "resumen.csv", "dentro", "-1"),
            ("mediana", "resumen.csv", "tiempo_mediana_s", "999"),
            ("tiempo", "tiempos.csv", "segundos", "nan"),
            ("repeticion", "tiempos.csv", "repeticion", "2"),
            ("punto", "primeros20.csv", "x", "99"),
        ):
            with self.subTest(nombre=nombre):
                carpeta = self.copia(nombre)
                ruta = carpeta / archivo
                with ruta.open(newline="") as entrada:
                    lector = csv.DictReader(entrada)
                    columnas, filas = lector.fieldnames, list(lector)
                filas[0][columna] = valor
                with ruta.open("w", newline="") as salida:
                    escritor = csv.DictWriter(salida, fieldnames=columnas)
                    escritor.writeheader()
                    escritor.writerows(filas)
                with self.assertRaises(ValueError):
                    auditar(carpeta, "Python")
        for campo, valor in (("lenguaje", "Java"), ("repeticiones", 0), ("valores_lcg", 1),
                             ("geometria", "otra geometría"), ("incluye_io_en_tiempo", True),
                             ("sha256_secuencia", "0" * 64), ("tamanos", [1000, 10])):
            with self.subTest(campo=campo):
                carpeta = self.copia("metadatos_" + campo)
                ruta = carpeta / "entorno.json"
                metadatos = json.loads(ruta.read_text())
                metadatos[campo] = valor
                ruta.write_text(json.dumps(metadatos))
                with self.assertRaises(ValueError):
                    auditar(carpeta, "Python")
        carpeta = self.copia("faltante")
        (carpeta / "secuencia.bin").unlink()
        with self.assertRaises(FileNotFoundError):
            auditar(carpeta, "Python")

    def test_09_rechazar_salida_no_escribible_y_mediana(self):
        archivo = self.carpeta / "es_un_archivo"
        archivo.write_text("No es una carpeta")
        for lenguaje in ("python", "java"):
            self.ejecutar(lenguaje, ["--tamanos", "1", "--repeticiones", "1", "--salida", str(archivo)], 2)
        self.assertEqual(Medicion(Resultado(1, 1), (9., 1., 3.)).mediana, 3)
        self.assertEqual(Medicion(Resultado(1, 1), (3., 1.)).mediana, 2)

    def test_10_carga_un_millon_y_semilla_limite(self):
        for lenguaje in ("python", "java"):
            destino = self.carpeta / (lenguaje + "_carga")
            self.ejecutar(lenguaje, ["--semilla", "2147483646", "--tamanos", "1000,10000,100000,1000000",
                                     "--repeticiones", "1", "--salida", str(destino)], 0)
        tabla = comparar(self.carpeta / "python_carga", self.carpeta / "java_carga", self.carpeta / "carga")
        self.assertEqual(len(tabla), 4)
        self.assertTrue(tabla["coinciden"].all())
        self.assertEqual((self.carpeta / "python_carga/secuencia.bin").stat().st_size, 8000000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
