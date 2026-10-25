from dataclasses import dataclass
from decimal import Decimal

from Modelo.numeros import ErrorValidacion, decimal_desde_entrada


@dataclass(frozen=True)
class Parametros:
    p0: Decimal = Decimal("1000")
    tasa: Decimal = Decimal("0.1")
    sigma: Decimal = Decimal("0")
    dt: Decimal = Decimal("0.1")
    horizonte: Decimal = Decimal("6")
    semilla: int = 42
    precision: int = 50

    def __post_init__(self):
        for nombre in ("p0", "tasa", "sigma", "dt", "horizonte"):
            object.__setattr__(self, nombre, decimal_desde_entrada(getattr(self, nombre)))
        if self.p0 < 0 or self.sigma < 0:
            raise ErrorValidacion("P0 y sigma deben ser no negativos.")
        if self.dt <= 0:
            raise ErrorValidacion("dt debe ser positivo.")
        if not 0 <= self.horizonte <= 10000:
            raise ErrorValidacion("Horizonte admitido: de 0 a 10000 períodos.")
        if isinstance(self.semilla, bool) or not isinstance(self.semilla, int) or not 0 <= self.semilla < 2**64:
            raise ErrorValidacion("La semilla debe ser un entero entre 0 y 2^64-1.")
        if isinstance(self.precision, bool) or not isinstance(self.precision, int) or not 32 <= self.precision <= 200:
            raise ErrorValidacion("La precisión de aproximación debe ser un entero entre 32 y 200.")
