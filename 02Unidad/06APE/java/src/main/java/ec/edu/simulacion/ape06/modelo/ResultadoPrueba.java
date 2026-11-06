package ec.edu.simulacion.ape06.modelo;

import java.util.List;
import java.util.Map;

public record ResultadoPrueba(String nombre, String hipotesis, Double estadistico, Double valorP,
                              Double critico, double alfa, String metodo, Map<String, Double> detalles,
                              List<Intervalo> intervalos, String nota) {
    public ResultadoPrueba {
        detalles = Map.copyOf(detalles);
        intervalos = List.copyOf(intervalos);
    }

    public String decision() {
        if (valorP == null) return "No aplicable";
        return valorP < alfa ? "Se rechaza H0" : "No se rechaza H0";
    }
}
