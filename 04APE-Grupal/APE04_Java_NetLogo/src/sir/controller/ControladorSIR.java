package sir.controller;

import sir.io.ExportadorResultados;
import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;
import sir.model.SimulacionSIR;
import sir.view.GraficaSIR;
import sir.view.VistaConsola;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/** Coordina modelo, vistas y exportacion. No calcula contagios. */
public final class ControladorSIR {
    public static final String CSV_POR_DEFECTO = "netlogo/java_simulado.csv";
    public static final String PNG_POR_DEFECTO = "resultados/grafica_sir_java.png";

    private final SimulacionSIR simulacion;
    private final VistaConsola vista;
    private final ExportadorResultados exportador;
    private final Path rutaCsv;
    private final Path rutaPng;
    private final boolean mostrarGrafica;
    private final List<ResultadoPaso> historial = new ArrayList<ResultadoPaso>();

    public ControladorSIR(SimulacionSIR simulacion, VistaConsola vista,
                         ExportadorResultados exportador, Path rutaCsv,
                         Path rutaPng, boolean mostrarGrafica) {
        this.simulacion = simulacion;
        this.vista = vista;
        this.exportador = exportador;
        this.rutaCsv = rutaCsv;
        this.rutaPng = rutaPng;
        this.mostrarGrafica = mostrarGrafica;
    }

    public void ejecutar() throws IOException {
        ParametrosSIR parametros = simulacion.getParametros();
        vista.mostrarInicio(parametros, simulacion.getSemilla());
        long inicio = System.nanoTime();
        historial.add(simulacion.contarPoblacion());
        for (int tiempo = 1; tiempo <= parametros.getTiempoSimulacion(); tiempo++) {
            historial.add(simulacion.paso());
        }
        double milisegundos = (System.nanoTime() - inicio) / 1_000_000.0;
        for (ResultadoPaso paso : historial) {
            vista.mostrarPaso(paso);
        }
        vista.mostrarResumen(parametros, historial);
        vista.mostrarMensaje(String.format(Locale.ROOT,
                "Tiempo del modelo y registro (sin grafica/CSV/consola): %.3f ms", milisegundos));
        exportador.exportar(historial, rutaCsv);
        vista.mostrarMensaje("CSV generado: " + rutaCsv);
        Path padre = rutaPng.toAbsolutePath().getParent();
        if (padre != null) {
            Files.createDirectories(padre);
        }
        GraficaSIR grafica = new GraficaSIR(historial);
        grafica.guardarImagen(rutaPng.toString());
        vista.mostrarMensaje("PNG generado: " + rutaPng);
        if (mostrarGrafica) {
            grafica.mostrarVentana("APE04 - Modelo SIR en Java");
        }
    }

    public List<ResultadoPaso> getHistorial() {
        return Collections.unmodifiableList(historial);
    }
}
