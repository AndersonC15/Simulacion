"""Adaptación de un experimento inmutable a NetLogo; no ejecuta simulaciones.

La JVM vive en un proceso auxiliar por envío. El proceso principal nunca carga
JPype, por lo que repetir un envío no intenta reiniciar una JVM ya cerrada.
"""

from dataclasses import dataclass
from decimal import Context, Decimal, localcontext
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


MAX_PUNTOS_NETLOGO = 100_000
MODELO_PREDEFINIDO = Path(__file__).resolve().parents[1] / "netlogo" / "poblacion.nlogox"


class ErrorNetLogo(ValueError):
    """Fallo de configuración, conversión, comunicación o cierre del puente."""


@dataclass(frozen=True)
class InformeNetLogo:
    version_netlogo: str
    version_java: str
    version_pynetlogo: str
    puntos_por_serie: tuple[int, ...]
    poblaciones_finales: tuple[float, ...]
    agentes: int
    datos_verificados: bool
    archivo_plot: Path | None
    archivo_interfaz: Path | None


def numero_visual(valor: Decimal) -> float:
    """Única frontera Decimal → double; rechaza pérdidas catastróficas.

Se admite el redondeo binario ordinario (tolerancia relativa 1e-12), pero no
infinito, subdesbordamiento a cero ni pérdidas relativas mayores a ese límite.
Los valores convertidos nunca regresan al dominio para continuar cálculos.
"""
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ErrorNetLogo("NetLogo necesita valores Decimal finitos.")
    convertido = float(valor)
    if not math.isfinite(convertido) or (valor != 0 and convertido == 0):
        raise ErrorNetLogo("Un valor excede el rango double de NetLogo.")
    if valor != 0:
        # Decimal.from_float aquí mide el error ya producido, no recupera precisión.
        with localcontext(Context(prec=80)):
            error = abs(Decimal.from_float(convertido) - valor)
            if error > abs(valor) * Decimal("1e-12"):
                raise ErrorNetLogo("La conversión a NetLogo perdería precisión relevante.")
    return convertido


def localizar_netlogo(ruta: str | Path | None = None) -> Path:
    """Primero ruta explícita, después NETLOGO_HOME; búsqueda local limitada."""
    configurada = ruta if ruta is not None else os.environ.get("NETLOGO_HOME")
    if configurada is not None:
        candidatos = [Path(configurada).expanduser()]
    else:
        bases = (Path.home() / "Aplicaciones", Path.home() / "Applications", Path("/opt"))
        candidatos = [carpeta for base in bases if base.is_dir()
                      for patron in ("NetLogo*", "netlogo*") for carpeta in base.glob(patron)]
    validos = [p.resolve() for p in candidatos if p.is_dir() and
               (any((p / "lib" / "app").glob("netlogo-*.jar")) or (p / "NetLogo.jar").is_file())]
    if not validos:
        detalle = str(configurada) if configurada is not None else "sin ruta configurada"
        raise ErrorNetLogo(f"NetLogo no está disponible ({detalle}). Indique NETLOGO_HOME o una ruta válida.")
    if len(validos) > 1:
        raise ErrorNetLogo("Hay varias instalaciones de NetLogo; seleccione una con NETLOGO_HOME.")
    return validos[0]


def preparar_envio(experimento) -> dict:
    """Copia solo para transporte las mismas series que ya calculó Python."""
    parametros = experimento.parametros
    campos = ("p0", "tasa", "sigma", "dt", "horizonte", "semilla", "precision")
    envio = {"parametros": [[campo, str(getattr(parametros, campo))] for campo in campos],
             "escenario": experimento.escenario, "series": [], "observaciones": []}
    if not 1 <= len(experimento.series) <= 4:
        raise ErrorNetLogo("Envíe de una a cuatro series calculadas.")
    total = len(experimento.observaciones)
    for serie in experimento.series:
        if not serie.tiempos or len(serie.tiempos) != len(serie.poblaciones):
            raise ErrorNetLogo("Tiempos y poblaciones deben tener la misma longitud positiva.")
        total += len(serie.tiempos)
        if total > MAX_PUNTOS_NETLOGO:
            raise ErrorNetLogo(f"NetLogo admite hasta {MAX_PUNTOS_NETLOGO} puntos por envío.")
        tiempos = [numero_visual(t) for t in serie.tiempos]
        if any(b <= a for a, b in zip(tiempos, tiempos[1:])):
            raise ErrorNetLogo("La precisión double de NetLogo fusionaría tiempos distintos.")
        envio["series"].append({"nombre": serie.nombre, "tiempos": tiempos,
                               "poblaciones": [numero_visual(p) for p in serie.poblaciones]})
    envio["observaciones"] = [[i, numero_visual(p)] for i, p in enumerate(experimento.observaciones)]
    return envio


class PuenteNetLogo:
    """Ejecuta pyNetLogo en un subproceso limitado y comprueba el retorno real."""

    def enviar(self, experimento, netlogo_home: str | Path | None = None, *,
               gui: bool = False, timeout: float = 90,
               salida_plot: str | Path | None = None,
               salida_interfaz: str | Path | None = None,
               segundos_vista: float = 5,
               modelo: str | Path = MODELO_PREDEFINIDO,
               jvm_path: str | Path | None = None) -> InformeNetLogo:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 300:
            raise ErrorNetLogo("El tiempo máximo de NetLogo debe estar entre 0 y 300 segundos.")
        if not isinstance(gui, bool):
            raise ErrorNetLogo("gui debe ser un valor booleano.")
        if gui and (isinstance(segundos_vista, bool) or not isinstance(segundos_vista, (int, float)) or not math.isfinite(segundos_vista) or not 5 <= segundos_vista <= 30):
            raise ErrorNetLogo("La ventana NetLogo puede permanecer abierta entre 5 y 30 segundos.")
        if salida_interfaz is not None and not gui:
            raise ErrorNetLogo("La captura de interfaz necesita gui=True y un escritorio gráfico.")
        instalacion = localizar_netlogo(netlogo_home)
        archivo_modelo = Path(modelo).expanduser().resolve()
        if not archivo_modelo.is_file():
            raise ErrorNetLogo(f"No existe el modelo NetLogo: {archivo_modelo}")
        if gui and sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            raise ErrorNetLogo("No hay escritorio gráfico; use NetLogo sin ventana (gui=False).")
        envio = preparar_envio(experimento)
        archivo_plot = Path(salida_plot).expanduser().resolve() if salida_plot is not None else None
        archivo_interfaz = Path(salida_interfaz).expanduser().resolve() if salida_interfaz is not None else None
        for archivo in (archivo_plot, archivo_interfaz):
            if archivo is not None and archivo.exists():
                raise ErrorNetLogo(f"El archivo de NetLogo ya existe: {archivo}; elija otra ruta.")
            if archivo is not None and not archivo.parent.is_dir():
                raise ErrorNetLogo(f"No existe la carpeta de salida de NetLogo: {archivo.parent}")
        envio.update(netlogo_home=str(instalacion), modelo=str(archivo_modelo), gui=gui,
                     salida_plot=str(archivo_plot) if archivo_plot is not None else None,
                     salida_interfaz=str(archivo_interfaz) if archivo_interfaz is not None else None,
                     segundos_vista=segundos_vista,
                     jvm_path=str(jvm_path) if jvm_path is not None else os.environ.get("NETLOGO_JVM_PATH"))
        worker = Path(__file__).with_name("worker_netlogo.py")
        with tempfile.TemporaryDirectory(prefix="ape02-netlogo-") as temporal:
            resultado = Path(temporal) / "respuesta.json"
            diagnostico = Path(temporal) / "diagnostico.txt"
            with diagnostico.open("w", encoding="utf-8") as registro:
                try:
                    proceso = subprocess.run([sys.executable, str(worker), str(resultado)],
                                             input=json.dumps(envio, ensure_ascii=False), text=True,
                                             encoding="utf-8", stdout=registro, stderr=registro,
                                             timeout=timeout, check=False)
                except subprocess.TimeoutExpired as error:
                    raise ErrorNetLogo(f"NetLogo superó {timeout} segundos; se terminó el proceso auxiliar y su JVM.") from error
                except OSError as error:
                    raise ErrorNetLogo(f"No se pudo iniciar el proceso de NetLogo: {error}") from error
            if not resultado.is_file():
                detalle = diagnostico.read_text(encoding="utf-8", errors="replace")[-4000:]
                raise ErrorNetLogo(f"El proceso NetLogo terminó sin respuesta (código {proceso.returncode}). {detalle}")
            try:
                respuesta = json.loads(resultado.read_text(encoding="utf-8"))
            except (ValueError, OSError) as error:
                raise ErrorNetLogo("El proceso de NetLogo devolvió una respuesta inválida.") from error
        if proceso.returncode != 0 or not respuesta.get("ok"):
            raise ErrorNetLogo(respuesta.get("error", "El proceso de NetLogo terminó con un error."))
        if respuesta["series"] != envio["series"] or respuesta["parametros"] != envio["parametros"] or respuesta["observaciones"] != envio["observaciones"] or respuesta["escenario"] != envio["escenario"]:
            raise ErrorNetLogo("La comprobación de retorno detectó datos diferentes en NetLogo.")
        if respuesta["agentes"] != 0:
            raise ErrorNetLogo("El visualizador no debe crear agentes por habitante.")
        return InformeNetLogo(respuesta["netlogo"], respuesta["java"], respuesta["pynetlogo"],
                              tuple(len(s["tiempos"]) for s in envio["series"]),
                              tuple(s["poblaciones"][-1] for s in envio["series"]),
                              respuesta["agentes"], True, archivo_plot, archivo_interfaz)
