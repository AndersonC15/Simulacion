"""Mallas por índice entero y cociente racional, sin sumas acumulativas."""
from decimal import Decimal
from fractions import Fraction

from Modelo.numeros import MAX_PUNTOS, ErrorValidacion, multiplicar


def malla(parametros, periodica=False):
    horizonte = parametros.horizonte
    paso = Decimal(1) if periodica else parametros.dt
    if periodica and horizonte != horizonte.to_integral_value():
        raise ErrorValidacion("Discreto y estocástico requieren un horizonte entero de períodos.")
    cociente = Fraction(horizonte) / Fraction(paso)
    pasos = (cociente.numerator + cociente.denominator - 1) // cociente.denominator
    if pasos + 1 > MAX_PUNTOS:
        raise ErrorValidacion("La malla supera 10001 puntos; aumente dt o reduzca el horizonte.")
    return tuple(multiplicar(Decimal(i), paso) for i in range(pasos)) + (horizonte,)
