"""Contratos matemáticos y entradas adversas, independientes de la implementación.

Las referencias racionales usan Fraction, y la exponencial se calcula con
100 dígitos para contrastar el contexto de 50 dígitos del experimento.
"""

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction
import random

import numpy as np
import pytest

from Controlador.simulacion import ControladorSimulacion
from Modelo.datos import parsear_arreglo
from Modelo.estimacion import estimar
from Modelo.estrategias import ContinuoEuler, Deterministico, Discreto, Estocastico
from Modelo.numeros import ErrorValidacion, decimal_desde_entrada
from Modelo.parametros import Parametros
from Modelo.resultados import Serie


D = Decimal
MODELOS = (Deterministico, Discreto, Estocastico, ContinuoEuler)


def configuracion(**cambios):
    return Parametros(**dict(p0="1000", tasa="0.1", sigma="0", dt="0.1",
                            horizonte="6", semilla=42, precision=50) | cambios)


def decimal_racional(valor):
    with localcontext() as contexto:
        contexto.prec = 100
        return D(valor.numerator) / D(valor.denominator)


@pytest.mark.parametrize("entrada,esperado", [
    ("0", "0"), ("  1000  ", "1000"), ("+2.50", "2.50"),
    ("-0.125", "-0.125"), ("1,25", "1.25"), ("1e-20", "1e-20"),
    ("2.5E+10", "2.5e10"), (".25", ".25"), ("0,0000000001", "1e-10"),
    (0, "0"), (12345678901234567890, "12345678901234567890"),
    (D("1.000000000000000000001"), "1.000000000000000000001"),
    ("1e100", "1e100"), ("1e-100", "1e-100"), ("9" * 80, "9" * 80),
])
def test_entrada_decimal_conserva_el_valor(entrada, esperado):
    resultado = decimal_desde_entrada(entrada)
    assert isinstance(resultado, Decimal)
    assert resultado == D(esperado)


@pytest.mark.parametrize("entrada", [
    "", "   ", "población", "1.2.3", "1,2,3", "1,234.5", "1.234,5",
    "1 000", "1_000", "0x10", "1/3", "[1]", "1;2", "++1", "--1",
    "NaN", "sNaN", "Infinity", "-Infinity", "inf", "1e101", "1e-101",
    "9" * 81, "1" * 257, "0." + "0" * 255 + "1",
    0.1, float("inf"), float("nan"), True, False, None, [], {}, object(),
])
def test_entrada_decimal_rechaza_ambiguedad_y_limites(entrada):
    with pytest.raises(ErrorValidacion):
        decimal_desde_entrada(entrada)


def test_entero_enorme_tambien_informa_error_de_dominio():
    with pytest.raises(ErrorValidacion):
        decimal_desde_entrada(10**5000)


@pytest.mark.parametrize("texto,esperado", [
    ("1000;1100;1250", ("1000", "1100", "1250")),
    ("[1000; 1100; 1250]", ("1000", "1100", "1250")),
    ("  [1,5; 2,75; 3]  ", ("1.5", "2.75", "3")),
    ("1.5;2.75;3", ("1.5", "2.75", "3")),
    ("0;0;1", ("0", "0", "1")),
    ("42", ("42",)),
    ("[42]", ("42",)),
    ("1e-10;2E-10", ("1e-10", "2e-10")),
])
def test_arreglo_separa_elementos_de_decimales(texto, esperado):
    assert tuple(parsear_arreglo(texto)) == tuple(map(D, esperado))


@pytest.mark.parametrize("texto", [
    "", "[]", "[ ]", "1;", ";1", "1;;2", "[1;2", "1;2]", "[[1;2]]",
    "1,2,3", "1 2 3", "1;NaN", "Infinity;1", "1;-2", "texto",
    "__import__('os').system('echo peligro')", "1;" + "9" * 81,
])
def test_arreglo_invalido_tiene_error_de_dominio(texto):
    with pytest.raises(ErrorValidacion):
        parsear_arreglo(texto)


def test_arreglo_limite_de_observaciones_se_valida_antes_de_reservar_resultados():
    assert len(parsear_arreglo(";".join(["0"] * 10001))) == 10001
    with pytest.raises(ErrorValidacion):
        parsear_arreglo(";".join(["0"] * 10002))
    with pytest.raises(ErrorValidacion):
        parsear_arreglo(" " * 100001)


@pytest.mark.parametrize("campo,valor", [
    ("p0", "-0.001"), ("p0", "NaN"), ("p0", "Infinity"),
    ("sigma", "-1"), ("sigma", "NaN"), ("sigma", "Infinity"),
    ("dt", "0"), ("dt", "-0.1"), ("dt", "NaN"), ("dt", "Infinity"),
    ("horizonte", "-1"), ("horizonte", "NaN"), ("horizonte", "Infinity"),
    ("tasa", "NaN"), ("tasa", "Infinity"), ("tasa", "-Infinity"),
    ("semilla", -1), ("semilla", 1.5), ("semilla", True),
    ("semilla", 2**64),
    ("precision", 0), ("precision", -1), ("precision", 1.5), ("precision", True),
    ("precision", 31), ("precision", 81), ("precision", 201),
])
def test_parametros_validan_llamadas_directas(campo, valor):
    with pytest.raises(ErrorValidacion):
        configuracion(**{campo: valor})


def test_parametros_son_inmutables():
    parametros = configuracion()
    with pytest.raises(FrozenInstanceError):
        parametros.tasa = D("0.2")
    modificado = replace(parametros, tasa="-0.1")
    assert parametros.tasa == D("0.1")
    assert modificado.tasa == D("-0.1")


@pytest.mark.parametrize("modelo,invalido", [
    (Deterministico, None), (Discreto, None), (Estocastico, None), (ContinuoEuler, None),
    (Deterministico, {}), (Discreto, "parametros"), (ContinuoEuler, True),
])
def test_modelos_rechazan_objetos_que_no_son_parametros(modelo, invalido):
    with pytest.raises(ErrorValidacion):
        modelo().simular(invalido)


@pytest.mark.parametrize("tiempos,poblaciones", [
    ((), ()), ((D(0),), (D(1), D(2))),
    ((D(1),), (D(1),)), ((D(0), D(0)), (D(1), D(2))),
    ((D(0), D(2), D(1)), (D(1), D(2), D(3))),
    ((D(0),), (D(-1),)), ((D(0),), (D("NaN"),)),
    ((D(0),), (D("Infinity"),)), ((D(0),), (1,)),
    ([D(0)], (D(1),)),
])
def test_resultados_no_admiten_series_incoherentes(tiempos, poblaciones):
    with pytest.raises(ErrorValidacion):
        Serie("ejemplo", tiempos, poblaciones)


@pytest.mark.parametrize("modelo", MODELOS)
@pytest.mark.parametrize("poblacion", ["0", "1000", "12.345678901234567890123456789"])
def test_tasa_y_ruido_cero_conservan_todas_las_cifras(modelo, poblacion):
    parametros = configuracion(p0=poblacion, tasa="0")
    serie = modelo().simular(parametros)
    assert all(p == D(poblacion) for p in serie.poblaciones)
    assert len(serie.tiempos) == len(serie.poblaciones)


@pytest.mark.parametrize("modelo", MODELOS)
def test_horizonte_cero_incluye_solo_condicion_inicial(modelo):
    serie = modelo().simular(configuracion(horizonte="0"))
    assert serie.tiempos == (D("0"),)
    assert serie.poblaciones == (D("1000"),)


@pytest.mark.parametrize("poblacion,tasa,periodos", [
    ("1000", "0.1", 1), ("1000", "0.1", 6), ("12.5", "0.25", 4),
    ("1000", "-0.1", 6), ("3", "-0.5", 5), ("5", "-1", 4),
    ("0", "0.2", 3), ("1.125", "1.5", 4),
])
def test_discreto_contra_potencias_racionales(poblacion, tasa, periodos):
    parametros = configuracion(p0=poblacion, tasa=tasa, horizonte=str(periodos))
    serie = Discreto().simular(parametros)
    esperados = tuple(decimal_racional(Fraction(poblacion) * (1 + Fraction(tasa)) ** k)
                      for k in range(periodos + 1))
    assert serie.poblaciones == esperados
    assert serie.tiempos == tuple(map(D, range(periodos + 1)))


@pytest.mark.parametrize("poblacion,tasa,paso,horizonte", [
    ("1000", "0.1", "0.5", "1"), ("1000", "0.1", "1", "6"),
    ("12.5", "0.25", "0.5", "2"), ("1000", "-0.1", "0.5", "3"),
    ("64", "-0.5", "0.5", "2"), ("1000", "0.1", "0.3", "1"),
    ("1000", "0.1", "2", "0.5"), ("8", "-0.25", "4", "4"),
])
def test_euler_contra_producto_racional(poblacion, tasa, paso, horizonte):
    parametros = configuracion(p0=poblacion, tasa=tasa, dt=paso, horizonte=horizonte)
    serie = ContinuoEuler().simular(parametros)
    t, final, h = Fraction(0), Fraction(horizonte), Fraction(paso)
    p, r = Fraction(poblacion), Fraction(tasa)
    esperados = [decimal_racional(p)]
    tiempos = [D(0)]
    while t < final:
        incremento = min(h, final - t)
        p *= 1 + incremento * r
        t += incremento
        tiempos.append(decimal_racional(t))
        esperados.append(decimal_racional(p))
    assert serie.poblaciones == tuple(esperados)
    assert serie.tiempos == tuple(tiempos)


@pytest.mark.parametrize("poblacion,tasa,tiempo", [
    ("1000", "0.1", "1"), ("1000", "-0.1", "6"),
    ("12.5", "0.25", "2"), ("1", "-1", "1"),
    ("0.0000000001", "0.1", "0.3"), ("0", "0.1", "2"),
])
def test_exponencial_con_referencia_de_cien_digitos(poblacion, tasa, tiempo):
    parametros = configuracion(p0=poblacion, tasa=tasa, horizonte=tiempo)
    valor = Deterministico().simular(parametros).poblaciones[-1]
    with localcontext() as contexto:
        contexto.prec = 100
        referencia = D(poblacion) * (D(tasa) * D(tiempo)).exp()
        tolerancia = max(abs(referencia), D(1)) * D("1e-48")
        assert abs(valor - referencia) <= tolerancia


@pytest.mark.parametrize("tasa", ["0.1", "-0.1", "0.5", "-0.5"])
def test_euler_converge_al_reducir_paso_en_caso_regular(tasa):
    parametros = configuracion(tasa=tasa, horizonte="2")
    referencia = Deterministico().simular(parametros).poblaciones[-1]
    errores = []
    for paso in ("1", "0.5", "0.1"):
        valor = ContinuoEuler().simular(replace(parametros, dt=paso)).poblaciones[-1]
        errores.append(abs(valor - referencia))
    assert errores[2] < errores[1] < errores[0]


@pytest.mark.parametrize("tasa", ["-1", "-0.5", "0", "0.1", "0.5"])
def test_euler_con_paso_uno_equivale_a_discreto(tasa):
    parametros = configuracion(tasa=tasa, dt="1")
    euler = ContinuoEuler().simular(parametros)
    discreto = Discreto().simular(parametros)
    assert euler.tiempos == discreto.tiempos
    assert euler.poblaciones == discreto.poblaciones


@pytest.mark.parametrize("modelo", [Discreto, Estocastico, ContinuoEuler])
def test_recurrencia_conserva_decimales_mas_alla_de_precision_aproximada(modelo):
    poblacion = "1.23456789012345678901234567890123456789012345678901234567890123456789"
    tasa = "0.1234567890123456789012345678901234567890123456789"
    parametros = configuracion(p0=poblacion, tasa=tasa, dt="1", horizonte="3", precision=32)
    serie = modelo().simular(parametros)
    assert tuple(map(Fraction, serie.poblaciones)) == tuple(
        Fraction(poblacion) * (1 + Fraction(tasa)) ** k for k in range(4)
    )


@pytest.mark.parametrize("tasa", ["-1", "-0.25", "0", "0.1", "1"])
def test_estocastico_sin_ruido_equivale_a_discreto(tasa):
    parametros = configuracion(tasa=tasa, sigma="0")
    aleatorio = Estocastico().simular(parametros)
    discreto = Discreto().simular(parametros)
    assert aleatorio.tiempos == discreto.tiempos
    assert aleatorio.poblaciones == discreto.poblaciones


@pytest.mark.parametrize("modelo", [Deterministico, ContinuoEuler])
@pytest.mark.parametrize("paso,horizonte", [
    ("0.1", "0.3"), ("0.3", "1"), ("2", "0.5"),
    ("0.125", "0.5"), ("0.7", "2"),
])
def test_malla_incluye_extremos_sin_sobrepasar_horizonte(modelo, paso, horizonte):
    serie = modelo().simular(configuracion(dt=paso, horizonte=horizonte))
    assert serie.tiempos[0] == D(0)
    assert serie.tiempos[-1] == D(horizonte)
    assert len(serie.tiempos) == len(serie.poblaciones)
    assert all(a < b for a, b in zip(serie.tiempos, serie.tiempos[1:]))
    assert all(D(0) <= t <= D(horizonte) for t in serie.tiempos)
    assert all(p.is_finite() and p >= 0 for p in serie.poblaciones)


@pytest.mark.parametrize("modelo", [Discreto, Estocastico])
def test_recurrencias_rechazan_horizonte_fraccionario(modelo):
    with pytest.raises(ErrorValidacion):
        modelo().simular(configuracion(horizonte="1.5"))


@pytest.mark.parametrize("tasa", ["-1.01", "-2", "-10"])
def test_discreto_no_oculta_poblaciones_negativas(tasa):
    with pytest.raises(ErrorValidacion):
        Discreto().simular(configuracion(tasa=tasa, horizonte="1"))


def test_restriccion_cero_estocastica_pertenece_a_su_ecuacion():
    serie = Estocastico().simular(configuracion(p0="10", tasa="-2", horizonte="2"))
    assert serie.poblaciones == (D(10), D(0), D(0))


@pytest.mark.parametrize("tasa,paso", [("-2", "1"), ("-0.6", "2"), ("-10", "0.2")])
def test_euler_rechaza_paso_que_destruye_positividad(tasa, paso):
    with pytest.raises(ErrorValidacion):
        ContinuoEuler().simular(configuracion(tasa=tasa, dt=paso, horizonte="2"))


@pytest.mark.parametrize("modelo,cambios", [
    (ContinuoEuler, {"dt": "1e-100"}),
    (Deterministico, {"dt": "1e-100"}),
    (Discreto, {"horizonte": "1e100"}),
    (Estocastico, {"horizonte": "1e100"}),
])
def test_limite_recursos_antes_de_crear_arreglos(modelo, cambios):
    with pytest.raises(ErrorValidacion):
        modelo().simular(configuracion(**cambios))


@pytest.mark.parametrize("modelo", MODELOS)
def test_simular_no_modifica_contexto_decimal_global(modelo):
    contexto = getcontext().copy()
    modelo().simular(configuracion())
    assert getcontext().prec == contexto.prec
    assert getcontext().rounding == contexto.rounding
    assert getcontext().traps == contexto.traps


@pytest.mark.parametrize("modelo", MODELOS)
def test_calculos_no_dependen_de_precision_global_dos(modelo):
    parametros = configuracion(p0="123.45678901234567890123456789",
                              tasa="0.12345678901234567890123456789", horizonte="1")
    with localcontext() as contexto:
        contexto.prec = 100
        referencia = modelo().simular(parametros)
        contexto.prec = 2
        resultado = modelo().simular(parametros)
        assert resultado.tiempos == referencia.tiempos
        assert resultado.poblaciones == referencia.poblaciones
        assert contexto.prec == 2


@pytest.mark.parametrize("tasa,p0", [
    ("500.0000000000000000000000000000000000001", "1e-100"),
    ("-500.0000000000000000000000000000000000001", "1e100"),
])
def test_limite_exponente_no_se_redondea_con_contexto_global(tasa, p0):
    with localcontext() as contexto:
        contexto.prec = 2
        with pytest.raises(ErrorValidacion):
            Deterministico().simular(configuracion(p0=p0, tasa=tasa, horizonte="1"))


@pytest.mark.parametrize("modelo", [Discreto, ContinuoEuler])
def test_factor_negativo_diminuto_no_se_redondea_a_cero(modelo):
    with localcontext() as contexto:
        contexto.prec = 2
        with pytest.raises(ErrorValidacion):
            modelo().simular(configuracion(tasa="-1.0000000000000000000000000001",
                                           dt="1", horizonte="1"))


@pytest.mark.parametrize("modelo,cambios", [
    (Deterministico, {"p0": "1e100", "tasa": "500", "dt": "1", "horizonte": "1"}),
    (Discreto, {"p0": "1e100", "tasa": "1e100", "horizonte": "2"}),
    (ContinuoEuler, {"p0": "1e100", "tasa": "1e100", "dt": "1", "horizonte": "2"}),
    (Estocastico, {"p0": "1e100", "tasa": "1e100", "horizonte": "2"}),
])
def test_resultados_fuera_del_rango_no_se_sustituyen_por_cero(modelo, cambios):
    with pytest.raises(ErrorValidacion):
        modelo().simular(configuracion(**cambios))


@pytest.mark.parametrize("modelo", MODELOS)
def test_modelo_devuelve_resultado_sin_imprimir_ni_pedir_entrada(modelo, monkeypatch, capsys):
    def entrada_prohibida(*args, **kwargs):
        pytest.fail("El modelo no puede solicitar entrada de consola")

    monkeypatch.setattr("builtins.input", entrada_prohibida)
    resultado = modelo().simular(configuracion())
    assert isinstance(resultado, Serie)
    capturado = capsys.readouterr()
    assert capturado.out == capturado.err == ""


def test_semilla_reproduce_y_generador_no_toca_estado_global():
    parametros = configuracion(sigma="10")
    estado_python = random.getstate()
    estado_numpy = np.random.get_state()
    primera = Estocastico().simular(parametros)
    segunda = Estocastico().simular(parametros)
    assert primera.poblaciones == segunda.poblaciones
    assert random.getstate() == estado_python
    posterior_numpy = np.random.get_state()
    assert posterior_numpy[0] == estado_numpy[0]
    assert np.array_equal(posterior_numpy[1], estado_numpy[1])
    assert posterior_numpy[2:] == estado_numpy[2:]


@pytest.mark.parametrize("sigma,esperado", [("3", "112"), ("0.5", "102")])
def test_sigma_escala_desviacion_y_no_varianza(monkeypatch, sigma, esperado):
    class NormalControlada:
        def normal(self, loc=0, scale=1):
            # Fija una realización de dos desviaciones sobre la media.
            return float(loc + 2 * scale)

    monkeypatch.setattr(np.random, "default_rng", lambda semilla: NormalControlada())
    parametros = configuracion(p0="100", tasa="0", sigma=sigma, horizonte="2")
    assert Estocastico().simular(parametros).poblaciones[-1] == D(esperado)


@pytest.mark.parametrize("p0,tasa,ruidos,esperados", [
    ("10", "0", ("-20", "5", "1"), ("10", "0", "5", "6")),
    ("10", "0.1", ("1", "-2", "3"), ("10", "12", "11.2", "15.32")),
    ("10", "-0.5", ("0", "-10", "2"), ("10", "5", "0", "2")),
    ("0", "0.1", ("2", "-100", "3"), ("0", "2", "0", "3")),
])
def test_ruido_controlado_recurrencia_y_cero_no_absorbente(p0, tasa, ruidos, esperados):
    secuencia = iter(map(D, ruidos))
    modelo = Estocastico(ruido=lambda: next(secuencia))
    parametros = configuracion(p0=p0, tasa=tasa, sigma="1", horizonte="3")
    assert modelo.simular(parametros).poblaciones == tuple(map(D, esperados))
    with pytest.raises(StopIteration):
        next(secuencia)


@pytest.mark.parametrize("invalido", ["normal", 1, [1, 2], {}, True])
def test_estrategia_estocastica_rechaza_ruido_que_no_es_funcion(invalido):
    with pytest.raises(ErrorValidacion):
        Estocastico(ruido=invalido)


@pytest.mark.parametrize("invalido", [None, "NaN", "Infinity", "texto", 0.1, True])
def test_ruido_controlado_invalido_tiene_error_de_dominio(invalido):
    with pytest.raises(ErrorValidacion):
        Estocastico(ruido=lambda: invalido).simular(configuracion(horizonte="1"))


def test_mayor_sigma_amplia_dispersion_en_varias_realizaciones_controladas():
    """Cinco realizaciones simétricas: se compara dispersión, no tendencia."""
    finales = {}
    for sigma in (D(1), D(3)):
        finales[sigma] = []
        for z in map(D, (-2, -1, 0, 1, 2)):
            modelo = Estocastico(ruido=lambda z=z, sigma=sigma: z * sigma)
            parametros = configuracion(p0="100", tasa="0", horizonte="1", sigma=sigma)
            finales[sigma].append(modelo.simular(parametros).poblaciones[-1])
    assert sum(finales[D(1)]) == sum(finales[D(3)]) == D(500)
    dispersion_uno = sum((p - D(100)) ** 2 for p in finales[D(1)])
    dispersion_tres = sum((p - D(100)) ** 2 for p in finales[D(3)])
    assert dispersion_tres == 9 * dispersion_uno


@pytest.mark.parametrize("datos,tasa", [
    (("1000", "1100", "1210"), "0.1"),
    (("1000", "900", "810"), "-0.1"),
    (("12.5", "12.5", "12.5"), "0"),
    (("2", "4", "8", "16"), "1"),
])
def test_estimacion_de_recurrencia_exacta(datos, tasa):
    valores = tuple(map(D, datos))
    parametros = estimar(valores)
    assert parametros.p0 == valores[0]
    assert parametros.horizonte == D(len(valores) - 1)
    assert parametros.tasa == D(tasa)
    assert parametros.sigma == 0
    assert valores == tuple(map(D, datos))


@pytest.mark.parametrize("datos", [(), (D(1),), (D(0), D(1)), (D(1), D(0), D(1))])
def test_estimacion_detecta_insuficiencia_y_divisor_cero(datos):
    with pytest.raises(ErrorValidacion):
        estimar(datos)


def test_estimacion_utiliza_todas_las_observaciones_y_dispersion_centrada():
    datos = (D(10), D(20), D(30), D(60))
    parametros = estimar(datos)
    with localcontext() as contexto:
        contexto.prec = 100
        tasa = sum((b - a) / a for a, b in zip(datos, datos[1:])) / D(3)
        residuos = [b - (1 + tasa) * a for a, b in zip(datos, datos[1:])]
        media = sum(residuos) / D(3)
        sigma = (sum((x - media) ** 2 for x in residuos) / D(3)).sqrt()
        assert abs(parametros.tasa - tasa) < D("1e-48")
        assert abs(parametros.sigma - sigma) < D("1e-46")
    assert parametros.p0 == datos[0]
    assert parametros.horizonte == 3


def test_controlador_comparte_configuracion_y_reutiliza_experimento():
    parametros = configuracion(sigma="10")
    controlador = ControladorSimulacion(parametros=parametros)
    experimento = controlador.ejecutar()
    assert experimento.parametros is parametros
    assert len(experimento.series) == 4
    assert experimento.observaciones == controlador.datos
    assert all(s.poblaciones[0] == parametros.p0 for s in experimento.series)
    assert controlador.experimento_actual() is experimento
    assert controlador.ultimo is experimento
    assert controlador.experimento_actual().series[2] is experimento.series[2]


def test_controlador_invalida_resultado_al_configurar():
    controlador = ControladorSimulacion(parametros=configuracion())
    anterior = controlador.ejecutar()
    nuevos = replace(controlador.parametros, tasa="0.2")
    controlador.configurar(nuevos)
    assert controlador.ultimo is None
    actual = controlador.experimento_actual()
    assert actual is not anterior
    assert actual.parametros is nuevos


@pytest.mark.parametrize("escenario,tasa", [
    ("crecimiento", "0.1"), ("decrecimiento", "-0.1"), ("constante", "0"),
])
def test_escenarios_conservan_configuracion_comparable(escenario, tasa):
    controlador = ControladorSimulacion(parametros=configuracion(sigma="10"))
    original = controlador.parametros
    controlador.ejecutar()
    controlador.escenario(escenario)
    assert controlador.ultimo is None
    assert controlador.parametros.tasa == D(tasa)
    assert controlador.parametros.sigma == 0
    assert controlador.parametros.p0 == original.p0
    assert controlador.parametros.horizonte == original.horizonte
    assert controlador.parametros.dt == original.dt
    assert controlador.parametros.semilla == original.semilla
    assert controlador.ejecutar().escenario == escenario


@pytest.mark.parametrize("nombre", ["desconocido", "", "Discreto"])
def test_controlador_rechaza_seleccion_inexistente_y_conserva_resultado(nombre):
    controlador = ControladorSimulacion(parametros=configuracion())
    anterior = controlador.ejecutar()
    with pytest.raises(ErrorValidacion):
        controlador.ejecutar(nombre)
    assert controlador.ultimo is anterior


def test_datos_no_estimables_permiten_modo_manual():
    controlador = ControladorSimulacion(parametros=configuracion())
    originales = controlador.parametros
    controlador.cambiar_datos((D(0), D(1), D(2)), automatico=False)
    assert controlador.datos == (D(0), D(1), D(2))
    assert controlador.parametros.p0 == 0
    assert controlador.parametros.horizonte == 2
    assert controlador.parametros.tasa == originales.tasa
    assert controlador.parametros.sigma == originales.sigma


def test_cambio_datos_fallido_es_atomico():
    controlador = ControladorSimulacion(parametros=configuracion())
    experimento = controlador.ejecutar()
    datos, parametros = controlador.datos, controlador.parametros
    with pytest.raises(ErrorValidacion):
        controlador.cambiar_datos((D(0), D(1)), automatico=True)
    assert controlador.datos is datos
    assert controlador.parametros is parametros
    assert controlador.ultimo is experimento
