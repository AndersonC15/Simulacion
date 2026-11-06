"""Graficas exportables: frecuencias, FDE completa y pares consecutivos."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ape06.modelo.datos import Analisis


class VistaGraficas:
    def guardar(self, analisis: Analisis, directorio: Path) -> None:
        valores = analisis.muestra.valores
        nombre = analisis.muestra.parametros.nombre
        chi, ks = analisis.pruebas[:2]
        plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

        figura, eje = plt.subplots(figsize=(9, 5), layout="constrained")
        eje.bar(np.arange(10) / 10 + 0.05, [b.observada for b in chi.intervalos],
                width=0.085, color="#24768a", label="Observada")
        eje.axhline(len(valores) / 10, color="#c45d35", linestyle="--", label="Esperada N/10")
        eje.set(xlim=(0, 1), xlabel="Intervalo de U", ylabel="Frecuencia",
                title=f"{nombre.upper()} · Chi-cuadrado: {chi.estadistico:.4f}, p={chi.valor_p:.6g}")
        eje.legend()
        figura.savefig(directorio / "histograma.png", dpi=150)
        plt.close(figura)

        ordenados = np.sort(valores)
        n = len(valores)
        figura, eje = plt.subplots(figsize=(7, 6), layout="constrained")
        eje.step(np.r_[0, ordenados, 1], np.r_[0, np.arange(1, n + 1) / n, 1],
                 where="post", color="#24768a", label="FDE empirica (todos los datos)")
        eje.plot([0, 1], [0, 1], "--", color="#c45d35", label="Uniforme: F(u)=u")
        mas = np.arange(1, n + 1) / n - ordenados
        menos = ordenados - np.arange(n) / n
        i = int(np.argmax(mas if ks.detalles["d_mas"] >= ks.detalles["d_menos"] else menos))
        inferior, superior = (ordenados[i], (i + 1) / n) if ks.detalles["d_mas"] >= ks.detalles["d_menos"] else (i / n, ordenados[i])
        eje.vlines(ordenados[i], inferior, superior, color="#c52e45", linewidth=3, label="Distancia D")
        eje.set(xlim=(0, 1), ylim=(0, 1), xlabel="u", ylabel="Probabilidad acumulada",
                title=f"{nombre.upper()} · KS: D={ks.estadistico:.6f}, p≈{ks.valor_p:.6g}")
        eje.legend(loc="upper left")
        figura.savefig(directorio / "acumulada.png", dpi=150)
        plt.close(figura)

        figura, eje = plt.subplots(figsize=(6, 6), layout="constrained")
        limite = min(4000, n - 1)
        eje.scatter(valores[:limite], valores[1:limite + 1], s=5, alpha=0.5, color="#24768a")
        eje.set(xlim=(0, 1), ylim=(0, 1), xlabel="U(n)", ylabel="U(n+1)",
                title=f"{nombre.upper()} · {limite} pares consecutivos\nInspeccion visual; no es una prueba formal")
        figura.savefig(directorio / "pares.png", dpi=150)
        plt.close(figura)
