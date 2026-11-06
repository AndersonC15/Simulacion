package ec.edu.simulacion.ape06.controlador;

import ec.edu.simulacion.ape06.infraestructura.RepositorioResultados;
import ec.edu.simulacion.ape06.modelo.Analisis;
import ec.edu.simulacion.ape06.modelo.Medicion;
import ec.edu.simulacion.ape06.modelo.MedidorRendimiento;
import ec.edu.simulacion.ape06.modelo.ParametrosLCG;
import ec.edu.simulacion.ape06.modelo.ServicioSimulacion;
import ec.edu.simulacion.ape06.vista.VistaConsola;
import ec.edu.simulacion.ape06.vista.VistaGraficas;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public final class ControladorSimulacion {
    private final ServicioSimulacion servicio;
    private final MedidorRendimiento medidor;
    private final VistaConsola consola;
    private final VistaGraficas graficas;
    private final RepositorioResultados repositorio;

    public ControladorSimulacion(ServicioSimulacion servicio, MedidorRendimiento medidor,
                                 VistaConsola consola, VistaGraficas graficas, RepositorioResultados repositorio) {
        this.servicio = servicio;
        this.medidor = medidor;
        this.consola = consola;
        this.graficas = graficas;
        this.repositorio = repositorio;
    }

    public void ejecutar(List<ParametrosLCG> parametros, int n, double alfa) throws IOException {
        var resultados = new ArrayList<Analisis>();
        for (var p : parametros) {
            var analisis = servicio.analizar(p, n, alfa);
            var carpeta = repositorio.guardarAnalisis(analisis);
            graficas.guardar(analisis, carpeta);
            consola.mostrarAnalisis(analisis);
            resultados.add(analisis);
        }
        repositorio.guardarResumen(resultados);
        repositorio.entorno("ejecutar");
    }

    public void benchmark(List<ParametrosLCG> parametros, List<Integer> tamanos, int repeticiones) throws IOException {
        var mediciones = new ArrayList<Medicion>();
        for (var p : parametros) for (int n : tamanos) {
            var medicion = medidor.medir(p, n, repeticiones);
            consola.mostrarMedicion(medicion);
            mediciones.add(medicion);
        }
        repositorio.guardarMediciones(mediciones);
        repositorio.entorno("benchmark");
    }
}
