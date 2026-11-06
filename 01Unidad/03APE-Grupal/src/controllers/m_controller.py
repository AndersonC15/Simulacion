"""Controlador: simulación SimPy del sistema M/M/1."""

import random

import simpy

from src.models.m_model import (
    ComparacionEscenario,
    Escenario,
    ModeloMM1,
    ResultadosSimulados,
)

TIEMPO_SIMULACION = 20000
SEMILLA = 42


def _cliente(
    env: simpy.Environment,
    servidor: simpy.Resource,
    mu: float,
    registro: dict,
):
    llegada = env.now

    with servidor.request() as solicitud:
        yield solicitud
        espera = env.now - llegada
        registro["tiempos_espera"].append(espera)
        registro["llegadas"].append(llegada)
        registro["estados_cola"].append((env.now, len(servidor.queue)))

        duracion = random.expovariate(mu)
        registro["tiempos_servicio"].append(duracion)
        yield env.timeout(duracion)

        registro["estados_cola"].append((env.now, len(servidor.queue)))
        registro["salidas"].append(env.now)


def _generar_clientes(
    env: simpy.Environment,
    servidor: simpy.Resource,
    lam: float,
    mu: float,
    registro: dict,
):
    while True:
        yield env.timeout(random.expovariate(lam))
        registro["estados_cola"].append((env.now, len(servidor.queue)))
        env.process(_cliente(env, servidor, mu, registro))


def _calcular_promedio_temporal(
    eventos: list[tuple[float, int]], horizon: float
) -> float:
    """Calcula el promedio temporal a partir de pares (tiempo, valor)."""
    if not eventos:
        return 0.0
    eventos = sorted(eventos)
    integral = 0.0
    for i in range(len(eventos) - 1):
        t, v = eventos[i]
        t_siguiente = eventos[i + 1][0]
        integral += v * (t_siguiente - t)
    ultimo_t, ultimo_v = eventos[-1]
    integral += ultimo_v * max(horizon - ultimo_t, 0.0)
    return integral / horizon


def simular_escenario(escenario: Escenario) -> ComparacionEscenario:
    """Ejecuta la simulación SimPy para un escenario y compara con lo teórico."""
    random.seed(SEMILLA)
    env = simpy.Environment()
    servidor = simpy.Resource(env, capacity=1)

    registro = {
        "tiempos_espera": [],
        "estados_cola": [],
        "llegadas": [],
        "salidas": [],
        "tiempos_servicio": [],
    }

    env.process(
        _generar_clientes(
            env, servidor, escenario.lam, escenario.mu, registro
        )
    )
    env.run(until=TIEMPO_SIMULACION)

    teoricos = ModeloMM1.calcular_teoricos(escenario.lam, escenario.mu)

    n = len(registro["tiempos_espera"])
    wq_sim = sum(registro["tiempos_espera"]) / n if n else 0.0

    tiempo_total_sistema = 0.0
    for espera, llegada, salida in zip(
        registro["tiempos_espera"], registro["llegadas"], registro["salidas"]
    ):
        tiempo_total_sistema += salida - llegada
    w_sim = tiempo_total_sistema / n if n else 0.0

    lq_sim = _calcular_promedio_temporal(
        registro["estados_cola"], TIEMPO_SIMULACION
    )
    l_sim = lq_sim + teoricos.rho

    tiempo_servicio_total = sum(registro["tiempos_servicio"])
    utilizacion = tiempo_servicio_total / TIEMPO_SIMULACION

    simulados = ResultadosSimulados(
        Wq=wq_sim,
        W=w_sim,
        Lq=lq_sim,
        L=l_sim,
        utilizacion=min(utilizacion, 1.0),
    )

    return ComparacionEscenario(
        escenario=escenario,
        teoricos=teoricos,
        simulados=simulados,
        tiempos_espera=registro["tiempos_espera"],
        tamanios_cola=[v for _, v in registro["estados_cola"]],
        reloj_llegadas=[t for t, _ in registro["estados_cola"]],
    )
