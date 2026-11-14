"""Vista de consola y archivos; la exportación queda fuera del tiempo medido."""

import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import struct

from ape07.modelo import GeneradorLCG, Medicion, Parametros


class VistaResultados:
    def guardar(self, parametros: Parametros, mediciones: tuple[Medicion, ...], salida: Path) -> None:
        salida.mkdir(parents=True, exist_ok=True)
        with (salida / "resumen.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("n", "dentro", "pi_estimado", "error_absoluto", "tiempo_mediana_s",
                                "tiempo_minimo_s", "repeticiones"))
            for medicion in mediciones:
                resultado = medicion.resultado
                escritor.writerow((resultado.puntos, resultado.dentro, resultado.estimacion,
                                    resultado.error_absoluto, medicion.mediana,
                                    min(medicion.segundos), len(medicion.segundos)))
        with (salida / "tiempos.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("n", "repeticion", "segundos"))
            for medicion in mediciones:
                escritor.writerows((medicion.resultado.puntos, indice, tiempo)
                                    for indice, tiempo in enumerate(medicion.segundos, 1))
        cantidad = 2 * max(medicion.resultado.puntos for medicion in mediciones)
        generador = GeneradorLCG(parametros)
        huella = hashlib.sha256()
        with (salida / "secuencia.bin").open("wb") as archivo:
            for inicio in range(0, cantidad, 4096):
                bloque = b"".join(struct.pack(">I", generador.siguiente_entero())
                                 for _ in range(min(4096, cantidad - inicio)))
                archivo.write(bloque)
                huella.update(bloque)
        generador = GeneradorLCG(parametros)
        with (salida / "primeros20.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("punto", "estado_x", "estado_y", "x", "y", "dentro"))
            for indice in range(1, min(20, cantidad // 2) + 1):
                estado_x, estado_y = generador.siguiente_entero(), generador.siguiente_entero()
                coordenada_x = 2.0 * (estado_x / parametros.modulo) - 1.0
                coordenada_y = 2.0 * (estado_y / parametros.modulo) - 1.0
                dentro = coordenada_x * coordenada_x + coordenada_y * coordenada_y <= 1.0
                escritor.writerow((indice, estado_x, estado_y, coordenada_x, coordenada_y, int(dentro)))
        metadatos = {
            "lenguaje": "Python", "version": platform.python_version(), "sistema": platform.platform(),
            "parametros": {**asdict(parametros), "a": parametros.multiplicador,
                           "c": parametros.incremento, "m": parametros.modulo},
            "geometria": "cuadrado [-1,1)²; circulo x²+y²<=1", "formato_secuencia": "uint32-be",
            "valores_lcg": cantidad, "sha256_secuencia": huella.hexdigest(),
            "tamanos": [medicion.resultado.puntos for medicion in mediciones],
            "repeticiones": len(mediciones[0].segundos), "calentamientos": 3,
            "reloj": "perf_counter", "incluye_io_en_tiempo": False,
        }
        (salida / "entorno.json").write_text(json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")

    def mostrar(self, mediciones: tuple[Medicion, ...], salida: Path) -> None:
        print("Monte Carlo | Python | cuadrado [-1,1)² y círculo de radio 1")
        print(f"{'N':>10} {'Dentro':>10} {'Pi estimado':>15} {'Error absoluto':>15} {'Mediana (s)':>15}")
        for medicion in mediciones:
            resultado = medicion.resultado
            print(f"{resultado.puntos:10d} {resultado.dentro:10d} {resultado.estimacion:15.9f} "
                  f"{resultado.error_absoluto:15.9f} {medicion.mediana:15.6f}")
        print(f"Archivos: {salida.resolve()}")
