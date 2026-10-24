"""Dibujo y almacenamiento; float se usa únicamente al trazar las curvas."""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends import backend_registry
from matplotlib.figure import Figure

from Modelo.modelo import ResultadoLluvia, UMBRALES


def backend_interactivo(nombre: str) -> bool:
    """Consulta el framework real: Agg es estático; TkAgg y QtAgg son GUI."""
    _, framework = backend_registry.resolve_backend(nombre)
    return framework is not None


@dataclass(frozen=True)
class EntregaGraficas:
    rutas: tuple[Path, Path]
    mensaje: str


class VistaGraficas:
    def __init__(self, carpeta: Path | None = None) -> None:
        self.carpeta = carpeta if carpeta is not None else (
            Path(__file__).resolve().parent.parent / "graficas_generadas"
        )

    def generar(self, original: list[ResultadoLluvia],
                ajustado: list[ResultadoLluvia]) -> EntregaGraficas:
        figuras: list[Figure] = []
        aviso = ""
        try:
            self.carpeta.mkdir(parents=True, exist_ok=True)
            try:
                variables, eje_variables = plt.subplots(figsize=(11, 5.5))
            except (ImportError, RuntimeError) as error:
                # Por ejemplo, Tk/Qt forzado en una sesión sin escritorio o sin toolkit.
                plt.switch_backend("Agg")
                aviso = f"No se pudo iniciar el backend gráfico ({error}). "
                variables, eje_variables = plt.subplots(figsize=(11, 5.5))
            figuras.append(variables)
            self._dibujar_variables(eje_variables, original)
            comparacion, eje_comparacion = plt.subplots(figsize=(11, 5.5))
            figuras.append(comparacion)
            self._dibujar_comparacion(eje_comparacion, original, ajustado)
            rutas = (self.carpeta / "variables_modelo.png", self.carpeta / "comparacion_modelos.png")
            for figura, ruta in zip(figuras, rutas):
                figura.tight_layout()
                figura.savefig(ruta, dpi=150, bbox_inches="tight")
            if backend_interactivo(plt.get_backend()):
                try:
                    plt.show(block=True)
                    mensaje = "Visualización interactiva finalizada. Los PNG también están guardados."
                except (ImportError, RuntimeError, OSError) as error:
                    mensaje = f"Los PNG están guardados, pero no se pudieron mostrar las ventanas: {error}"
            else:
                mensaje = aviso + f"Backend {plt.get_backend()} sin ventanas. Consulte los archivos PNG guardados."
            return EntregaGraficas(rutas, mensaje)
        finally:
            for figura in figuras:
                plt.close(figura)

    @staticmethod
    def _configurar_ejes(eje: Axes, resultados: list[ResultadoLluvia],
                         titulo: str, etiqueta_y: str) -> None:
        posiciones = range(len(resultados))
        eje.set_xticks(posiciones, [r.registro.hora for r in resultados])
        eje.set_xlabel("Hora")
        eje.set_ylabel(etiqueta_y)
        eje.set_title(titulo)
        eje.set_ylim(0, 1)
        eje.grid(True, alpha=0.35)
        eje.legend(loc="best")

    def _dibujar_variables(self, eje: Axes, resultados: list[ResultadoLluvia]) -> None:
        posiciones = range(len(resultados))
        for atributo, etiqueta in (
            ("humedad_normalizada", "Humedad (H)"),
            ("nubosidad_normalizada", "Nubosidad (N)"),
            ("factor_temperatura", "Factor temperatura (Tf)"),
        ):
            eje.plot(posiciones, [float(getattr(r, atributo)) for r in resultados],
                     marker="o", label=etiqueta)
        self._configurar_ejes(eje, resultados, "Variables del modelo de lluvia", "Valor normalizado")

    def _dibujar_comparacion(self, eje: Axes, original: list[ResultadoLluvia],
                             ajustado: list[ResultadoLluvia]) -> None:
        posiciones = range(len(original))
        for resultados, nombre in ((original, "Modelo original"), (ajustado, "Modelo ajustado")):
            eje.plot(posiciones, [float(r.indice) for r in resultados], marker="o", label=nombre)
        for umbral, nombre, color in zip(UMBRALES,
                                        ("Baja posibilidad", "Lluvia probable", "Lluvia"),
                                        ("gray", "orange", "red")):
            eje.axhline(float(umbral), linestyle="--", color=color, label=f"{nombre} ({umbral})")
        self._configurar_ejes(eje, original, "Comparación de los modelos de lluvia", "Índice de lluvia")
