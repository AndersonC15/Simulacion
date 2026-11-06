"""Experimento reproducible de dispersión; varias semillas por cada sigma."""
from dataclasses import dataclass, replace
from decimal import Decimal, localcontext
from fractions import Fraction

from Modelo.estrategias import Estocastico
from Modelo.numeros import ErrorValidacion, decimal_desde_entrada, multiplicar


@dataclass(frozen=True)
class ResumenRuido:
    sigma: Decimal
    semillas: tuple[int, ...]
    finales: tuple[Decimal, ...]
    media: Decimal
    desviacion: Decimal


def analizar_ruido(parametros, replicas=30):
    if isinstance(replicas, bool) or not isinstance(replicas, int) or not 2 <= replicas <= 100:
        raise ErrorValidacion("El análisis admite entre 2 y 100 realizaciones por sigma.")
    if parametros.horizonte > 100:
        raise ErrorValidacion("El análisis de ruido se limita a 100 períodos para acotar el trabajo total.")
    base = parametros.sigma if parametros.sigma > 0 else Decimal(1)
    sigmas = (Decimal(0), base, multiplicar(Decimal(2), base))
    semillas = tuple((parametros.semilla + i) % (2**64) for i in range(replicas))
    resumenes = []
    for sigma in sigmas:
        sigma = decimal_desde_entrada(sigma)
        finales = tuple(Estocastico().simular(replace(parametros, sigma=sigma, semilla=semilla)).poblaciones[-1]
                        for semilla in semillas)
        media_racional = sum(map(Fraction, finales), Fraction(0)) / replicas
        varianza_racional = sum(((Fraction(valor) - media_racional) ** 2 for valor in finales), Fraction(0)) / replicas
        with localcontext() as contexto:
            contexto.prec = parametros.precision + 20
            media = Decimal(media_racional.numerator) / Decimal(media_racional.denominator)
            varianza = Decimal(varianza_racional.numerator) / Decimal(varianza_racional.denominator)
            contexto.prec = parametros.precision
            desviacion = varianza.sqrt()
            media = +media
        resumenes.append(ResumenRuido(sigma, semillas, finales, media, desviacion))
    return tuple(resumenes)
