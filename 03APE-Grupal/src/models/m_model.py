"""Modelo M/M/1: cálculos teóricos y estructuras de datos."""

from dataclasses import dataclass, field


@dataclass
class Escenario:
    lam: float
    mu: float
    condicion: str

    @property
    def rho(self) -> float:
        return self.lam / self.mu

    @property
    def es_estable(self) -> bool:
        return self.lam < self.mu


@dataclass
class ResultadosTeoricos:
    rho: float
    L: float
    Lq: float
    W: float
    Wq: float


@dataclass
class ResultadosSimulados:
    Wq: float
    W: float
    Lq: float
    L: float
    utilizacion: float


@dataclass
class ComparacionEscenario:
    escenario: Escenario
    teoricos: ResultadosTeoricos
    simulados: ResultadosSimulados
    tiempos_espera: list = field(default_factory=list)
    tamanios_cola: list = field(default_factory=list)
    reloj_llegadas: list = field(default_factory=list)


class ModeloMM1:
    """Lógica de cálculo teórico del modelo M/M/1."""

    @staticmethod
    def calcular_teoricos(lam: float, mu: float) -> ResultadosTeoricos:
        if lam >= mu:
            raise ValueError("El sistema no es estable: se requiere λ < μ")

        rho = lam / mu
        L = lam / (mu - lam)
        Lq = lam**2 / (mu * (mu - lam))
        W = 1.0 / (mu - lam)
        Wq = lam / (mu * (mu - lam))

        return ResultadosTeoricos(rho=rho, L=L, Lq=Lq, W=W, Wq=Wq)

    @staticmethod
    def construir_escenarios() -> list[Escenario]:
        return [
            Escenario(lam=2.0, mu=3.0, condicion="Sistema estable"),
            Escenario(lam=2.5, mu=3.0, condicion="Mayor utilización"),
            Escenario(lam=2.9, mu=3.0, condicion="Cerca de saturación"),
        ]
