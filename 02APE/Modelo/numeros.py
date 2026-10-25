"""Entrada decimal y operaciones finitas exactas con recursos acotados."""
import re
from decimal import Decimal, DecimalException, Inexact, Rounded, localcontext

MAX_CARACTERES = 256
MAX_DIGITOS_ENTRADA = 80
MAX_PRECISION_EXACTA = 10000
MAX_PUNTOS = 10001


class ErrorValidacion(ValueError):
    """Entrada o configuración incompatible con el dominio."""


def decimal_desde_entrada(valor):
    if isinstance(valor, bool) or not isinstance(valor, (str, int, Decimal)):
        raise ErrorValidacion("Use texto, entero o Decimal; float y booleanos no se admiten.")
    texto = str(valor)
    if len(texto) > MAX_CARACTERES:
        raise ErrorValidacion("Entrada demasiado larga: máximo 256 caracteres.")
    texto = texto.strip()
    if not re.fullmatch(r"[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?", texto, flags=re.ASCII):
        raise ErrorValidacion("Número inválido: use punto o coma decimal, sin miles ni espacios internos.")
    if "e" in texto.lower() and abs(int(texto.lower().split("e")[1])) > 100:
        raise ErrorValidacion("El exponente escrito debe estar entre -100 y 100.")
    numero = Decimal(texto.replace(",", "."))
    if not numero.is_finite():
        raise ErrorValidacion("El número debe ser finito.")
    if len(numero.as_tuple().digits) > MAX_DIGITOS_ENTRADA or abs(numero.as_tuple().exponent) > 100:
        raise ErrorValidacion("Máximo 80 dígitos y exponente interno entre -100 y 100; no se recorta la entrada.")
    return numero


def comprobar_resultado(valor):
    if not valor.is_finite() or (valor and abs(valor.adjusted()) > 250):
        raise ErrorValidacion("Resultado fuera del rango numérico admitido (exponente ajustado ±250).")
    if len(valor.as_tuple().digits) > MAX_PRECISION_EXACTA:
        raise ErrorValidacion("El cálculo exacto supera 10000 dígitos; reduzca pasos o dígitos de parámetros.")
    return valor


def exacta(operacion, a, b):
    """Suma/producto sin redondeos. Una precisión insuficiente produce error."""
    if operacion == "producto":
        precision = len(a.as_tuple().digits) + len(b.as_tuple().digits)
    else:
        precision = max(a.adjusted(), b.adjusted(), 0) - min(a.as_tuple().exponent, b.as_tuple().exponent, 0) + 3
    if precision > MAX_PRECISION_EXACTA:
        raise ErrorValidacion("La operación supera el límite de precisión exacta (10000 dígitos).")
    try:
        with localcontext() as contexto:
            contexto.prec = max(precision, 2)
            contexto.traps[Inexact] = True
            contexto.traps[Rounded] = True
            resultado = a * b if operacion == "producto" else a + b
    except DecimalException as error:
        raise ErrorValidacion("No se pudo calcular sin pérdida decimal.") from error
    return comprobar_resultado(resultado)


def sumar(a, b):
    return exacta("suma", a, b)


def multiplicar(a, b):
    return exacta("producto", a, b)
