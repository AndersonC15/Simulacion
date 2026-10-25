"""Proceso auxiliar privado: una sesión pyNetLogo y una JVM por invocación."""

import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time


def literal(valor):
    """Solo valores de transporte; nunca se concatena código del usuario."""
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    if isinstance(valor, list):
        return "[" + " ".join(literal(elemento) for elemento in valor) + "]"
    return repr(valor)


def ejecutar(solicitud):
    import jpype
    import pynetlogo

    ruta = Path(solicitud["netlogo_home"])
    jvm = solicitud["jvm_path"]
    if not jvm:
        posibles = [ruta / "lib/runtime/lib/server/libjvm.so",
                    ruta / "runtime/Contents/Home/lib/server/libjvm.dylib",
                    ruta / "runtime/bin/server/jvm.dll"]
        jvm = next((str(p) for p in posibles if p.is_file()), None)
    argumentos = ["-Xmx768m", "-Dfile.encoding=UTF-8",
                  f"-Dnetlogo.docs.dir={ruta}",
                  f"-Dnetlogo.models.dir={ruta / 'models'}"]
    if not solicitud["gui"]:
        argumentos.append("-Djava.awt.headless=true")
    enlace = None
    try:
        # 0.5.2 usa jvmargs; se comprobó la firma instalada, no la documentación de otra versión.
        enlace = pynetlogo.NetLogoLink(gui=solicitud["gui"], netlogo_home=str(ruta),
                                      jvm_path=jvm, jvmargs=argumentos)
        enlace.load_model(solicitud["modelo"])
        enlace.command("iniciar")
        enlace.command("set parametros-python " + literal(solicitud["parametros"]))
        enlace.command("set escenario-python " + literal(solicitud["escenario"]))
        enlace.command("set nombres-python " + literal([s["nombre"] for s in solicitud["series"]]))
        enlace.command("set tiempos-python " + literal([s["tiempos"] for s in solicitud["series"]]))
        enlace.command("set poblaciones-python " + literal([s["poblaciones"] for s in solicitud["series"]]))
        enlace.command("set observaciones-python " + literal(solicitud["observaciones"]))
        enlace.command("representar")
        nombres = [str(n) for n in enlace.report("nombres-python")]
        # 0.5.2 convierte listas anidadas con np.asarray; las mallas de Euler
        # tienen otra longitud. Se consultan por separado para evitar ese fallo.
        tiempos = [[float(v) for v in enlace.report(f"item {i} tiempos-python")] for i in range(len(nombres))]
        poblaciones = [[float(v) for v in enlace.report(f"item {i} poblaciones-python")] for i in range(len(nombres))]
        salida = {"ok": True, "netlogo": str(enlace.report("netlogo-version")),
                  "java": str(jpype.java.lang.System.getProperty("java.version")),
                  "pynetlogo": importlib.metadata.version("pynetlogo"),
                  "escenario": str(enlace.report("escenario-python")),
                  "series": [{"nombre": str(n), "tiempos": list(t), "poblaciones": list(p)}
                             for n, t, p in zip(nombres, tiempos, poblaciones)],
                  "parametros": [[str(v) for v in enlace.report(f"item {i} parametros-python")]
                                 for i in range(len(solicitud["parametros"]))],
                  "observaciones": [[float(v) for v in enlace.report(f"item {i} observaciones-python")]
                                    for i in range(len(solicitud["observaciones"]))],
                  "agentes": int(enlace.report("count turtles"))}
        if solicitud["salida_plot"]:
            enlace.command("export-plot \"Comparación poblacional\" " + literal(solicitud["salida_plot"]))
        if solicitud["gui"]:
            # Permite inspeccionar la ventana sin dejar una JVM huérfana.
            time.sleep(0.3)
            if solicitud["salida_interfaz"]:
                enlace.command("export-interface " + literal(solicitud["salida_interfaz"]))
            time.sleep(solicitud["segundos_vista"])
        return salida
    except (pynetlogo.NetLogoException, jpype.JException) as error:
        raise RuntimeError(f"La API de NetLogo rechazó el modelo o los datos: {error}") from error
    finally:
        if not solicitud["gui"]:
            try:
                if enlace is not None:
                    enlace.kill_workspace()
            except (pynetlogo.NetLogoException, jpype.JException) as error:
                raise RuntimeError(f"No se pudo cerrar el espacio NetLogo: {error}") from error
            finally:
                if jpype.isJVMStarted():
                    jpype.shutdownJVM()


def main():
    archivo_respuesta = Path(sys.argv[1])
    cierre_de_proceso = False
    try:
        solicitud = json.loads(sys.stdin.read())
        cierre_de_proceso = solicitud["gui"]
        respuesta = ejecutar(solicitud)
    except (ImportError, OSError, RuntimeError, ValueError, TypeError) as error:
        # Frontera del proceso: clasifica los fallos esperados y conserva su mensaje.
        respuesta = {"ok": False, "error": f"No se pudo ejecutar NetLogo ({type(error).__name__}): {error}"}
    archivo_respuesta.write_text(json.dumps(respuesta, ensure_ascii=False), encoding="utf-8")
    if cierre_de_proceso:
        # Probado: pyNetLogo 0.5.2 puede bloquearse en Frame.dispose() de la GUI.
        # La respuesta ya está cerrada en disco; terminar este proceso aislado
        # libera la JVM y todas sus ventanas, sin reiniciarla ni afectar Python.
        os._exit(0 if respuesta["ok"] else 1)
    return 0 if respuesta["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
