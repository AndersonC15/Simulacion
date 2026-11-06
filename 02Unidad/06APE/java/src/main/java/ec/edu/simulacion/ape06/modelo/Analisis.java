package ec.edu.simulacion.ape06.modelo;

import java.util.List;

public record Analisis(Muestra muestra, List<ResultadoPrueba> pruebas, double minimo, double maximo,
                       double media, double varianza, int distintos, Integer periodoObservado) {
    public Analisis { pruebas = List.copyOf(pruebas); }
}
