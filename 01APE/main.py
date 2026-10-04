from datos import REGISTROS
from modelo import ORIGINAL, AJUSTADO

humedad = 90
nubosidad = 80
temperatura = 18

Humedad = humedad /100
Nubosidad = nubosidad /100

Tf = 0.60

Resultado = 0.5 * Humedad + 0.3 * Nubosidad + 0.2 * Tf


print(f"Humedad normalizada: {Humedad:.2f}")
print(f"Nubosidad normalizada: {Nubosidad:.2f}")
print(f"Factor temperatura: {Tf:.2f}")

print(f"El índice de lluvia es: {Resultado:.2f}")

def leer_numero(mensaje, minimo, maximo):
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
        except ValueError:
            print("Ingrese un número válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"El valor debe estar entre {minimo} y {maximo}.")



def caso_manual():
    print("\n--- Caso manual (modelo original) ---")
    humedad = leer_numero("Humedad (%): ", 0, 100)
    nubosidad = leer_numero("Nubosidad (%): ", 0, 100)
    temperatura = leer_numero("Temperatura (°C): ", -50, 60)
    r = procesar_registro(humedad, nubosidad, temperatura, ORIGINAL)
    print(f"\nH  = {r['H']:.2f}")
    print(f"N  = {r['N']:.2f}")
    print(f"Tf = {r['Tf']:.2f}")
    print(f"Índice I = {r['I']:.3f} ({r['I'] * 100:.1f}%)")
    print(f"Estado: {r['estado']}")


def imprimir_tabla(resultados, titulo):
    print(f"\n{titulo}")
    encabezado = f"{'Hora':<7}{'Hum':>5}{'Nub':>5}{'Temp':>6}{'H':>7}{'N':>7}{'Tf':>7}{'Índice':>9}  Estado"
    print(encabezado)
    print("-" * (len(encabezado) + 18))
    for (hora, hum, nub, temp), r in zip(REGISTROS, resultados):
        print(f"{hora:<7}{hum:>5}{nub:>5}{temp:>6}{r['H']:>7.2f}{r['N']:>7.2f}{r['Tf']:>7.2f}{r['I']:>9.3f}  {r['estado']}")
    horas_lluvia = [r["hora"] for r in resultados if r["estado"] in ("Lluvia probable", "Lluvia")]
    print("\nHoras con posibilidad de lluvia (probable o lluvia):", ", ".join(horas_lluvia) or "ninguna")



def menu():
    while True:
        print("\n=== Modelo de índice de lluvia ===")
        print("1. Tabla con modelo original")
        print("2. Tabla con modelo ajustado")
        print("3. Generar gráficas")
        print("4. Ingresar un caso manual")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            imprimir_tabla(procesar_tabla(REGISTROS, ORIGINAL), "MODELO ORIGINAL (0.5H + 0.3N + 0.2Tf)")
        elif opcion == "2":
            imprimir_tabla(procesar_tabla(REGISTROS, AJUSTADO), "MODELO AJUSTADO (0.4H + 0.4N + 0.2Tf)")
        elif opcion == "3":
            generar_graficas()
        elif opcion == "4":
            caso_manual()
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()