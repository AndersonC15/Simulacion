from dataclasses import replace
from decimal import Decimal

from Modelo.datos import DATOS_OFICIALES, validar_datos
from Modelo.estimacion import estimar
from Modelo.estrategias import ContinuoEuler, Deterministico, Discreto, Estocastico
from Modelo.numeros import ErrorValidacion
from Modelo.parametros import Parametros
from Modelo.resultados import Experimento


class ControladorSimulacion:
    def __init__(self, datos=DATOS_OFICIALES, parametros=None, estrategias=None):
        self.datos = validar_datos(datos)
        self.parametros = estimar(self.datos) if parametros is None else parametros
        if not isinstance(self.parametros, Parametros):
            raise ErrorValidacion("Se requiere un objeto Parametros.")
        self.estrategias = estrategias if estrategias is not None else {
            "deterministico": Deterministico(), "discreto": Discreto(),
            "estocastico": Estocastico(), "continuo": ContinuoEuler(),
        }
        self.ultimo = None
        self.nombre_escenario = "estimación de observaciones" if parametros is None else "manual"

    def configurar(self, parametros):
        if not isinstance(parametros, Parametros):
            raise ErrorValidacion("Se requiere un objeto Parametros.")
        self.parametros = parametros
        self.nombre_escenario = "manual"
        self.ultimo = None

    def cambiar_datos(self, datos, automatico=True):
        nuevos = validar_datos(datos)
        parametros = estimar(nuevos, self.parametros.precision) if automatico else replace(
            self.parametros, p0=nuevos[0], horizonte=Decimal(len(nuevos) - 1))
        self.configurar(parametros)
        self.datos = nuevos
        self.nombre_escenario = "estimación de observaciones" if automatico else "datos nuevos, parámetros manuales"

    def escenario(self, nombre):
        tasas = {"crecimiento": "0.1", "decrecimiento": "-0.1", "constante": "0"}
        if nombre not in tasas:
            raise ErrorValidacion("Escenario inexistente: crecimiento, decrecimiento o constante.")
        self.configurar(replace(self.parametros, tasa=tasas[nombre], sigma="0"))
        self.nombre_escenario = nombre

    def ejecutar(self, nombre=None):
        if nombre is not None and nombre not in self.estrategias:
            raise ErrorValidacion("Modelo inexistente.")
        seleccion = tuple(self.estrategias.values()) if nombre is None else (self.estrategias[nombre],)
        series = tuple(estrategia.simular(self.parametros) for estrategia in seleccion)
        experimento = Experimento(self.parametros, series, self.datos, self.nombre_escenario)
        self.ultimo = experimento
        return experimento

    def experimento_actual(self):
        return self.ultimo if self.ultimo is not None else self.ejecutar()
