"""Adaptador de archivos CSV y JSON; no contiene formulas estadisticas."""

from dataclasses import asdict
import csv
import json
from pathlib import Path
import platform
import statistics
import sys

import numpy as np

from ape06.modelo.datos import Analisis, Medicion, ParametrosLCG


def leer_parametros(ruta: Path, nombres: tuple[str, ...]) -> tuple[ParametrosLCG, ...]:
    parametros = {}
    with ruta.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            p = ParametrosLCG(fila["nombre"], *(int(fila[campo]) for campo in ("semilla", "a", "c", "m")),
                              fuente=fila.get("fuente", "Configuracion del usuario"))
            if p.nombre in parametros:
                raise ValueError(f"Generador duplicado en la configuracion: {p.nombre}")
            parametros[p.nombre] = p
    if not parametros:
        raise ValueError("La configuracion no contiene generadores.")
    if not nombres or len(set(nombres)) != len(nombres):
        raise ValueError("Selecciona generadores sin nombres vacios o duplicados.")
    desconocidos = set(nombres) - parametros.keys()
    if desconocidos:
        raise ValueError(f"Generadores desconocidos: {', '.join(sorted(desconocidos))}")
    return tuple(parametros[nombre] for nombre in nombres)


def escribir_json(ruta: Path, contenido: object) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def escribir_csv(ruta: Path, campos: list[str], filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


class RepositorioResultados:
    def __init__(self, directorio: Path) -> None:
        self.directorio = directorio
        directorio.mkdir(parents=True, exist_ok=True)

    def entorno(self, comando: str) -> None:
        escribir_json(self.directorio / f"entorno_{comando}.json", {
            "lenguaje": "Python", "version": sys.version, "sistema": platform.platform(),
            "comando": comando, "reloj": "perf_counter", "unidad_tiempo": "segundos",
        })

    def guardar_analisis(self, analisis: Analisis) -> Path:
        muestra = analisis.muestra
        directorio = self.directorio / muestra.parametros.nombre
        directorio.mkdir(parents=True, exist_ok=True)
        with (directorio / "secuencia.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("posicion", "estado", "valor"))
            escritor.writerows((i, int(x), float(u)) for i, (x, u) in enumerate(zip(muestra.estados, muestra.valores), 1))
        ordenados = np.sort(muestra.valores)
        n = len(ordenados)
        with (directorio / "ks_ordenados.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("i", "u_ordenado", "fn_derecha", "fn_izquierda", "d_mas", "d_menos"))
            escritor.writerows((i, float(u), i / n, (i - 1) / n, i / n - u, u - (i - 1) / n)
                                for i, u in enumerate(ordenados, 1))
        chi = next(p for p in analisis.pruebas if p.nombre == "chi_cuadrado")
        escribir_csv(directorio / "frecuencias.csv", list(asdict(chi.intervalos[0])),
                     [asdict(intervalo) for intervalo in chi.intervalos])
        escribir_json(directorio / "analisis.json", {
            "lenguaje": "Python", "parametros": asdict(muestra.parametros), "n": n,
            "resumen": {campo: getattr(analisis, campo) for campo in
                        ("minimo", "maximo", "media", "varianza", "distintos", "periodo_observado")},
            "pruebas": [dict(asdict(p), decision=p.decision) for p in analisis.pruebas],
        })
        return directorio

    def guardar_resumen(self, analisis: tuple[Analisis, ...]) -> None:
        filas = [dict(generador=a.muestra.parametros.nombre, n=len(a.muestra.valores), prueba=p.nombre,
                       estadistico=p.estadistico, valor_p=p.valor_p, critico=p.critico, alfa=p.alfa,
                       decision=p.decision, metodo=p.metodo) for a in analisis for p in a.pruebas]
        escribir_csv(self.directorio / "resumen.csv", list(filas[0]), filas)

    def guardar_mediciones(self, mediciones: tuple[Medicion, ...]) -> None:
        filas = [dict(generador=m.parametros.nombre, n=m.resultado.puntos, dentro=m.resultado.dentro,
                       pi_estimado=m.resultado.estimacion, error_absoluto=m.resultado.error_absoluto,
                       tiempo_mediana_s=statistics.median(m.segundos), tiempo_minimo_s=min(m.segundos),
                       repeticiones=len(m.segundos), valores_lcg=2*m.resultado.puntos) for m in mediciones]
        escribir_csv(self.directorio / "benchmark.csv", list(filas[0]), filas)
        tiempos = [dict(generador=m.parametros.nombre, n=m.resultado.puntos, repeticion=i, segundos=t)
                   for m in mediciones for i, t in enumerate(m.segundos, 1)]
        escribir_csv(self.directorio / "tiempos.csv", list(tiempos[0]), tiempos)
