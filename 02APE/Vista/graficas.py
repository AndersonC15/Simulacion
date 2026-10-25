"""Conversión a float exclusivamente al dibujar; CSV conserva Decimal."""
import csv
import os
from pathlib import Path
import sys
import tempfile

from Modelo.numeros import ErrorValidacion


class VistaGraficas:
    def guardar(self, experimento, directorio=None, *, mostrar=False, nombre="comparacion"):
        import matplotlib
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.registry import backend_registry

        if nombre not in ("comparacion", "crecimiento", "decrecimiento", "constante"):
            raise ValueError("Nombre de salida no admitido.")
        carpeta = Path(directorio) if directorio is not None else Path(__file__).resolve().parents[1] / "resultados"
        carpeta.mkdir(parents=True, exist_ok=True)
        png = carpeta / f"{nombre}.png"
        csv_salida = carpeta / f"{nombre}.csv"
        figura, eje = plt.subplots(figsize=(10, 6))
        try:
            for serie in experimento.series:
                tiempos = [float(t) for t in serie.tiempos]
                poblaciones = [float(p) for p in serie.poblaciones]
                if any(b <= a for a, b in zip(tiempos, tiempos[1:])):
                    raise ErrorValidacion("La precisión gráfica fusionaría tiempos distintos; aumente el último paso.")
                if serie.nombre == "Discreto":
                    eje.step(tiempos, poblaciones, where="post", marker="s", label=serie.nombre)
                elif serie.nombre == "Estocástico":
                    eje.plot(tiempos, poblaciones, marker="o", linestyle="--", label=serie.nombre)
                else:
                    eje.plot(tiempos, poblaciones, label=serie.nombre)
            eje.scatter(range(len(experimento.observaciones)), [float(x) for x in experimento.observaciones],
                        color="black", marker="x", s=60, label="Observaciones de referencia", zorder=5)
            eje.set(title=f"Comparación de modelos poblacionales: {experimento.escenario}",
                    xlabel="Tiempo (períodos)", ylabel="Población")
            eje.grid(True, alpha=0.35)
            eje.legend()
            figura.tight_layout()
            # Reemplazo atómico: una ejecución repetida no usa la tabla/PNG como datos.
            with tempfile.NamedTemporaryFile(dir=carpeta, suffix=".png", delete=False) as archivo:
                temporal = Path(archivo.name)
            try:
                figura.savefig(temporal, dpi=150, metadata={"Software": "APE02"})
                temporal.replace(png)
            finally:
                temporal.unlink(missing_ok=True)
            self._guardar_csv(experimento, csv_salida)
            _, framework = backend_registry.resolve_backend(matplotlib.get_backend())
            if mostrar and framework is not None:
                plt.show()
            return png, csv_salida
        finally:
            plt.close(figura)

    @staticmethod
    def _guardar_csv(experimento, destino):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=destino.parent,
                                         suffix=".csv", delete=False) as archivo:
            temporal = Path(archivo.name)
            try:
                escritor = csv.writer(archivo)
                escritor.writerow(("modelo", "tiempo_periodos", "poblacion"))
                for serie in experimento.series:
                    escritor.writerows((serie.nombre, str(t), str(p)) for t, p in zip(serie.tiempos, serie.poblaciones))
                escritor.writerows(("Observación de referencia", str(t), str(p))
                                    for t, p in enumerate(experimento.observaciones))
            except OSError:
                temporal.unlink(missing_ok=True)
                raise
        try:
            temporal.replace(destino)
        finally:
            temporal.unlink(missing_ok=True)
