"""Audita cada estado de la secuencia y cada medición antes de consolidar la entrega."""

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import median
import struct

import numpy as np
import pandas as pd

from ape07.modelo import Parametros, validar_tamanos


def exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(mensaje)


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def auditar(carpeta: Path, lenguaje: str) -> tuple[dict, bytes, list[dict]]:
    entorno = json.loads((carpeta / "entorno.json").read_text(encoding="utf-8"))
    parametros = entorno["parametros"]
    configuracion = Parametros(parametros["semilla"])
    exigir(parametros == {"semilla": configuracion.semilla, "a": 16807, "c": 0, "m": 2147483647},
           "Parámetros incompatibles con el experimento documentado.")
    tamanos = tuple(entorno["tamanos"])
    validar_tamanos(tamanos)
    repeticiones = entorno["repeticiones"]
    exigir(type(repeticiones) is int and 1 <= repeticiones <= 30, "Repeticiones inválidas.")
    exigir(entorno["lenguaje"] == lenguaje and entorno["calentamientos"] == 3
           and entorno["incluye_io_en_tiempo"] is False, "Metadatos del entorno incorrectos.")
    exigir(entorno["formato_secuencia"] == "uint32-be"
           and entorno["geometria"] == "cuadrado [-1,1)²; circulo x²+y²<=1", "Formato o geometría incorrectos.")
    secuencia = (carpeta / "secuencia.bin").read_bytes()
    cantidad = 2 * max(tamanos)
    exigir(len(secuencia) == 4 * cantidad and entorno["valores_lcg"] == cantidad,
           "Longitud de secuencia incorrecta: deben existir 2N estados de cuatro bytes.")
    exigir(hashlib.sha256(secuencia).hexdigest() == entorno["sha256_secuencia"], "SHA-256 de secuencia incorrecto.")
    anterior = configuracion.semilla
    for posicion, (estado,) in enumerate(struct.iter_unpack(">I", secuencia), 1):
        esperado = 16807 * anterior % 2147483647
        exigir(estado == esperado, f"Recurrencia incorrecta en el estado {posicion}.")
        anterior = estado
    estados = np.frombuffer(secuencia, dtype=">u4")
    puntos = 2.0 * (estados.astype(np.float64) / 2147483647) - 1.0
    coordenadas = puntos.reshape(-1, 2)
    interiores = np.sum(coordenadas * coordenadas, axis=1) <= 1.0
    acumulados = np.cumsum(interiores)
    resumen = leer_csv(carpeta / "resumen.csv")
    tiempos = leer_csv(carpeta / "tiempos.csv")
    exigir([int(fila["n"]) for fila in resumen] == list(tamanos), "Faltan tamaños o hay filas duplicadas.")
    exigir(len(tiempos) == len(tamanos) * repeticiones, "Cantidad de tiempos incorrecta.")
    for fila in resumen:
        cantidad_puntos = int(fila["n"])
        dentro = int(acumulados[cantidad_puntos - 1])
        estimado = 4.0 * dentro / cantidad_puntos
        exigir(int(fila["dentro"]) == dentro and float(fila["pi_estimado"]) == estimado
               and float(fila["error_absoluto"]) == abs(estimado - math.pi),
               f"Conteo, estimación o error incorrectos para N={cantidad_puntos}.")
        individuales = [muestra for muestra in tiempos if int(muestra["n"]) == cantidad_puntos]
        exigir([int(muestra["repeticion"]) for muestra in individuales] == list(range(1, repeticiones + 1)),
               "Repeticiones ausentes o duplicadas.")
        segundos = [float(muestra["segundos"]) for muestra in individuales]
        exigir(all(math.isfinite(valor) and valor > 0 for valor in segundos), "Tiempo no finito o no positivo.")
        exigir(int(fila["repeticiones"]) == repeticiones
               and float(fila["tiempo_mediana_s"]) == median(segundos)
               and float(fila["tiempo_minimo_s"]) == min(segundos), "Mediana o mínimo incoherentes.")
    primeros = leer_csv(carpeta / "primeros20.csv")
    exigir(len(primeros) == min(20, max(tamanos)), "Tabla inicial incompleta.")
    for indice, fila in enumerate(primeros):
        exigir(int(fila["punto"]) == indice + 1
               and int(fila["estado_x"]) == int(estados[2 * indice])
               and int(fila["estado_y"]) == int(estados[2 * indice + 1])
               and float(fila["x"]) == coordenadas[indice, 0]
               and float(fila["y"]) == coordenadas[indice, 1]
               and int(fila["dentro"]) == int(interiores[indice]), "Tabla de primeros puntos incorrecta.")
    return entorno, secuencia, resumen


def comparar(python: Path, java: Path, salida: Path) -> pd.DataFrame:
    entorno_python, secuencia_python, resumen_python = auditar(python, "Python")
    entorno_java, secuencia_java, resumen_java = auditar(java, "Java")
    for campo in ("parametros", "tamanos", "repeticiones", "valores_lcg"):
        exigir(entorno_python[campo] == entorno_java[campo], f"Diferencias entre lenguajes: {campo}.")
    exigir(secuencia_python == secuencia_java, "Las secuencias de Python y Java difieren.")
    filas = []
    for fila_python, fila_java in zip(resumen_python, resumen_java):
        for campo in ("n", "dentro", "pi_estimado", "error_absoluto"):
            exigir(float(fila_python[campo]) == float(fila_java[campo]), f"Diferencia numérica: {campo}.")
        filas.append({"N": int(fila_python["n"]), "pi_estimado": float(fila_python["pi_estimado"]),
                      "error_absoluto": float(fila_python["error_absoluto"]),
                      "tiempo_python_s": float(fila_python["tiempo_mediana_s"]),
                      "tiempo_java_s": float(fila_java["tiempo_mediana_s"]),
                      "dentro": int(fila_python["dentro"]), "coinciden": True})
    salida.mkdir(parents=True, exist_ok=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(salida / "tabla_guia.csv", index=False)
    verificacion = {"correcto": True, "estados_comparados": len(secuencia_python) // 4,
                    "puntos_comparados": len(secuencia_python) // 8,
                    "sha256_secuencia": entorno_python["sha256_secuencia"],
                    "igualdad": "exacta en todos los estados, puntos, conteos y estimaciones",
                    "tamanos": entorno_python["tamanos"], "parametros": entorno_python["parametros"]}
    (salida / "verificacion.json").write_text(json.dumps(verificacion, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")
    return tabla
