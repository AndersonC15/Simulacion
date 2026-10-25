"""El menú se prueba con entradas reales de texto y cancelación inyectada."""

from decimal import Decimal
from pathlib import Path
import os
import subprocess
import sys

import pytest

from Controlador.simulacion import ControladorSimulacion
from Modelo.parametros import Parametros
from main import VistaConsola


class Entrada:
    def __init__(self, pasos):
        self.pasos = iter(pasos)
        self.preguntas = []

    def __call__(self, pregunta=""):
        self.preguntas.append(pregunta)
        try:
            paso = next(self.pasos)
        except StopIteration:
            raise EOFError from None
        if isinstance(paso, BaseException):
            raise paso
        return paso


def ejecutar(pasos, controlador=None):
    controlador = controlador or ControladorSimulacion(parametros=Parametros())
    salida = []
    entrada = Entrada(pasos)
    VistaConsola(controlador, entrada=entrada, salida=salida.append).ejecutar()
    return controlador, "\n".join(salida), entrada


def test_salir_no_calcula_experimento():
    controlador, salida, _ = ejecutar(["0"])
    assert controlador.ultimo is None
    assert "Hasta luego" in salida


@pytest.mark.parametrize("opcion", ["", "texto", "12", "-1", "1.0"])
def test_opcion_inexistente_se_recupera_y_permite_simular(opcion):
    controlador, salida, _ = ejecutar([opcion, "2", "0"])
    assert "Opción inexistente" in salida
    assert len(controlador.ultimo.series) == 1
    assert controlador.ultimo.series[0].poblaciones[-1] == Decimal("1771.561")
    assert "Hasta luego" in salida


@pytest.mark.parametrize("opcion,nombre", [
    ("1", "Determinístico"), ("2", "Discreto"),
    ("3", "Estocástico"), ("4", "Euler"),
])
def test_menu_selecciona_cada_estrategia(opcion, nombre):
    controlador, salida, _ = ejecutar([opcion, "0"])
    assert len(controlador.ultimo.series) == 1
    assert nombre in controlador.ultimo.series[0].nombre
    assert nombre in salida


def test_comparacion_presenta_las_cuatro_series_con_configuracion_comun():
    controlador, salida, _ = ejecutar(["5", "0"])
    assert len(controlador.ultimo.series) == 4
    assert controlador.ultimo.parametros is controlador.parametros
    assert all(s.nombre in salida for s in controlador.ultimo.series)


def test_consultar_configuracion_presenta_datos_y_decimales_completos():
    controlador = ControladorSimulacion(parametros=Parametros(p0="1.2345678901234567890123456789"))
    _, salida, _ = ejecutar(["6", "0"], controlador)
    assert "1000; 1100; 1250; 1400; 1600; 1850; 2100" in salida
    assert "1.2345678901234567890123456789" in salida
    assert "semilla = 42" in salida
    assert controlador.ultimo is None


def test_modificar_parametros_conserva_texto_decimal_y_configura_semilla():
    valores = ["123.45678901234567890123456789", "-0,2", "3.5", "0.25", "2", "0", "80"]
    controlador, salida, _ = ejecutar(["7", *valores, "0"])
    assert controlador.parametros.p0 == Decimal(valores[0])
    assert controlador.parametros.tasa == Decimal("-0.2")
    assert controlador.parametros.sigma == Decimal("3.5")
    assert controlador.parametros.dt == Decimal("0.25")
    assert controlador.parametros.horizonte == 2
    assert controlador.parametros.semilla == 0
    assert controlador.parametros.precision == 80
    assert "Parámetros actualizados" in salida


def test_enter_conserva_los_siete_parametros():
    controlador = ControladorSimulacion(parametros=Parametros())
    originales = controlador.parametros
    ejecutar(["7", *("" for _ in range(7)), "0"], controlador)
    assert controlador.parametros == originales


@pytest.mark.parametrize("campo,valor", [
    (0, "-1"), (1, "NaN"), (2, "-2"), (3, "0"), (4, "-1"),
])
def test_modificacion_invalida_no_aplica_cambios_parciales(campo, valor):
    controlador = ControladorSimulacion(parametros=Parametros())
    originales = controlador.parametros
    entradas = [""] * 7
    entradas[campo] = valor
    _, salida, _ = ejecutar(["7", *entradas, "2", "0"], controlador)
    assert "Error:" in salida
    assert controlador.parametros is originales
    assert controlador.ultimo.parametros is originales
    assert controlador.ultimo.series[0].poblaciones[-1] == Decimal("1771.561")


@pytest.mark.parametrize("valor", ["-1", "1.5", "True", "9" * 257])
def test_semilla_invalida_recupera_menu(valor):
    controlador, salida, _ = ejecutar(["7", "", "", "", "", "", valor, "0"])
    assert controlador.parametros.semilla == 42
    assert "Error:" in salida
    assert "Hasta luego" in salida


@pytest.mark.parametrize("fallo", [EOFError, KeyboardInterrupt])
@pytest.mark.parametrize("prefijo", [[], ["7", ""], ["8"], ["9", "1;2"]])
def test_eof_y_ctrl_c_cierran_limpio_sin_configuracion_parcial(fallo, prefijo):
    controlador = ControladorSimulacion(parametros=Parametros())
    originales = controlador.parametros
    _, salida, _ = ejecutar([*prefijo, fallo()], controlador)
    assert controlador.parametros is originales
    assert controlador.ultimo is None
    assert "Entrada finalizada" in salida


def test_arreglo_nuevo_estimado_actualiza_condicion_horizonte_y_tasa():
    controlador, salida, _ = ejecutar(["9", "[10;20;40]", "a", "2", "0"])
    assert controlador.datos == tuple(map(Decimal, (10, 20, 40)))
    assert controlador.parametros.p0 == 10
    assert controlador.parametros.horizonte == 2
    assert controlador.parametros.tasa == 1
    assert controlador.parametros.sigma == 0
    assert controlador.ultimo.series[0].poblaciones == tuple(map(Decimal, (10, 20, 40)))
    assert "Error:" not in salida


def test_arreglo_con_ceros_admite_configuracion_manual():
    controlador, salida, _ = ejecutar(["9", "0;1;2", "m", "2", "0"])
    assert controlador.datos == tuple(map(Decimal, (0, 1, 2)))
    assert controlador.parametros.tasa == Decimal("0.1")
    assert controlador.ultimo.series[0].poblaciones == (Decimal(0),) * 3
    assert "Error:" not in salida


@pytest.mark.parametrize("arreglo,modo", [("0;1", "a"), ("1;2", "x")])
def test_arreglo_incompatible_no_sustituye_datos_anteriores(arreglo, modo):
    controlador = ControladorSimulacion(parametros=Parametros())
    datos, parametros = controlador.datos, controlador.parametros
    _, salida, _ = ejecutar(["9", arreglo, modo, "2", "0"], controlador)
    assert controlador.datos is datos
    assert controlador.parametros is parametros
    assert "Error:" in salida
    assert controlador.ultimo.parametros is parametros


@pytest.mark.parametrize("arreglo", ["[]", "1;;2", "1,2,3", "1;NaN", "1;-2"])
def test_arreglo_invalido_recupera_menu(arreglo):
    controlador, salida, _ = ejecutar(["9", arreglo, "2", "0"])
    assert "Error:" in salida
    assert controlador.ultimo is not None


@pytest.mark.parametrize("escenario,tasa", [
    ("crecimiento", "0.1"), ("decrecimiento", "-0.1"), ("constante", "0"),
])
def test_escenarios_desde_menu(escenario, tasa):
    controlador, salida, _ = ejecutar(["8", escenario, "5", "0"])
    assert controlador.parametros.tasa == Decimal(tasa)
    assert controlador.ultimo.escenario == escenario
    assert "Error:" not in salida


def test_escenario_inexistente_no_interrumpe_menu():
    controlador, salida, _ = ejecutar(["8", "inventado", "2", "0"])
    assert "Error:" in salida
    assert controlador.parametros.tasa == Decimal("0.1")
    assert controlador.ultimo is not None


def test_graficas_desde_menu_reutilizan_mismo_experimento(monkeypatch, tmp_path):
    recibidos = []

    def guardar(vista, experimento, *args, **kwargs):
        recibidos.append(experimento)
        return tmp_path / "comparacion.png", tmp_path / "comparacion.csv"

    monkeypatch.setattr("Vista.graficas.VistaGraficas.guardar", guardar)
    controlador, salida, _ = ejecutar(["5", "10", "10", "0"])
    assert len(recibidos) == 2
    assert recibidos[0] is recibidos[1] is controlador.ultimo
    assert "comparacion.png" in salida
    assert "comparacion.csv" in salida


@pytest.mark.parametrize("error", [PermissionError, OSError, ImportError, RuntimeError])
def test_fallo_grafico_recupera_menu_sin_perder_experimento(monkeypatch, error):
    def guardar(*args, **kwargs):
        raise error("fallo controlado de salida")

    monkeypatch.setattr("Vista.graficas.VistaGraficas.guardar", guardar)
    controlador, salida, _ = ejecutar(["5", "10", "6", "0"])
    assert controlador.ultimo is not None
    assert "fallo controlado de salida" in salida
    assert "Hasta luego" in salida


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="chmod requiere POSIX sin privilegios root")
def test_permiso_real_de_escritura_recupera_menu_y_cierra_figura(monkeypatch, tmp_path):
    from Vista.graficas import VistaGraficas
    import matplotlib.pyplot as plt

    destino = tmp_path / "sin permiso de escritura"
    destino.mkdir()
    destino.chmod(0o500)
    guardar_original = VistaGraficas.guardar

    def guardar(vista, experimento, *args, **kwargs):
        return guardar_original(vista, experimento, destino, mostrar=False)

    monkeypatch.setattr(VistaGraficas, "guardar", guardar)
    controlador = ControladorSimulacion(parametros=Parametros())
    anterior = controlador.ejecutar()
    try:
        _, salida, _ = ejecutar(["10", "6", "0"], controlador)
        assert "No pudo completarse la salida" in salida
        assert controlador.ultimo is anterior
        assert list(destino.iterdir()) == []
        assert plt.get_fignums() == []
    finally:
        destino.chmod(0o700)


def test_opcion_netlogo_envia_experimento_guardado(monkeypatch):
    recibidos = []

    def enviar(vista):
        recibidos.append(vista.controlador.experimento_actual())

    monkeypatch.setattr(VistaConsola, "enviar_netlogo", enviar)
    controlador, _, _ = ejecutar(["5", "11", "11", "0"])
    assert len(recibidos) == 2
    assert recibidos[0] is recibidos[1] is controlador.ultimo


def test_adaptacion_consola_netlogo_reutiliza_serie_y_no_sobrescribe_exportacion(monkeypatch, tmp_path):
    from Vista.puente_netlogo import InformeNetLogo, PuenteNetLogo

    controlador = ControladorSimulacion(parametros=Parametros(sigma="10"))
    anterior = controlador.ejecutar()
    recibidos = []
    rutas = []

    def enviar(puente, experimento, netlogo_home=None, **kwargs):
        recibidos.append(experimento)
        rutas.append(kwargs["salida_plot"])
        return InformeNetLogo("prueba", "prueba", "prueba", tuple(len(s.tiempos) for s in experimento.series),
                              tuple(float(s.poblaciones[-1]) for s in experimento.series), 0, True,
                              kwargs["salida_plot"], None)

    monkeypatch.setattr(PuenteNetLogo, "enviar", enviar)
    salida = []
    vista = VistaConsola(controlador, salida=salida.append)
    vista.enviar_netlogo(directorio=tmp_path)
    vista.enviar_netlogo(directorio=tmp_path)
    assert recibidos[0] is recibidos[1] is anterior
    assert rutas[0] != rutas[1]
    assert all(r.parent == tmp_path for r in rutas)
    assert "Datos de retorno verificados: True" in "\n".join(salida)


def test_error_netlogo_se_traduce_y_menu_permanece_utilizable(monkeypatch, tmp_path):
    from Vista.puente_netlogo import ErrorNetLogo, PuenteNetLogo

    def fallar(*args, **kwargs):
        raise ErrorNetLogo("NetLogo no disponible en prueba controlada")

    enviar_original = VistaConsola.enviar_netlogo
    monkeypatch.setattr(PuenteNetLogo, "enviar", fallar)
    monkeypatch.setattr(VistaConsola, "enviar_netlogo", lambda vista: enviar_original(vista, directorio=tmp_path))
    controlador, salida, _ = ejecutar(["5", "11", "6", "0"])
    assert controlador.ultimo is not None
    assert "Error: NetLogo no disponible en prueba controlada" in salida
    assert "Hasta luego" in salida


def test_analisis_ruido_desde_menu_conserva_experimento_y_presenta_tres_niveles():
    controlador = ControladorSimulacion(parametros=Parametros(sigma="5"))
    anterior = controlador.ejecutar()
    originales = controlador.parametros
    _, salida, _ = ejecutar(["a", "0"], controlador)
    assert controlador.ultimo is anterior
    assert controlador.parametros is originales
    assert "30 semillas compartidas por nivel" in salida
    assert all(f"{sigma} | " in salida for sigma in (0, 5, 10))
    assert "una curva no demuestra tendencia poblacional" in salida


def test_error_analisis_ruido_recupera_menu_sin_perder_experimento():
    controlador = ControladorSimulacion(parametros=Parametros(horizonte="101"))
    anterior = controlador.ejecutar("discreto")
    _, salida, _ = ejecutar(["a", "6", "0"], controlador)
    assert controlador.ultimo is anterior
    assert "Error:" in salida and "100 períodos" in salida
    assert "Hasta luego" in salida


def test_proceso_real_acepta_eof_sin_traceback():
    raiz = Path(__file__).resolve().parents[1]
    proceso = subprocess.run([sys.executable, str(raiz / "main.py")], cwd=raiz,
                             input="", text=True, capture_output=True, timeout=15)
    assert proceso.returncode == 0
    assert "Entrada finalizada" in proceso.stdout
    assert "Traceback" not in proceso.stderr


def test_cli_comparacion_funciona_desde_ruta_con_espacios(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    ubicacion = tmp_path / "directorio con espacios"
    ubicacion.mkdir()
    entorno = dict(os.environ, MPLBACKEND="Agg")
    proceso = subprocess.run([sys.executable, str(raiz / "main.py"), "--comparar",
                              "--escenario", "decrecimiento"], cwd=ubicacion,
                             env=entorno, text=True, capture_output=True, timeout=15)
    assert proceso.returncode == 0, proceso.stderr
    assert all(nombre in proceso.stdout for nombre in ("Determinístico", "Discreto", "Estocástico", "Euler"))
    assert "decrecimiento" in proceso.stdout


def test_cli_graficas_guarda_resultados_en_ruta_con_espacios(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    salida = tmp_path / "salida con espacios"
    proceso = subprocess.run([sys.executable, str(raiz / "main.py"), "--graficas", "--salida", str(salida)],
                             cwd=tmp_path, env=dict(os.environ, MPLBACKEND="Agg"),
                             text=True, capture_output=True, timeout=30)
    assert proceso.returncode == 0, proceso.stderr
    assert (salida / "comparacion.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    tabla = (salida / "comparacion.csv").read_text()
    assert "Determinístico" in tabla and "Observación de referencia" in tabla
    assert "Estocástico" in tabla and "Euler" in tabla


def test_cli_analisis_ruido_reproducible_y_presenta_dispersion(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    argumentos = [sys.executable, str(raiz / "main.py"), "--analizar-ruido"]
    primera = subprocess.run(argumentos, cwd=tmp_path, text=True, capture_output=True, timeout=15)
    segunda = subprocess.run(argumentos, cwd=tmp_path, text=True, capture_output=True, timeout=15)
    assert primera.returncode == segunda.returncode == 0
    assert primera.stdout == segunda.stdout
    assert "30 semillas compartidas por nivel" in primera.stdout
    assert "desviación poblacional final aproximada" in primera.stdout
    assert "recorte a cero puede sesgar la media" in primera.stdout
    assert len([linea for linea in primera.stdout.splitlines() if linea.count(" | ") == 2]) == 4


def test_cli_ruta_netlogo_inexistente_informa_error_sin_traceback(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    proceso = subprocess.run([sys.executable, str(raiz / "main.py"), "--netlogo",
                              "--netlogo-home", str(tmp_path / "NetLogo inexistente"),
                              "--salida", str(tmp_path / "salidas")],
                             cwd=tmp_path, text=True, capture_output=True, timeout=15)
    assert proceso.returncode == 1
    assert "NetLogo" in proceso.stderr + proceso.stdout
    assert "Traceback" not in proceso.stderr


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="chmod requiere POSIX sin privilegios root")
def test_cli_sin_permiso_salida_no_deja_archivos_y_explica_error(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    salida = tmp_path / "sin permiso"
    salida.mkdir()
    salida.chmod(0o500)
    try:
        proceso = subprocess.run([sys.executable, str(raiz / "main.py"), "--graficas", "--salida", str(salida)],
                                 cwd=tmp_path, env=dict(os.environ, MPLBACKEND="Agg"),
                                 text=True, capture_output=True, timeout=30)
        assert proceso.returncode == 1
        assert "Traceback" not in proceso.stderr
        assert "Error" in proceso.stderr + proceso.stdout
        assert list(salida.iterdir()) == []
    finally:
        salida.chmod(0o700)


@pytest.mark.skipif(os.name != "posix", reason="Señal SIGINT real disponible en POSIX")
def test_sigint_real_mientras_el_menu_espera_entrada():
    import select
    import signal
    import time
    ruta = Path(__file__).resolve().parents[1] / "main.py"
    proceso = subprocess.Popen([sys.executable, "-u", str(ruta)], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    recibido = b""
    limite = time.monotonic() + 5
    try:
        while b"Opcion:" not in recibido and b"Opci\xc3\xb3n:" not in recibido and time.monotonic() < limite:
            if select.select([proceso.stdout], [], [], 0.1)[0]:
                recibido += os.read(proceso.stdout.fileno(), 4096)
        assert b"Opci\xc3\xb3n:" in recibido
        proceso.send_signal(signal.SIGINT)
        salida, errores = proceso.communicate(timeout=5)
        assert proceso.returncode == 0
        assert "Entrada finalizada" in salida.decode()
        assert b"Traceback" not in errores
    finally:
        if proceso.poll() is None:
            proceso.kill()
            proceso.communicate()
