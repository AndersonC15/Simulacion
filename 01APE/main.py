"""Vista principal de consola de la práctica 01."""

from Controlador.controlador import procesar_registro, procesar_tabla
from Modelo.datos import REGISTROS
from Modelo.modelo import AJUSTADO, ORIGINAL
from Vista.graficas import generar_graficas


def leer_numero(mensaje: str, minimo: float, maximo: float) -> float:
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
        except ValueError:
            print("Ingrese un número válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"El valor debe estar entre {minimo} y {maximo}.")


def caso_manual() -> None:
    print("\n--- Caso manual (modelo original) ---")
    humedad = leer_numero("Humedad (%): ", 0, 100)
    nubosidad = leer_numero("Nubosidad (%): ", 0, 100)
    temperatura = leer_numero("Temperatura (°C): ", -50, 60)
    resultado = procesar_registro(humedad, nubosidad, temperatura, ORIGINAL)
    print(f"\nH  = {resultado['H']:.2f}")
    print(f"N  = {resultado['N']:.2f}")
    print(f"Tf = {resultado['Tf']:.2f}")
    print(f"Índice I = {resultado['I']:.3f} ({resultado['I'] * 100:.1f}%)")
    print(f"Estado: {resultado['estado']}")


def imprimir_tabla(resultados: list[dict], titulo: str) -> None:
    print(f"\n{titulo}")
    encabezado = (f"{'Hora':<7}{'Humedad':>9}{'Nubosidad':>11}{'Temp.':>8}"
                  f"{'H':>7}{'N':>7}{'Tf':>7}{'Índice':>9}  Estado")
    print(encabezado)
    print("-" * len(encabezado))
    for fila in resultados:
        print(f"{fila['hora']:<7}{fila['humedad']:>9.0f}{fila['nubosidad']:>11.0f}"
              f"{fila['temperatura']:>8.0f}{fila['H']:>7.2f}{fila['N']:>7.2f}"
              f"{fila['Tf']:>7.2f}{fila['I']:>9.3f}  {fila['estado']}")
    horas_lluvia = [f["hora"] for f in resultados
                     if f["estado"] in ("Lluvia probable", "Lluvia")]
    print("\nHoras con lluvia probable o lluvia:", ", ".join(horas_lluvia) or "ninguna")


def menu() -> None:
    originales = procesar_tabla(REGISTROS, ORIGINAL)
    ajustados = procesar_tabla(REGISTROS, AJUSTADO)
    while True:
        print("\n=== Modelo de índice de lluvia ===")
        print("1. Tabla con modelo original")
        print("2. Tabla con modelo ajustado")
        print("3. Generar gráficas")
        print("4. Ingresar un caso manual")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            imprimir_tabla(originales, "MODELO ORIGINAL (0.5H + 0.3N + 0.2Tf)")
        elif opcion == "2":
            imprimir_tabla(ajustados, "MODELO AJUSTADO (0.4H + 0.4N + 0.2Tf)")
        elif opcion == "3":
            rutas = generar_graficas(originales, ajustados)
            print("\nGráficas generadas correctamente:")
            for ruta in rutas:
                print(f"- {ruta}")
        elif opcion == "4":
            caso_manual()
        elif opcion == "0":
            print("Programa finalizado.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()
