"""Salida de consola, CSV, JSON y PNG; las gráficas funcionan sin escritorio."""

import csv
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from statistics import fmean, pvariance

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from lcg_practica.modelo import ResultadoExperimento


class VistaArchivosConsola:
    def presentar(self, resultado: ResultadoExperimento, destino: Path) -> None:
        destino.mkdir(parents=True, exist_ok=True)
        base = destino / f"semilla_{resultado.parametros.semilla}"
        valores = resultado.normalizados
        with base.with_suffix(".csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("n", "x", "u"))
            for n, (estado, valor) in enumerate(zip(resultado.estados, valores), start=1):
                escritor.writerow((n, estado, format(valor, ".17g")))
        resumen = {
            "lenguaje": "Python",
            "parametros": asdict(resultado.parametros),
            "cantidad": len(valores),
            "periodo": asdict(resultado.periodo),
            "estadisticas_descriptivas": {
                "minimo": min(valores),
                "maximo": max(valores),
                "media": fmean(valores),
                "varianza_poblacional": pvariance(valores),
            },
        }
        base.with_suffix(".json").write_text(
            json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        self._graficar(resultado, base.with_suffix(".png"))
        print(f"\nPython | semilla={resultado.parametros.semilla} | n={len(valores)}")
        print(f"{'n':>4} {'Xn':>12} {'Un (decimal exacto)':>34}")
        for n, (estado, valor) in enumerate(zip(resultado.estados[:20], valores[:20]), 1):
            print(f"{n:4d} {estado:12d} {Decimal.from_float(valor):34f}")
        print(f"Período teórico (Hull–Dobell): {resultado.periodo.periodo_teorico}")
        print(f"Período observado: {resultado.periodo.periodo_observado or 'no detectado en la muestra'}")
        print(f"Archivos: {base}.csv / .json / .png")

    @staticmethod
    def _graficar(resultado: ResultadoExperimento, destino: Path) -> None:
        valores = resultado.normalizados
        figura, ejes = plt.subplots(3, 1, figsize=(12, 12), constrained_layout=True)
        figura.suptitle(f"LCG — Python — semilla {resultado.parametros.semilla}")
        ejes[0].scatter(range(1, len(valores) + 1), valores, s=2, alpha=0.45)
        ejes[0].set(title=f"Secuencia completa: {len(valores):,} valores", xlabel="n", ylabel="Un")
        limite = min(200, len(valores))
        ejes[1].plot(range(1, limite + 1), valores[:limite], linewidth=0.7, marker=".", markersize=3)
        ejes[1].set(title=f"Detalle de las primeras {limite} observaciones", xlabel="n", ylabel="Un")
        ejes[2].scatter(valores[:-1], valores[1:], s=2, alpha=0.45)
        ejes[2].set(title="Pares consecutivos: inspección visual, no prueba estadística", xlabel="Un", ylabel="Un+1", xlim=(0, 1))
        for eje in ejes:
            eje.set_ylim(0, 1)
            eje.grid(alpha=0.2)
        figura.savefig(destino, dpi=140)
        plt.close(figura)

