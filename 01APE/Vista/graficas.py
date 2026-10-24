"""Gráficas de los resultados de ambos modelos."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from Modelo.modelo import ResultadoLluvia


def generar_graficas(original: list[ResultadoLluvia], ajustado: list[ResultadoLluvia]) -> list[Path]:
    carpeta_salida = Path(__file__).resolve().parent.parent / "graficas_generadas"
    carpeta_salida.mkdir(exist_ok=True)
    horas = [fila.registro.hora for fila in original]
    t = np.arange(len(horas))

    # Conserva la estructura de trazado proporcionada por el docente.
    plt.figure(figsize=(10, 5))
    plt.plot(t, [float(f.humedad_normalizada) for f in original], marker="o", label="Humedad (H)")
    plt.plot(t, [float(f.nubosidad_normalizada) for f in original], marker="o", label="Nubosidad (N)")
    plt.plot(t, [float(f.factor_temperatura) for f in original], marker="o", label="Factor temperatura (Tf)")
    plt.xticks(t, horas)
    plt.xlabel("Hora")
    plt.ylabel("Valor normalizado")
    plt.title("Variables del modelo de lluvia")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    ruta_variables = carpeta_salida / "variables_modelo.png"
    plt.savefig(ruta_variables, dpi=150, bbox_inches="tight")

    plt.figure(figsize=(10, 5))
    plt.plot(t, [float(f.indice) for f in original], marker="o", label="Modelo original")
    plt.plot(t, [float(f.indice) for f in ajustado], marker="o", label="Modelo ajustado")
    plt.axhline(y=0.40, linestyle="--", color="gray", label="Baja posibilidad (0.40)")
    plt.axhline(y=0.60, linestyle="--", color="orange", label="Lluvia probable (0.60)")
    plt.axhline(y=0.75, linestyle="--", color="red", label="Lluvia (0.75)")
    plt.xticks(t, horas)
    plt.xlabel("Hora")
    plt.ylabel("Índice de lluvia")
    plt.title("Comparación de los modelos de lluvia")
    plt.ylim(0, 1)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    ruta_comparacion = carpeta_salida / "comparacion_modelos.png"
    plt.savefig(ruta_comparacion, dpi=150, bbox_inches="tight")

    # Agg genera imágenes, pero no puede abrir ventanas interactivas.
    if "agg" not in plt.get_backend().lower():
        plt.show()
    plt.close("all")
    return [ruta_variables, ruta_comparacion]
