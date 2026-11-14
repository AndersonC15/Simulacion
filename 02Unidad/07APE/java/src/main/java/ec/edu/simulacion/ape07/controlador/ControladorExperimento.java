package ec.edu.simulacion.ape07.controlador;

import ec.edu.simulacion.ape07.modelo.*;
import ec.edu.simulacion.ape07.vista.VistaResultados;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class ControladorExperimento {
    private final MedidorRendimiento medidor;
    private final VistaResultados vista;

    public ControladorExperimento(MedidorRendimiento medidor, VistaResultados vista) {
        this.medidor = medidor;
        this.vista = vista;
    }

    public List<Medicion> ejecutar(Parametros parametros, int[] tamanos, int repeticiones, Path salida)
            throws IOException {
        if (tamanos.length == 0) {
            throw new IllegalArgumentException("Debe indicar al menos un tamaño.");
        }
        int anterior = 0;
        for (int puntos : tamanos) {
            if (puntos <= anterior || puntos > 1000000) {
                throw new IllegalArgumentException("Los tamaños deben estar ordenados, sin duplicados, entre 1 y 1000000.");
            }
            anterior = puntos;
        }
        var mediciones = new ArrayList<Medicion>();
        for (int puntos : tamanos) {
            mediciones.add(medidor.medir(parametros, puntos, repeticiones));
        }
        vista.guardar(parametros, mediciones, salida);
        vista.mostrar(mediciones, salida);
        return List.copyOf(mediciones);
    }
}
