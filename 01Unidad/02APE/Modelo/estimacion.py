"""Estimación descriptiva; no es una calibración científica validada."""
from decimal import Decimal, DecimalException, localcontext

from Modelo.datos import validar_datos
from Modelo.numeros import ErrorValidacion, multiplicar, sumar
from Modelo.parametros import Parametros


def estimar(datos, precision=50):
    datos = validar_datos(datos)
    # Valida precisión antes de utilizarla en un contexto.
    Parametros(precision=precision)
    if len(datos) < 2:
        raise ErrorValidacion("La estimación necesita al menos dos observaciones; utilice configuración manual.")
    if any(x == 0 for x in datos[:-1]):
        raise ErrorValidacion("No puede estimarse una tasa relativa con un divisor cero; utilice modo manual.")
    try:
        with localcontext() as contexto:
            contexto.prec = precision + 20
            tasas = [sumar(b, a.copy_negate()) / a for a, b in zip(datos, datos[1:])]
            tasa = sum(tasas, Decimal(0)) / Decimal(len(tasas))
            contexto.prec = precision
            tasa = +tasa  # Única aproximación declarada del parámetro r estimado.
        residuos = [sumar(b, multiplicar(sumar(Decimal(1), tasa), a).copy_negate())
                    for a, b in zip(datos, datos[1:])]
        with localcontext() as contexto:
            contexto.prec = precision + 20
            media = sum(residuos, Decimal(0)) / Decimal(len(residuos))
            varianza = sum(((x - media) ** 2 for x in residuos), Decimal(0)) / Decimal(len(residuos))
            contexto.prec = precision
            sigma = varianza.sqrt()
    except DecimalException as error:
        raise ErrorValidacion("No se pudieron estimar parámetros en el rango numérico admitido.") from error
    return Parametros(p0=datos[0], tasa=tasa, sigma=sigma, horizonte=len(datos) - 1, precision=precision)
