#!/usr/bin/env python3
"""Compara las implementaciones y genera tablas y gráficas desde los datos reales."""

from pathlib import Path
import math

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from ape07.comparacion import comparar, leer_csv


BASE = Path(__file__).resolve().parents[1]
SALIDA = BASE / "resultados/comparacion"


def generar() -> None:
    tabla = comparar(BASE / "resultados/python", BASE / "resultados/java", SALIDA)
    estados = np.fromfile(BASE / "resultados/python/secuencia.bin", dtype=">u4")
    puntos = (2.0 * (estados.astype(np.float64) / 2147483647) - 1.0).reshape(-1, 2)
    dentro = np.sum(puntos * puntos, axis=1) <= 1
    acumulados = np.cumsum(dentro)
    posiciones = np.unique(np.concatenate((np.arange(1000, len(puntos) + 1, 1000), tabla["N"].to_numpy())))
    posiciones = posiciones[posiciones <= len(puntos)]
    convergencia = pd.DataFrame({"N": posiciones, "pi_estimado": 4.0 * acumulados[posiciones - 1] / posiciones})
    convergencia["error_absoluto"] = abs(convergencia["pi_estimado"] - math.pi)
    convergencia.to_csv(SALIDA / "convergencia.csv", index=False)

    figura, ejes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    limite = min(5000, len(puntos))
    for estado, color, etiqueta in ((True, "#126d82", "Dentro"), (False, "#b74834", "Fuera")):
        seleccion = dentro[:limite] == estado
        ejes[0].scatter(puntos[:limite][seleccion, 0], puntos[:limite][seleccion, 1], s=3, color=color, label=etiqueta)
    angulos = np.linspace(0, 2 * math.pi, 500)
    ejes[0].plot(np.cos(angulos), np.sin(angulos), color="black", linewidth=1)
    ejes[0].set(xlim=(-1, 1), ylim=(-1, 1), aspect="equal", xlabel="x", ylabel="y",
                title=f"Primeros {limite:,} puntos; círculo inscrito")
    ejes[0].legend(loc="upper right", markerscale=3)
    ejes[1].plot(convergencia["N"], convergencia["pi_estimado"], linewidth=.8, label="Monte Carlo")
    ejes[1].axhline(math.pi, color="#b74834", linestyle="--", label="π de referencia")
    ejes[1].set(xlabel="N puntos", ylabel="π estimado", xscale="log", title="Evolución del estimador")
    ejes[1].legend()
    figura.savefig(SALIDA / "puntos_convergencia.png", dpi=170)
    plt.close(figura)

    figura, ejes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    ejes[0].loglog(tabla["N"], tabla["error_absoluto"], "o-", label="Error observado")
    referencia = tabla["error_absoluto"].iloc[0] * np.sqrt(tabla["N"].iloc[0] / tabla["N"])
    ejes[0].loglog(tabla["N"], referencia, "--", label="Forma 1/√N; referencia visual")
    ejes[0].set(xlabel="N puntos", ylabel="Error absoluto", title="Error en los cuatro tamaños de la guía")
    ejes[0].legend()
    for lenguaje in ("python", "java"):
        ejes[1].loglog(tabla["N"], tabla[f"tiempo_{lenguaje}_s"], "o-", label=lenguaje.capitalize())
    ejes[1].set(xlabel="N puntos", ylabel="Mediana en segundos", title="Generación + clasificación de puntos")
    ejes[1].legend()
    figura.savefig(SALIDA / "error_tiempos.png", dpi=170)
    plt.close(figura)
    primeros_python = leer_csv(BASE / "resultados/python/primeros20.csv")
    primeros_java = leer_csv(BASE / "resultados/java/primeros20.csv")
    comparados = []
    for fila_python, fila_java in zip(primeros_python, primeros_java):
        comparados.append({"punto": int(fila_python["punto"]), "x_python": float(fila_python["x"]),
                           "x_java": float(fila_java["x"]), "y_python": float(fila_python["y"]),
                           "y_java": float(fila_java["y"]), "dentro": int(fila_python["dentro"]),
                           "coinciden": True})
    pd.DataFrame(comparados).to_csv(SALIDA / "primeros20_comparados.csv", index=False)
    print(tabla.to_string(index=False))
    print(f"Secuencia completa verificada: {len(estados):,} estados, {len(puntos):,} puntos.")


if __name__ == "__main__":
    generar()
