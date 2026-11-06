"""El controlador coordina el modelo, las vistas y el repositorio."""

from ape06.infraestructura.archivos import RepositorioResultados
from ape06.modelo.datos import ParametrosLCG
from ape06.modelo.experimentos import MedidorRendimiento, ServicioSimulacion
from ape06.vista.consola import VistaConsola
from ape06.vista.graficas import VistaGraficas


class ControladorSimulacion:
    def __init__(self, servicio: ServicioSimulacion, medidor: MedidorRendimiento,
                 consola: VistaConsola, graficas: VistaGraficas, repositorio: RepositorioResultados) -> None:
        self._servicio = servicio
        self._medidor = medidor
        self._consola = consola
        self._graficas = graficas
        self._repositorio = repositorio

    def ejecutar(self, parametros: tuple[ParametrosLCG, ...], n: int, alfa: float) -> None:
        resultados = []
        for p in parametros:
            analisis = self._servicio.analizar(p, n, alfa)
            directorio = self._repositorio.guardar_analisis(analisis)
            self._graficas.guardar(analisis, directorio)
            self._consola.mostrar_analisis(analisis)
            resultados.append(analisis)
        self._repositorio.guardar_resumen(tuple(resultados))
        self._repositorio.entorno("ejecutar")

    def benchmark(self, parametros: tuple[ParametrosLCG, ...], tamanos: tuple[int, ...], repeticiones: int) -> None:
        resultados = []
        for p in parametros:
            for n in tamanos:
                medicion = self._medidor.medir(p, n, repeticiones)
                self._consola.mostrar_medicion(medicion)
                resultados.append(medicion)
        self._repositorio.guardar_mediciones(tuple(resultados))
        self._repositorio.entorno("benchmark")
