"""Entrada decimal acotada y operaciones finitas sin redondeos silenciosos."""

import re
from decimal import Decimal, Inexact, Rounded, localcontext

EntradaDecimal = str | int | Decimal
MAX_LONGITUD = 256
MAX_DIGITOS = 120
MAX_EXPONENTE = 120
_NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE][+-]?[0-9]+)?")


def convertir_decimal(valor: EntradaDecimal) -> Decimal:
    """Admite punto o coma decimal, nunca agrupadores ni conversiones por float."""
    if isinstance(valor, bool) or not isinstance(valor, (str, int, Decimal)):
        raise ValueError("Use texto, enteros o Decimal; no se admiten float.")
    texto = str(valor)
    if len(texto) > MAX_LONGITUD:
        raise ValueError(f"La entrada admite hasta {MAX_LONGITUD} caracteres.")
    texto = texto.strip()
    if not _NUMERO.fullmatch(texto):
        raise ValueError("Ingrese un número finito con punto o coma decimal, sin separadores de miles.")
    partes = re.split("[eE]", texto)
    if len(partes) == 2 and abs(int(partes[1])) > MAX_EXPONENTE:
        raise ValueError(f"El exponente escrito debe estar entre -{MAX_EXPONENTE} y {MAX_EXPONENTE}.")
    numero = Decimal(texto.replace(",", "."))
    tupla = numero.as_tuple()
    if len(tupla.digits) > MAX_DIGITOS or abs(tupla.exponent) > MAX_EXPONENTE:
        raise ValueError(f"Se admiten hasta {MAX_DIGITOS} dígitos de coeficiente y exponente decimal entre -{MAX_EXPONENTE} y {MAX_EXPONENTE}.")
    return numero


def decimal_finito(valor: EntradaDecimal) -> Decimal:
    """Los resultados internos pueden tener más dígitos que una entrada."""
    if isinstance(valor, Decimal):
        if not valor.is_finite():
            raise ValueError("El número debe ser finito.")
        return valor
    return convertir_decimal(valor)


def sumar(*valores: Decimal) -> Decimal:
    """Alinea los coeficientes y reserva los dígitos del posible acarreo."""
    if not valores:
        return Decimal("0")
    exponente_minimo = min(v.as_tuple().exponent for v in valores)
    posicion_maxima = max(v.adjusted() for v in valores)
    # M-E+1 posiciones alineadas y len(str(n)) para el acarreo de n términos.
    precision = max(1, posicion_maxima - exponente_minimo + 1) + len(str(len(valores)))
    with localcontext() as contexto:
        contexto.prec = precision
        contexto.traps[Inexact] = True
        contexto.traps[Rounded] = True
        resultado = valores[0]
        for valor in valores[1:]:
            resultado = resultado + valor
        return resultado


def multiplicar(*valores: Decimal) -> Decimal:
    """El producto necesita a lo sumo la suma de dígitos de sus coeficientes."""
    with localcontext() as contexto:
        contexto.prec = max(1, sum(len(v.as_tuple().digits) for v in valores))
        contexto.traps[Inexact] = True
        contexto.traps[Rounded] = True
        resultado = Decimal("1")
        for valor in valores:
            resultado = resultado * valor
        return resultado
