"""Modelo matemático decimal del índice de lluvia descrito en la guía."""

from dataclasses import dataclass
from decimal import Decimal

from Modelo.precision import (
    EntradaDecimal, convertir_decimal, decimal_finito, multiplicar, sumar,
)


def validar_intervalo(valor: EntradaDecimal, minimo: str, maximo: str, nombre: str) -> Decimal:
    numero = decimal_finito(valor)
    if not Decimal(minimo) <= numero <= Decimal(maximo):
        raise ValueError(f"{nombre} debe estar entre {minimo} y {maximo}.")
    return numero


LIMITES_MEDICION = {"humedad": ("0", "100"), "nubosidad": ("0", "100"),
                    "temperatura": ("-50", "60")}


def validar_medicion(valor: EntradaDecimal, campo: str) -> Decimal:
    minimo, maximo = LIMITES_MEDICION[campo]
    return validar_intervalo(convertir_decimal(valor), minimo, maximo, campo.capitalize())


@dataclass(frozen=True)
class ParametrosModelo:
    """Pesos finitos, no negativos y de suma decimal exactamente igual a uno."""

    humedad: Decimal
    nubosidad: Decimal
    temperatura: Decimal
    nombre: str

    def __post_init__(self) -> None:
        for campo in ("humedad", "nubosidad", "temperatura"):
            peso = convertir_decimal(getattr(self, campo))
            validar_intervalo(peso, "0", "1", "El peso")
            object.__setattr__(self, campo, peso)
        if sumar(self.humedad, self.nubosidad, self.temperatura) != Decimal("1"):
            raise ValueError("La suma de los tres pesos debe ser exactamente 1.")

    @property
    def descripcion(self) -> str:
        return f"{self.nombre} ({self.humedad}H + {self.nubosidad}N + {self.temperatura}Tf)"


ORIGINAL = ParametrosModelo(Decimal("0.50"), Decimal("0.30"), Decimal("0.20"), "Modelo original")
AJUSTADO = ParametrosModelo(Decimal("0.40"), Decimal("0.40"), Decimal("0.20"), "Modelo ajustado")
TEMPERATURAS = tuple(Decimal(str(t)) for t in range(10, 29, 2))
FACTORES_TEMPERATURA = tuple(Decimal(t) for t in (
    "1.00", "0.90", "0.80", "0.70", "0.60", "0.50", "0.40", "0.30", "0.20", "0.10",
))
UMBRALES = (Decimal("0.40"), Decimal("0.60"), Decimal("0.75"))
ESTADOS = ("Sin lluvia", "Baja posibilidad", "Lluvia probable", "Lluvia")


def normalizar_porcentaje(valor: EntradaDecimal) -> Decimal:
    numero = convertir_decimal(valor)
    validar_intervalo(numero, "0", "100", "El porcentaje")
    return multiplicar(numero, Decimal("0.01"))


def calcular_factor_temperatura(temperatura: EntradaDecimal) -> Decimal:
    """Interpolación lineal: cada grado resta 0.05 dentro de la tabla."""
    numero = convertir_decimal(temperatura)
    validar_intervalo(numero, "-50", "60", "La temperatura")
    if numero <= TEMPERATURAS[0]:
        return FACTORES_TEMPERATURA[0]
    if numero >= TEMPERATURAS[-1]:
        return FACTORES_TEMPERATURA[-1]
    diferencia = sumar(numero, Decimal("-10"))
    return sumar(Decimal("1"), multiplicar(diferencia, Decimal("-0.05")))


def calcular_indice(h: EntradaDecimal, n: EntradaDecimal, tf: EntradaDecimal,
                    parametros: ParametrosModelo) -> Decimal:
    h = validar_intervalo(h, "0", "1", "H")
    n = validar_intervalo(n, "0", "1", "N")
    tf = validar_intervalo(tf, "0", "1", "Tf")
    return sumar(multiplicar(parametros.humedad, h),
                 multiplicar(parametros.nubosidad, n),
                 multiplicar(parametros.temperatura, tf))


def clasificar_indice(indice: EntradaDecimal) -> str:
    numero = validar_intervalo(indice, "0", "1", "El índice")
    for umbral, estado in zip(UMBRALES, ESTADOS):
        if numero < umbral:
            return estado
    return ESTADOS[-1]


@dataclass(frozen=True)
class RegistroMeteorologico:
    """Medición validada, independiente de su origen (consola o tabla)."""

    hora: str
    humedad: Decimal
    nubosidad: Decimal
    temperatura: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.hora, str) or not self.hora.strip():
            raise ValueError("El registro debe tener una hora o etiqueta.")
        for campo in LIMITES_MEDICION:
            numero = validar_medicion(getattr(self, campo), campo)
            object.__setattr__(self, campo, numero)


@dataclass(frozen=True)
class ResultadoLluvia:
    registro: RegistroMeteorologico
    humedad_normalizada: Decimal
    nubosidad_normalizada: Decimal
    factor_temperatura: Decimal
    indice: Decimal
    estado: str

    @property
    def porcentaje(self) -> Decimal:
        return multiplicar(self.indice, Decimal("100"))

    @property
    def tiene_lluvia_probable_o_lluvia(self) -> bool:
        return self.indice >= UMBRALES[1]


class ModeloLluvia:
    """Evalúa registros con pesos sustituibles, sin conocer la interfaz."""

    def evaluar(self, registro: RegistroMeteorologico,
                parametros: ParametrosModelo = ORIGINAL) -> ResultadoLluvia:
        h = normalizar_porcentaje(registro.humedad)
        n = normalizar_porcentaje(registro.nubosidad)
        tf = calcular_factor_temperatura(registro.temperatura)
        indice = calcular_indice(h, n, tf, parametros)
        return ResultadoLluvia(registro, h, n, tf, indice, clasificar_indice(indice))

    def evaluar_tabla(self, registros: tuple[RegistroMeteorologico, ...],
                     parametros: ParametrosModelo) -> list[ResultadoLluvia]:
        return [self.evaluar(registro, parametros) for registro in registros]
