"""Strategy: cada prueba implementa el mismo contrato y conserva el orden original."""

from abc import ABC, abstractmethod
import math

import numpy as np
from numpy.typing import NDArray
from scipy.stats import chi2, kstwobign, norm

from .datos import Intervalo, ResultadoPrueba


def validar(valores: NDArray[np.float64], alfa: float) -> None:
    if valores.ndim != 1 or len(valores) == 0:
        raise ValueError("Se necesita una secuencia unidimensional no vacia.")
    if not np.all(np.isfinite(valores)) or np.any((valores < 0) | (valores >= 1)):
        raise ValueError("Todos los datos deben ser finitos y pertenecer a [0, 1).")
    if not math.isfinite(alfa) or not 0 < alfa < 1:
        raise ValueError("El nivel de significancia debe estar entre 0 y 1.")


class PruebaEstadistica(ABC):
    @abstractmethod
    def evaluar(self, valores: NDArray[np.float64], alfa: float) -> ResultadoPrueba:
        """Evalua los datos sin modificarlos."""


class ChiCuadrado(PruebaEstadistica):
    INTERVALOS = 10

    def evaluar(self, valores: NDArray[np.float64], alfa: float) -> ResultadoPrueba:
        validar(valores, alfa)
        esperada = len(valores) / self.INTERVALOS
        if esperada < 5:
            raise ValueError("Chi-cuadrado requiere N >= 50: Ei >= 5 en los 10 intervalos.")
        limites = np.arange(self.INTERVALOS + 1, dtype=float) / self.INTERVALOS
        frecuencias, _ = np.histogram(valores, bins=limites)
        intervalos = tuple(
            Intervalo(i / 10, (i + 1) / 10, int(o), esperada, (int(o) - esperada) ** 2 / esperada)
            for i, o in enumerate(frecuencias)
        )
        estadistico = sum(intervalo.aporte for intervalo in intervalos)
        return ResultadoPrueba(
            "chi_cuadrado", "Uniformidad U(0,1)", estadistico,
            float(chi2.sf(estadistico, 9)), float(chi2.isf(alfa, 9)), alfa,
            "Chi-cuadrado con 9 gl; cola superior", {"gl": 9.0}, intervalos,
        )


class KolmogorovSmirnov(PruebaEstadistica):
    def evaluar(self, valores: NDArray[np.float64], alfa: float) -> ResultadoPrueba:
        validar(valores, alfa)
        ordenados = np.sort(valores)
        n = len(ordenados)
        posiciones = np.arange(1, n + 1, dtype=float)
        d_mas = float(np.max(posiciones / n - ordenados))
        d_menos = float(np.max(ordenados - (posiciones - 1) / n))
        d = max(d_mas, d_menos)
        return ResultadoPrueba(
            "ks", "Uniformidad U(0,1)", d,
            float(kstwobign.sf(math.sqrt(n) * d)), float(kstwobign.isf(alfa) / math.sqrt(n)),
            alfa, "KS bilateral, distribucion limite de Kolmogorov (asintotico)",
            {"d_mas": d_mas, "d_menos": d_menos, "critico_005_diapositiva": 1.36 / math.sqrt(n)},
            nota="El valor p es aproximado. Las diapositivas recomiendan N >= 35.",
        )


class Rachas(PruebaEstadistica):
    def evaluar(self, valores: NDArray[np.float64], alfa: float) -> ResultadoPrueba:
        validar(valores, alfa)
        mediana = float(np.median(valores))
        # Convencion explicita: se eliminan los empates con la mediana.
        signos = valores[valores != mediana] > mediana
        n1 = int(np.count_nonzero(signos))
        n2 = len(signos) - n1
        r = 0 if len(signos) == 0 else 1 + int(np.count_nonzero(signos[1:] != signos[:-1]))
        detalles = {"mediana": mediana, "n1": float(n1), "n2": float(n2), "rachas": float(r),
                    "empates": float(len(valores) - len(signos))}
        metodo = "Rachas sobre/bajo mediana; normal bilateral sin correccion de continuidad"
        if n1 <= 10 or n2 <= 10:
            return ResultadoPrueba(
                "rachas", "Orden aleatorio de signos respecto a la mediana", None, None, None,
                alfa, metodo, detalles, nota="No se usa la aproximacion normal: n1 y n2 deben ser > 10.",
            )
        total = n1 + n2
        media = 2.0 * n1 * n2 / total + 1
        varianza = 2.0 * n1 * n2 * (2.0 * n1 * n2 - total) / (total**2 * (total - 1))
        z = (r - media) / math.sqrt(varianza)
        detalles.update(media_rachas=media, varianza_rachas=varianza)
        return ResultadoPrueba(
            "rachas", "Orden aleatorio de signos respecto a la mediana", z,
            float(2 * norm.sf(abs(z))), float(norm.isf(alfa / 2)), alfa, metodo, detalles,
        )
