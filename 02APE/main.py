"""Vista de consola y arranque. Las ecuaciones pertenecen a Modelo/."""
import argparse
from dataclasses import fields
from decimal import Decimal

from Controlador.simulacion import ControladorSimulacion
from Modelo.datos import parsear_arreglo
from Modelo.numeros import ErrorValidacion
from Modelo.parametros import Parametros


def formatear_numero(valor: Decimal | int) -> str:
    """Muestra hasta cinco decimales sin redondear ni alterar el valor original."""
    texto = format(valor, "f") if isinstance(valor, Decimal) else str(valor)
    entero, _, decimales = texto.partition(".")
    decimales = decimales[:5].rstrip("0")
    if entero == "-0" and not decimales:
        entero = "0"
    return f"{entero}.{decimales}" if decimales else entero


class VistaConsola:
    def __init__(self, controlador, entrada=input, salida=print):
        self.controlador = controlador
        self.entrada = entrada
        self.salida = salida

    def mostrar_configuracion(self):
        self.salida("Observaciones (períodos 0..n-1): " + "; ".join(map(formatear_numero, self.controlador.datos)))
        for campo in fields(Parametros):
            self.salida(f"{campo.name} = {formatear_numero(getattr(self.controlador.parametros, campo.name))}")
        self.salida("r y sigma iniciales son estimaciones descriptivas; dt y semilla son decisiones de implementación.")

    def presentar(self, experimento):
        self.salida(f"Escenario: {experimento.escenario}. Tabla de extremos; máximo cinco decimales sin redondear.")
        for serie in experimento.series:
            self.salida(f"{serie.nombre} | {len(serie.tiempos)} puntos")
            self.salida(f"Tiempo={formatear_numero(serie.tiempos[0])} | Población={formatear_numero(serie.poblaciones[0])}")
            if len(serie.tiempos) > 1:
                self.salida(f"Tiempo={formatear_numero(serie.tiempos[-1])} | Población={formatear_numero(serie.poblaciones[-1])}")
        self.salida("La tasa exponencial es instantánea; la discreta es relativa por período. Euler aproxima dP/dt=rP.")

    def modificar(self):
        actual = self.controlador.parametros
        nuevos = {}
        for campo in fields(Parametros):
            texto = self.entrada(f"{campo.name} [{formatear_numero(getattr(actual, campo.name))}] (Enter conserva): ")
            if texto.strip():
                if campo.name in ("semilla", "precision"):
                    if len(texto) > 256 or not texto.strip().isascii() or not texto.strip().isdigit():
                        raise ErrorValidacion(f"{campo.name}: se requiere entero no negativo, hasta 256 caracteres.")
                    nuevos[campo.name] = int(texto.strip())
                else:
                    nuevos[campo.name] = texto
            else:
                nuevos[campo.name] = getattr(actual, campo.name)
        self.controlador.configurar(Parametros(**nuevos))
        self.salida("Parámetros actualizados; la siguiente ejecución creará un experimento nuevo.")

    def nuevo_arreglo(self):
        texto = self.entrada("Observaciones separadas por ; (coma o punto decimal), ejemplo [1000;1100;1250]: ")
        datos = parsear_arreglo(texto)
        modo = self.entrada("Modo: a=estimar automáticamente, m=conservar r/sigma/dt/semilla manuales: ").strip().lower()
        if modo not in ("a", "m"):
            raise ErrorValidacion("Seleccione a o m.")
        self.controlador.cambiar_datos(datos, automatico=modo == "a")
        self.mostrar_configuracion()

    def graficar(self):
        from Vista.graficas import VistaGraficas
        rutas = VistaGraficas().guardar(self.controlador.experimento_actual(), mostrar=True)
        self.salida("Archivos guardados: " + ", ".join(map(str, rutas)))

    def analizar_ruido(self):
        from Modelo.analisis import analizar_ruido
        resumenes = analizar_ruido(self.controlador.parametros)
        self.salida("30 semillas compartidas por nivel: sigma | media final aproximada | desviación poblacional final aproximada")
        for resumen in resumenes:
            self.salida(f"{formatear_numero(resumen.sigma)} | {formatear_numero(resumen.media)} | {formatear_numero(resumen.desviacion)}")
        self.salida("Se compara dispersión entre realizaciones; una curva no demuestra tendencia poblacional. El recorte a cero puede sesgar la media.")
        return resumenes

    def ejecutar(self):
        modelos = {"1": "deterministico", "2": "discreto", "3": "estocastico", "4": "continuo"}
        try:
            while True:
                self.salida("\n1 Exponencial | 2 Discreto | 3 Estocástico | 4 Euler | 5 Comparar\n"
                            "6 Datos/parámetros | 7 Modificar | 8 Escenario | 9 Nuevo arreglo | 10 Gráficas\n"
                            "a Analizar ruido (30 semillas) | 0 Salir")
                try:
                    opcion = self.entrada("Opción: ").strip()
                    if opcion == "0":
                        self.salida("Hasta luego.")
                        return
                    if opcion in modelos or opcion == "5":
                        self.presentar(self.controlador.ejecutar(modelos.get(opcion)))
                    elif opcion == "6":
                        self.mostrar_configuracion()
                    elif opcion == "7":
                        self.modificar()
                    elif opcion == "8":
                        self.controlador.escenario(self.entrada("crecimiento / decrecimiento / constante: ").strip().lower())
                        self.mostrar_configuracion()
                    elif opcion == "9":
                        self.nuevo_arreglo()
                    elif opcion == "10":
                        self.graficar()
                    elif opcion.lower() == "a":
                        self.analizar_ruido()
                    else:
                        self.salida("Opción inexistente; vuelva a intentarlo.")
                except ErrorValidacion as error:
                    self.salida(f"Error: {error}")
                except (OSError, ImportError, RuntimeError) as error:
                    self.salida(f"No pudo completarse la salida: {error}")
        except (EOFError, KeyboardInterrupt):
            self.salida("\nEntrada finalizada. Hasta luego.")


def main():
    parser = argparse.ArgumentParser(description="APE02: comparación de modelos poblacionales")
    parser.add_argument("--comparar", action="store_true", help="ejecutar los cuatro modelos y salir")
    parser.add_argument("--escenario", choices=("crecimiento", "decrecimiento", "constante"))
    parser.add_argument("--graficas", action="store_true", help="guardar PNG y CSV del experimento")
    parser.add_argument("--escenarios", action="store_true", help="guardar crecimiento, decrecimiento y constancia comparables")
    parser.add_argument("--salida", help="directorio de resultados; por defecto 02APE/resultados")
    parser.add_argument("--mostrar", action="store_true", help="abrir figuras si hay backend interactivo")
    parser.add_argument("--analizar-ruido", action="store_true", help="comparar sigma con 30 semillas por nivel y salir")
    argumentos = parser.parse_args()
    controlador = ControladorSimulacion()
    if argumentos.escenario:
        controlador.escenario(argumentos.escenario)
    vista = VistaConsola(controlador)
    if argumentos.analizar_ruido:
        vista.analizar_ruido()
    elif argumentos.escenarios:
        from Vista.graficas import VistaGraficas
        for nombre in ("crecimiento", "decrecimiento", "constante"):
            controlador.escenario(nombre)
            rutas = VistaGraficas().guardar(controlador.ejecutar(), argumentos.salida,
                                            mostrar=argumentos.mostrar, nombre=nombre)
            print("Archivos guardados:", *rutas)
    elif argumentos.comparar or argumentos.graficas:
        vista.mostrar_configuracion()
        experimento = controlador.ejecutar()
        vista.presentar(experimento)
        if argumentos.graficas:
            from Vista.graficas import VistaGraficas
            print("Archivos guardados:", *VistaGraficas().guardar(experimento, argumentos.salida, mostrar=argumentos.mostrar))
    else:
        vista.ejecutar()


def arranque():
    import sys
    try:
        main()
        return 0
    except (ErrorValidacion, OSError, ImportError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada finalizada. Hasta luego.")
        return 0


if __name__ == "__main__":
    raise SystemExit(arranque())
