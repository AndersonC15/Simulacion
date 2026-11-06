package ec.edu.simulacion.ape06.modelo;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public final class ServicioSimulacion {
    private final List<PruebaEstadistica> pruebas;

    public ServicioSimulacion(List<PruebaEstadistica> pruebas) { this.pruebas = List.copyOf(pruebas); }

    public Analisis analizar(ParametrosLCG parametros, int cantidad, double alfa) {
        if (cantidad < 50) throw new IllegalArgumentException("La practica requiere N >= 50.");
        Muestra muestra = new GeneradorLCG(parametros).generar(cantidad);
        var resultados = pruebas.stream().map(p -> p.evaluar(muestra.valores(), alfa)).toList();
        var vistos = new HashMap<Long, Integer>();
        vistos.put(parametros.semilla(), 0);
        Integer periodo = null;
        for (int i = 0; i < cantidad; i++) {
            Integer anterior = vistos.putIfAbsent(muestra.estados()[i], i + 1);
            if (anterior != null) { periodo = i + 1 - anterior; break; }
        }
        double media = Arrays.stream(muestra.valores()).average().orElseThrow();
        double varianza = Arrays.stream(muestra.valores()).map(u -> (u - media) * (u - media)).average().orElseThrow();
        return new Analisis(muestra, resultados, Arrays.stream(muestra.valores()).min().orElseThrow(),
                Arrays.stream(muestra.valores()).max().orElseThrow(), media, varianza,
                (int) Arrays.stream(muestra.estados()).distinct().count(), periodo);
    }
}
