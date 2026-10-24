package sir.controller;

import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;
import sir.model.SimulacionSIR;
import sir.view.GraficaSIR;
import sir.view.VistaConsola;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ControladorSIR {

    public static final String CSV_POR_DEFECTO = "resultados_java.csv";
    public static final String PNG_POR_DEFECTO = "grafica_sir_java.png";
    public static final String ENCABEZADO_CSV = "tiempo,susceptibles,infectados,recuperados";

    private final ParametrosSIR parametros;
    private final String rutaCsv;
    private final boolean mostrarGrafica;
    private final long semilla;
    private final VistaConsola vista;
    private final SimulacionSIR simulacion;
    private final List<ResultadoPaso> historial;

    public ControladorSIR(ParametrosSIR parametros, Long semilla, boolean mostrarGrafica, String rutaCsv) {
        this.parametros = parametros;
        this.semilla = (semilla != null) ? semilla.longValue() : new SecureRandom().nextLong();
        this.mostrarGrafica = mostrarGrafica;
        this.rutaCsv = (rutaCsv != null) ? rutaCsv : CSV_POR_DEFECTO;
        this.vista = new VistaConsola();
        this.simulacion = new SimulacionSIR(parametros, this.semilla);
        this.historial = new ArrayList<ResultadoPaso>();
    }

    public void ejecutar() {
        vista.mostrarInicio(parametros, semilla);

        for (int tiempo = 0; tiempo <= parametros.getTiempoSimulacion(); tiempo++) {
            ResultadoPaso resultado = simulacion.contarPoblacion();
            historial.add(resultado);
            vista.mostrarPaso(resultado);

            if (tiempo < parametros.getTiempoSimulacion()) {
                simulacion.paso();
            }
        }

        vista.mostrarResumen(parametros, historial);
        exportarCsv(rutaCsv);
        generarGrafica();
    }

    public File exportarCsv(String ruta) {
        File archivo = new File(ruta);
        try (PrintWriter escritor = new PrintWriter(archivo, "UTF-8")) {
            escritor.print(ENCABEZADO_CSV + "\n");
            for (ResultadoPaso resultado : historial) {
                escritor.print(resultado.aCsv() + "\n");
            }
        } catch (IOException e) {
            vista.mostrarMensaje("Error al escribir el CSV: " + e.getMessage());
            return null;
        }
        vista.mostrarMensaje("Datos exportados a: " + archivo.getAbsolutePath());
        return archivo;
    }

    private void generarGrafica() {
        GraficaSIR grafica = new GraficaSIR(historial);
        try {
            File imagen = grafica.guardarImagen(PNG_POR_DEFECTO);
            vista.mostrarMensaje("Grafica guardada en: " + imagen.getAbsolutePath());
        } catch (IOException e) {
            vista.mostrarMensaje("No se pudo guardar la grafica: " + e.getMessage());
        }
        if (mostrarGrafica) {
            grafica.mostrarVentana("Modelo SIR - Java");
        }
    }

    public long getSemilla() {
        return semilla;
    }

    public List<ResultadoPaso> getHistorial() {
        return Collections.unmodifiableList(historial);
    }
}
