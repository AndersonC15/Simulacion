import math

import numpy as np
import pytest
from scipy.stats import chisquare, kstest

from ape06.modelo.datos import ParametrosLCG, ResultadoPrueba
from ape06.modelo.experimentos import EstimadorPi, ServicioSimulacion
from ape06.modelo.lcg import GeneradorLCG
from ape06.modelo.pruebas import ChiCuadrado, KolmogorovSmirnov, Rachas


def parametros(**cambios):
    return ParametrosLCG(**(dict(nombre="ejemplo", semilla=1, a=5, c=1, m=16) | cambios))


def test_ciclo_lcg_calculado_a_mano():
    muestra = GeneradorLCG(parametros()).generar(16)
    assert muestra.estados.tolist() == [6, 15, 12, 13, 2, 11, 8, 9, 14, 7, 4, 5, 10, 3, 0, 1]
    assert muestra.valores[0] == 6 / 16
    assert muestra.valores[-1] == 1 / 16


def test_vector_conocido_park_miller_y_reproducibilidad():
    p = parametros(a=16807, c=0, m=2**31-1)
    a, b = GeneradorLCG(p).generar(5), GeneradorLCG(p).generar(5)
    assert a.estados.tolist() == [16807, 282475249, 1622650073, 984943658, 1144108930]
    np.testing.assert_array_equal(a.estados, b.estados)


def test_parametros_48_bits_no_desbordan():
    muestra = GeneradorLCG(parametros(a=25214903917, c=11, m=2**48)).generar(5)
    assert muestra.estados.tolist() == [25214903928, 206026503483683, 245470556921330, 105707381795861, 223576932655868]


@pytest.mark.parametrize("cambios", [{"m": 0}, {"a": -1}, {"c": 16}, {"semilla": 16},
                                     {"m": 2**53+1}, {"nombre": "../salida"}, {"semilla": True}])
def test_rechaza_parametros_invalidos(cambios):
    with pytest.raises(ValueError):
        parametros(**cambios)


def test_chi_limites_sin_perdidas_y_frecuencias_esperadas():
    valores = np.tile(np.arange(10) / 10, 5)
    resultado = ChiCuadrado().evaluar(valores, .05)
    assert [b.observada for b in resultado.intervalos] == [5]*10
    assert resultado.estadistico == 0
    assert resultado.valor_p == 1
    assert resultado.critico == pytest.approx(16.9189776046)
    valores = np.r_[np.zeros(48), np.nextafter(.3, 0), .3]
    resultado = ChiCuadrado().evaluar(valores, .05)
    assert resultado.intervalos[2].observada == 1
    assert resultado.intervalos[3].observada == 1


def test_ks_con_ejemplo_manual_y_sin_mutar_orden():
    valores = np.array([.1, .4, .35, .8])
    copia = valores.copy()
    resultado = KolmogorovSmirnov().evaluar(valores, .05)
    assert resultado.detalles["d_mas"] == pytest.approx(.35)
    assert resultado.detalles["d_menos"] == pytest.approx(.1)
    assert resultado.estadistico == pytest.approx(.35)
    np.testing.assert_array_equal(valores, copia)


@pytest.mark.parametrize("nombre,a,c,m,semilla", [
    ("minstd", 16807, 0, 2**31-1, 123457),
    ("glibc", 1103515245, 12345, 2**32, 1),
    ("zx81", 75, 74, 2**17+1, 1),
])
def test_estadisticos_contra_scipy(nombre, a, c, m, semilla):
    valores = GeneradorLCG(ParametrosLCG(nombre, semilla, a, c, m)).generar(10000).valores
    chi = ChiCuadrado().evaluar(valores, .05)
    referencia_chi = chisquare([b.observada for b in chi.intervalos], f_exp=[1000]*10)
    assert chi.estadistico == pytest.approx(referencia_chi.statistic, abs=1e-12)
    assert chi.valor_p == pytest.approx(referencia_chi.pvalue, abs=1e-12)
    ks = KolmogorovSmirnov().evaluar(valores, .05)
    referencia_ks = kstest(valores, "uniform", method="asymp")
    assert ks.estadistico == pytest.approx(referencia_ks.statistic, abs=1e-15)
    assert ks.valor_p == pytest.approx(referencia_ks.pvalue, abs=1e-12)


def test_uniformidad_no_implica_independencia():
    valores = GeneradorLCG(parametros(semilla=0, a=1, c=1, m=100)).generar(100).valores
    assert ChiCuadrado().evaluar(valores, .05).valor_p == 1
    assert KolmogorovSmirnov().evaluar(valores, .05).valor_p > .05
    assert Rachas().evaluar(valores, .05).valor_p < .05


def test_rachas_alternadas_y_empates():
    alternados = np.tile([.2, .8], 12)
    r = Rachas().evaluar(alternados, .05)
    assert r.detalles["rachas"] == 24
    assert r.detalles["media_rachas"] == 13
    assert r.valor_p < .05
    r = Rachas().evaluar(np.array([.5, .1, .9]), .05)
    assert r.detalles["empates"] == 1
    assert r.valor_p is None
    assert r.decision == "No aplicable"
    assert Rachas().evaluar(np.full(50, .5), .05).valor_p is None


@pytest.mark.parametrize("valores", [np.array([]), np.array([np.nan]), np.array([np.inf]),
                                     np.array([1.0]), np.array([-.1]), np.ones((2, 2))])
def test_rechaza_muestras_invalidas(valores):
    with pytest.raises(ValueError):
        KolmogorovSmirnov().evaluar(valores, .05)


def test_chi_rechaza_esperadas_menores_a_cinco():
    with pytest.raises(ValueError, match="N >= 50"):
        ChiCuadrado().evaluar(np.full(49, .5), .05)


def test_decision_en_el_limite_alfa():
    resultado = ResultadoPrueba("ejemplo", "h0", 0, .05, 0, .05, "prueba")
    assert resultado.decision == "No se rechaza H0"


def test_pi_con_ocho_puntos_comprobables_y_periodo_acotado():
    r = EstimadorPi().estimar(parametros(), 8)
    assert r.dentro == 6
    assert r.estimacion == 3
    assert r.error_absoluto == pytest.approx(abs(3 - math.pi))
    analisis = ServicioSimulacion((ChiCuadrado(), KolmogorovSmirnov(), Rachas())).analizar(parametros(), 50, .05)
    assert analisis.periodo_observado == 16
    assert analisis.distintos == 16
