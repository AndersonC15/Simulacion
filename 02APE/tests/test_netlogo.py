"""Frontera double y pruebas reales opcionales, claramente separadas."""

from dataclasses import replace
from decimal import Decimal, localcontext
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from Modelo.parametros import Parametros
from Modelo.resultados import Experimento, Serie
from Controlador.simulacion import ControladorSimulacion
from Vista.puente_netlogo import (
    ErrorNetLogo, MODELO_PREDEFINIDO, PuenteNetLogo, localizar_netlogo,
    numero_visual, preparar_envio,
)


D = Decimal


def experimento_minimo():
    return Experimento(
        Parametros(p0="1000", tasa="0.1", sigma="2", dt="0.5", horizonte="1"),
        (Serie("Determinístico exponencial", (D(0), D(1)),
               (D(1000), D("1105.1709180756476248117078264902466682245471947375"))),
         Serie("Discreto", (D(0), D(1)), (D(1000), D(1100))),
         Serie("Estocástico", (D(0), D(1)), (D(1000), D("1101.1234567890123456789"))),
         Serie("Continuo (Euler, aproximación)", (D(0), D("0.5"), D(1)),
               (D(1000), D(1050), D("1102.5")))),
        (D(1000), D(1100)), "Prueba reproducible",
    )


@pytest.mark.parametrize("texto", ["0", "-0", "0.1", "-0.1", "1e100", "1e-100", "123.12345678901234567890123456789"])
def test_conversion_double_aislada(texto):
    valor = D(texto)
    assert numero_visual(valor) == float(texto)
    assert str(valor) == str(D(texto))


@pytest.mark.parametrize("valor", [D("NaN"), D("sNaN"), D("Infinity"), D("-Infinity"), D("1e400"), D("1e-400"), D("1e-323"), 0.1, "1"])
def test_conversion_invalida_rechazada(valor):
    with pytest.raises(ErrorNetLogo):
        numero_visual(valor)


def test_conversion_no_depende_de_contexto_global():
    with localcontext() as contexto:
        contexto.prec = 2
        assert numero_visual(D("0.1234567890123456789")) == 0.12345678901234568
        assert contexto.prec == 2


def test_envio_conserva_experimento_y_malla_euler():
    experimento = experimento_minimo()
    antes = repr(experimento)
    envio = preparar_envio(experimento)
    assert [len(s["tiempos"]) for s in envio["series"]] == [2, 2, 2, 3]
    assert envio["series"][2]["poblaciones"][-1] == float(experimento.series[2].poblaciones[-1])
    assert envio["observaciones"] == [[0, 1000.0], [1, 1100.0]]
    assert repr(experimento) == antes


def test_parametros_transportados_sin_redondeo_de_semilla():
    experimento = experimento_minimo()
    parametros = replace(experimento.parametros, semilla=2**64 - 1, tasa="0.12345678901234567890123456789")
    envio = preparar_envio(replace(experimento, parametros=parametros))
    assert ["semilla", "18446744073709551615"] in envio["parametros"]
    assert ["tasa", "0.12345678901234567890123456789"] in envio["parametros"]


def test_tiempos_distintos_no_se_fusionan_silenciosamente():
    serie = Serie("Discreto", (D(0), D(1), D("1.00000000000000000000001")), (D(1), D(2), D(3)))
    with pytest.raises(ErrorNetLogo, match="fusionaría"):
        preparar_envio(replace(experimento_minimo(), series=(serie,)))


@pytest.mark.parametrize("cantidad", [0, 5])
def test_cantidad_de_series_limitada(cantidad):
    experimento = experimento_minimo()
    with pytest.raises(ErrorNetLogo, match="una a cuatro"):
        preparar_envio(replace(experimento, series=(experimento.series[0],) * cantidad))


def test_envio_limita_puntos_antes_de_conversion():
    # Un objeto adverso permite probar el límite del adaptador independientemente del dominio.
    serie = SimpleNamespace(nombre="Exceso", tiempos=(D(0),) * 100_001, poblaciones=(D(1),) * 100_001)
    with pytest.raises(ErrorNetLogo, match="100000"):
        preparar_envio(replace(experimento_minimo(), series=(serie,)))


def test_ruta_explicitamente_erronea_no_usa_otro_netlogo(tmp_path, monkeypatch):
    monkeypatch.setenv("NETLOGO_HOME", str(tmp_path))
    with pytest.raises(ErrorNetLogo, match="NetLogo no está disponible"):
        localizar_netlogo(tmp_path / "ruta con espacios ausente")


def test_ruta_netlogo_con_espacios_reconocida(tmp_path):
    instalacion = tmp_path / "NetLogo con espacios"
    jars = instalacion / "lib" / "app"
    jars.mkdir(parents=True)
    (jars / "netlogo-7.0.4.jar").write_bytes(b"")
    assert localizar_netlogo(instalacion) == instalacion.resolve()


@pytest.mark.parametrize("timeout", [0, -1, True, "60", float("inf"), float("nan"), 301])
def test_timeout_invalido_no_inicia_jvm(timeout):
    with pytest.raises(ErrorNetLogo, match="tiempo máximo"):
        PuenteNetLogo().enviar(experimento_minimo(), timeout=timeout)


def test_captura_sin_gui_rechazada():
    with pytest.raises(ErrorNetLogo, match="captura de interfaz"):
        PuenteNetLogo().enviar(experimento_minimo(), salida_interfaz="innecesaria.png")


@pytest.mark.parametrize("segundos", [0, 4, 31, float("nan"), True])
def test_ventana_tiene_duracion_limitada(segundos):
    with pytest.raises(ErrorNetLogo, match="entre 5 y 30"):
        PuenteNetLogo().enviar(experimento_minimo(), gui=True, segundos_vista=segundos)


@pytest.fixture
def netlogo_real():
    if os.environ.get("APE02_PROBAR_NETLOGO") != "1":
        pytest.skip("Integración real opcional: use APE02_PROBAR_NETLOGO=1 y NETLOGO_HOME.")
    pytest.importorskip("pynetlogo")
    return localizar_netlogo()


def test_real_cuatro_series_retorno_y_repeticion(netlogo_real, tmp_path):
    experimento = ControladorSimulacion().experimento_actual()
    antes = repr(experimento)
    puente = PuenteNetLogo()
    primer = puente.enviar(experimento, netlogo_real, salida_plot=tmp_path / "primer plot.csv")
    segundo = puente.enviar(experimento, netlogo_real, salida_plot=tmp_path / "segundo plot.csv")
    assert primer.datos_verificados and segundo.datos_verificados
    assert primer.puntos_por_serie == (61, 7, 7, 61)
    assert primer.poblaciones_finales == segundo.poblaciones_finales
    assert primer.agentes == segundo.agentes == 0
    assert primer.version_netlogo == "7.0.4"
    assert '"export-plot data (NetLogo 7.0.4)"' in primer.archivo_plot.read_text()
    assert repr(experimento) == antes


def test_real_cero_horizonte_sin_observaciones_y_texto_escapado(netlogo_real):
    parametros = replace(experimento_minimo().parametros, horizonte="0")
    serie = Serie('Discreto "dato"', (D(0),), (D(1000),))
    experimento = Experimento(parametros, (serie,), (), 'Escenario " ] clear-all [ "')
    informe = PuenteNetLogo().enviar(experimento, netlogo_real)
    assert informe.puntos_por_serie == (1,)
    assert informe.poblaciones_finales == (1000.0,)
    assert informe.datos_verificados


def test_real_modelo_invalido_informa_y_cierra(netlogo_real, tmp_path):
    modelo = tmp_path / "modelo inválido.nlogox"
    modelo.write_text("Esto no es un modelo XML", encoding="utf-8")
    with pytest.raises(ErrorNetLogo, match="NetLogo"):
        PuenteNetLogo().enviar(experimento_minimo(), netlogo_real, modelo=modelo)
    assert PuenteNetLogo().enviar(experimento_minimo(), netlogo_real).datos_verificados


def test_real_jvm_invalida_informa(netlogo_real, tmp_path):
    with pytest.raises(ErrorNetLogo, match="NetLogo"):
        PuenteNetLogo().enviar(experimento_minimo(), netlogo_real, jvm_path=tmp_path / "jvm inexistente.so")


def test_real_timeout_termina_y_permite_otro_envio(netlogo_real):
    with pytest.raises(ErrorNetLogo, match="se terminó el proceso"):
        PuenteNetLogo().enviar(experimento_minimo(), netlogo_real, timeout=0.001)
    assert PuenteNetLogo().enviar(experimento_minimo(), netlogo_real).datos_verificados


def test_real_no_sobrescribe_salida_existente(netlogo_real, tmp_path):
    archivo = tmp_path / "conservar.csv"
    archivo.write_text("dato del usuario", encoding="utf-8")
    with pytest.raises(ErrorNetLogo, match="ya existe"):
        PuenteNetLogo().enviar(experimento_minimo(), netlogo_real, salida_plot=archivo)
    assert archivo.read_text() == "dato del usuario"


def test_real_modelo_en_ruta_con_espacios(netlogo_real, tmp_path):
    carpeta = tmp_path / "modelo con espacios"
    carpeta.mkdir()
    modelo = carpeta / "población.nlogox"
    modelo.write_bytes(MODELO_PREDEFINIDO.read_bytes())
    assert PuenteNetLogo().enviar(experimento_minimo(), netlogo_real, modelo=modelo).datos_verificados
