package ec.edu.simulacion.ape06.modelo;

import java.util.Arrays;

public record Medicion(ParametrosLCG parametros, ResultadoPi resultado, double[] segundos) {
    public double mediana() {
        double[] ordenados = segundos.clone();
        Arrays.sort(ordenados);
        int n = ordenados.length;
        return n % 2 == 1 ? ordenados[n / 2] : (ordenados[n / 2 - 1] + ordenados[n / 2]) / 2;
    }
    public double minimo() { return Arrays.stream(segundos).min().orElseThrow(); }
}
