"""Controlador: coordina los datos de entrada y el modelo matemático."""

from Modelo.modelo import (
    ParametrosModelo, calcular_factor_temperatura, calcular_indice,
    clasificar_indice, normalizar_porcentaje,
)


def procesar_registro(humedad: float, nubosidad: float, temperatura: float,
                      parametros: ParametrosModelo, hora: str = "Caso manual") -> dict:
    h = normalizar_porcentaje(humedad)
    n = normalizar_porcentaje(nubosidad)
    tf = calcular_factor_temperatura(temperatura)
    indice = calcular_indice(h, n, tf, parametros)
    return {"hora": hora, "humedad": humedad, "nubosidad": nubosidad,
            "temperatura": temperatura, "H": h, "N": n, "Tf": tf,
            "I": indice, "estado": clasificar_indice(indice)}


def procesar_tabla(registros: list[tuple], parametros: ParametrosModelo) -> list[dict]:
    return [procesar_registro(h, n, t, parametros, hora) for hora, h, n, t in registros]
