from Modelo.numeros import MAX_PUNTOS, ErrorValidacion, decimal_desde_entrada

DATOS_OFICIALES = tuple(decimal_desde_entrada(x) for x in (1000, 1100, 1250, 1400, 1600, 1850, 2100))


def validar_datos(datos):
    if not isinstance(datos, (tuple, list)) or not 1 <= len(datos) <= MAX_PUNTOS:
        raise ErrorValidacion("Se requiere una lista de 1 a 10001 observaciones.")
    valores = tuple(decimal_desde_entrada(x) for x in datos)
    if any(x < 0 for x in valores):
        raise ErrorValidacion("Las observaciones deben ser no negativas.")
    return valores


def parsear_arreglo(texto):
    """Elementos separados por ;. Coma o punto son separadores decimales."""
    if not isinstance(texto, str) or len(texto) > 100000:
        raise ErrorValidacion("El arreglo admite como máximo 100000 caracteres.")
    texto = texto.strip()
    if texto.startswith("[") and texto.endswith("]"):
        texto = texto[1:-1]
    if texto.count(";") >= MAX_PUNTOS:
        raise ErrorValidacion("Demasiadas observaciones: máximo 10001.")
    return validar_datos(texto.split(";"))
