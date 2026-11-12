package ec.edu.simulacion.modelo;

import java.util.List;

public record ResultadoExperimento(
        ParametrosLCG parametros, List<Long> estados, AnalisisPeriodo periodo) {
    public ResultadoExperimento {
        estados = List.copyOf(estados);
    }

    public double normalizado(int indice) {
        return estados.get(indice) / (double) parametros.m();
    }
}

