package ec.edu.simulacion.ape07.modelo;

import java.util.List;

public record Medicion(Resultado resultado, List<Double> segundos) {
    public Medicion {
        segundos = List.copyOf(segundos);
    }

    public double mediana() {
        var ordenados = segundos.stream().sorted().toList();
        int centro = ordenados.size() / 2;
        return ordenados.size() % 2 == 1 ? ordenados.get(centro)
                : (ordenados.get(centro - 1) + ordenados.get(centro)) / 2.0;
    }
}
