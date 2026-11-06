"""Audita los archivos de dos ejecuciones independientes antes de crear el informe."""

import csv
from itertools import zip_longest
import json
import math
from pathlib import Path

import pandas as pd

from .archivos import escribir_csv, escribir_json


def comprobar(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(mensaje)


def comparar_numero(a: float | None, b: float | None, contexto: str, tolerancia: float = 1e-10) -> None:
    if a is None or b is None:
        comprobar(a is None and b is None, f"Diferencia en {contexto}: {a} != {b}")
    else:
        comprobar(math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=1e-10, abs_tol=tolerancia),
                  f"Diferencia en {contexto}: {a} != {b}")


def comparar_secuencia(ruta_python: Path, ruta_java: Path, salida: Path, parametros: dict, n: int) -> int:
    salida.parent.mkdir(parents=True, exist_ok=True)
    with ruta_python.open(encoding="utf-8", newline="") as archivo_p, \
         ruta_java.open(encoding="utf-8", newline="") as archivo_j, \
         salida.open("w", encoding="utf-8", newline="") as archivo_s:
        escritor = csv.writer(archivo_s)
        escritor.writerow(("posicion", "estado_python", "estado_java", "u_python", "u_java", "diferencia", "coincide"))
        cantidad = 0
        estado_anterior = parametros["semilla"]
        for i, (p, j) in enumerate(zip_longest(csv.DictReader(archivo_p), csv.DictReader(archivo_j)), 1):
            comprobar(p is not None and j is not None, "Las secuencias tienen longitudes diferentes.")
            xp, xj = int(p["estado"]), int(j["estado"])
            up, uj = float(p["valor"]), float(j["valor"])
            esperado = (parametros["a"] * estado_anterior + parametros["c"]) % parametros["m"]
            comprobar(int(p["posicion"]) == int(j["posicion"]) == i, f"Posicion incorrecta: {i}")
            comprobar(xp == xj == esperado, f"Estado diferente o recurrencia incorrecta en posicion {i}")
            comprobar(up == uj == xp / parametros["m"] and 0 <= up < 1, f"Normalizacion incorrecta en posicion {i}")
            escritor.writerow((i, xp, xj, up, uj, up - uj, True))
            estado_anterior = xp
            cantidad = i
        comprobar(cantidad == n, f"Se esperaban {n} valores, se encontraron {cantidad}.")
    return cantidad


def comparar_analisis(python: Path, java: Path, salida: Path) -> list[dict]:
    nombres_p = {p.parent.name for p in python.glob("*/analisis.json")}
    nombres_j = {p.parent.name for p in java.glob("*/analisis.json")}
    comprobar(bool(nombres_p) and nombres_p == nombres_j, "Faltan analisis o los conjuntos de generadores son diferentes.")
    resultados = []
    for nombre in sorted(nombres_p):
        p = json.loads((python / nombre / "analisis.json").read_text(encoding="utf-8"))
        j = json.loads((java / nombre / "analisis.json").read_text(encoding="utf-8"))
        comprobar(p["parametros"] == j["parametros"] and p["n"] == j["n"], f"Parametros diferentes: {nombre}")
        comprobar(p["lenguaje"] == "Python" and j["lenguaje"] == "Java", "Identificacion de lenguajes incorrecta.")
        comparar_secuencia(python / nombre / "secuencia.csv", java / nombre / "secuencia.csv",
                           salida / f"secuencia_{nombre}.csv", p["parametros"], p["n"])
        for campo, valor in p["resumen"].items():
            comparar_numero(valor, j["resumen"][campo], f"{nombre}/{campo}")
        pruebas_p = {r["nombre"]: r for r in p["pruebas"]}
        pruebas_j = {r["nombre"]: r for r in j["pruebas"]}
        comprobar(set(pruebas_p) == set(pruebas_j) == {"chi_cuadrado", "ks", "rachas"}, f"Faltan pruebas en {nombre}")
        for prueba, rp in pruebas_p.items():
            rj = pruebas_j[prueba]
            for campo in ("estadistico", "valor_p", "alfa"):
                comparar_numero(rp[campo], rj[campo], f"{nombre}/{prueba}/{campo}")
            comparar_numero(rp["critico"], rj["critico"], f"{nombre}/{prueba}/critico", 1e-8)
            comprobar(rp["decision"] == rj["decision"] and rp["metodo"] == rj["metodo"], f"Decisiones o metodos diferentes en {nombre}/{prueba}")
            comprobar(rp["detalles"].keys() == rj["detalles"].keys(), "Detalles incompletos")
            for campo, valor in rp["detalles"].items():
                comparar_numero(valor, rj["detalles"][campo], f"{nombre}/{prueba}/{campo}")
            if prueba == "chi_cuadrado":
                comprobar(len(rp["intervalos"]) == len(rj["intervalos"]) == 10, "Se requieren diez intervalos")
                comprobar(sum(b["observada"] for b in rp["intervalos"]) == p["n"], "Se perdieron datos en las frecuencias")
                for bp, bj in zip(rp["intervalos"], rj["intervalos"]):
                    for campo in bp:
                        comparar_numero(bp[campo], bj[campo], f"{nombre}/intervalo/{campo}")
        resultados.append(p)
    return resultados


def comparar_benchmark(python: Path, java: Path, salida: Path) -> list[dict]:
    p = pd.read_csv(python / "benchmark.csv", float_precision="round_trip")
    j = pd.read_csv(java / "benchmark.csv", float_precision="round_trip")
    claves = ["generador", "n"]
    comprobar(not p.duplicated(claves).any() and not j.duplicated(claves).any(), "Hay filas de rendimiento duplicadas")
    combinado = p.merge(j, on=claves, suffixes=("_python", "_java"), how="outer", indicator=True, validate="one_to_one")
    comprobar(not combinado.empty and combinado["_merge"].eq("both").all(), "Faltan mediciones en alguno de los lenguajes")
    filas = []
    for _, fila in combinado.iterrows():
        contexto = f"{fila['generador']}/N={fila['n']}"
        for campo in ("dentro", "pi_estimado", "error_absoluto", "valores_lcg", "repeticiones"):
            comprobar(fila[campo + "_python"] == fila[campo + "_java"], f"Diferencia en {contexto}/{campo}")
        comprobar(fila["valores_lcg_python"] == 2*fila["n"], f"Deben generarse 2N valores para {contexto}")
        comparar_numero(fila["pi_estimado_python"], 4*fila["dentro_python"]/fila["n"], contexto)
        comparar_numero(fila["error_absoluto_python"], abs(fila["pi_estimado_python"]-math.pi), contexto)
        for lenguaje in ("python", "java"):
            comprobar(math.isfinite(fila[f"tiempo_mediana_s_{lenguaje}"]) and fila[f"tiempo_mediana_s_{lenguaje}"] > 0,
                      f"Tiempo invalido en {contexto}/{lenguaje}")
        filas.append(dict(generador=fila["generador"], n=int(fila["n"]), pi_estimado=fila["pi_estimado_python"],
                          error_absoluto=fila["error_absoluto_python"], tiempo_python_s=fila["tiempo_mediana_s_python"],
                          tiempo_java_s=fila["tiempo_mediana_s_java"], dentro=int(fila["dentro_python"]), coincide=True))
    escribir_csv(salida / "tabla_guia.csv", list(filas[0]), filas)
    return filas


def comparar_todo(python: Path, java: Path, salida: Path) -> tuple[list[dict], list[dict]]:
    analisis = comparar_analisis(python, java, salida)
    benchmark = comparar_benchmark(python, java, salida)
    comprobar({a["parametros"]["nombre"] for a in analisis} == {b["generador"] for b in benchmark},
              "Los generadores de analisis y rendimiento no coinciden")
    escribir_json(salida / "verificacion.json", {
        "correcto": True, "secuencias": [{"generador": a["parametros"]["nombre"], "valores": a["n"],
                                         "estados_iguales": True, "valores_iguales": True} for a in analisis],
        "comparaciones_pi": len(benchmark), "tolerancia_estadistica_absoluta": 1e-10,
        "tolerancia_criticos_absoluta": 1e-8, "tolerancia_relativa": 1e-10,
    })
    return analisis, benchmark
