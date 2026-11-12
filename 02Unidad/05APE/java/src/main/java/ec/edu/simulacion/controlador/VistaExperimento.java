package ec.edu.simulacion.controlador;

import ec.edu.simulacion.modelo.ResultadoExperimento;
import java.io.IOException;
import java.nio.file.Path;

@FunctionalInterface
public interface VistaExperimento {
    void presentar(ResultadoExperimento resultado, Path destino) throws IOException;
}

