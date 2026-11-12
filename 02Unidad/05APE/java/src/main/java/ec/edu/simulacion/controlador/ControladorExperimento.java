package ec.edu.simulacion.controlador;

import ec.edu.simulacion.modelo.AnalizadorPeriodo;
import ec.edu.simulacion.modelo.GeneradorPseudoaleatorio;
import ec.edu.simulacion.modelo.ParametrosLCG;
import ec.edu.simulacion.modelo.ResultadoExperimento;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;

public final class ControladorExperimento {
    private final AnalizadorPeriodo analizador;
    private final VistaExperimento vista;

    public ControladorExperimento(AnalizadorPeriodo analizador, VistaExperimento vista) {
        this.analizador = analizador;
        this.vista = vista;
    }

    public ResultadoExperimento ejecutar(ParametrosLCG parametros,
            GeneradorPseudoaleatorio generador, int cantidad, Path destino) throws IOException {
        if (cantidad < 1 || cantidad > 1_000_000) {
            throw new IllegalArgumentException("La cantidad debe estar entre 1 y 1 000 000.");
        }
        var estados = new ArrayList<Long>(cantidad);
        for (int i = 0; i < cantidad; i++) {
            estados.add(generador.siguiente());
        }
        var resultado = new ResultadoExperimento(parametros, estados,
                analizador.analizar(parametros, estados));
        vista.presentar(resultado, destino);
        return resultado;
    }
}
