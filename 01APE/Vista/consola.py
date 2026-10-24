"""Entrada y presentación de consola; las reglas pertenecen al modelo."""

from collections.abc import Callable
from decimal import Decimal

from Modelo.modelo import RegistroMeteorologico, ResultadoLluvia
from Modelo.precision import convertir_decimal


def texto_decimal(valor: Decimal) -> str:
    """Representación exacta sin ceros finales superfluos ni redondeo."""
    texto = format(valor, "f")
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


class VistaConsola:
    def __init__(self, leer: Callable[[str], str] = input,
                 escribir: Callable[[str], None] = print) -> None:
        self.leer = leer
        self.escribir = escribir

    def mostrar_mensaje(self, mensaje: str) -> None:
        self.escribir(mensaje)

    def leer_opcion(self) -> str:
        self.escribir("\n=== Modelo de índice de lluvia ===\n"
                      "1. Tabla con modelo original\n2. Tabla con modelo ajustado\n"
                      "3. Generar gráficas\n4. Ingresar un caso manual\n0. Salir")
        return self.leer("Opción: ").strip()

    def leer_numero(self, mensaje: str, minimo: int, maximo: int) -> Decimal:
        while True:
            try:
                numero = convertir_decimal(self.leer(mensaje))
            except ValueError:
                self.escribir("Ingrese un número válido.")
                continue
            if minimo <= numero <= maximo:
                return numero
            self.escribir(f"El valor debe estar entre {minimo} y {maximo}.")

    def leer_registro(self) -> RegistroMeteorologico:
        self.escribir("\n--- Caso manual (modelo original) ---")
        humedad = self.leer_numero("Humedad (%): ", 0, 100)
        nubosidad = self.leer_numero("Nubosidad (%): ", 0, 100)
        temperatura = self.leer_numero("Temperatura (°C): ", -50, 60)
        return RegistroMeteorologico("Caso manual", humedad, nubosidad, temperatura)

    def mostrar_resultado(self, resultado: ResultadoLluvia) -> None:
        self.escribir(f"H  = {texto_decimal(resultado.humedad_normalizada)}")
        self.escribir(f"N  = {texto_decimal(resultado.nubosidad_normalizada)}")
        self.escribir(f"Tf = {texto_decimal(resultado.factor_temperatura)}")
        self.escribir(f"Índice I = {texto_decimal(resultado.indice)} "
                      f"({texto_decimal(resultado.porcentaje)}%)")
        self.escribir(f"Estado: {resultado.estado}")

    def mostrar_tabla(self, resultados: list[ResultadoLluvia], titulo: str) -> None:
        encabezados = ["Hora", "Humedad %", "Nubosidad %", "Temp. °C", "H", "N", "Tf", "Índice", "Estado"]
        filas = []
        for resultado in resultados:
            registro = resultado.registro
            numeros = (registro.humedad, registro.nubosidad, registro.temperatura,
                       resultado.humedad_normalizada, resultado.nubosidad_normalizada,
                       resultado.factor_temperatura, resultado.indice)
            filas.append([registro.hora, *(texto_decimal(n) for n in numeros), resultado.estado])
        anchos = [max(len(fila[i]) for fila in [encabezados, *filas]) for i in range(len(encabezados))]
        self.escribir(f"\n{titulo}")
        for fila in [encabezados, *filas]:
            self.escribir(" | ".join(texto.ljust(ancho) for texto, ancho in zip(fila, anchos)))
        horas = [r.registro.hora for r in resultados if r.tiene_lluvia_probable_o_lluvia]
        self.escribir("\nHoras con lluvia probable o lluvia: " + (", ".join(horas) or "ninguna"))
