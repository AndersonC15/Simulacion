package ec.edu.simulacion.ape06.modelo;

public final class MedidorRendimiento {
    private final EstimadorPi estimador;
    // Mantiene un resultado observable para que el calentamiento no sea trabajo descartable.
    private static volatile double ultimoCalentamiento;

    public MedidorRendimiento(EstimadorPi estimador) { this.estimador = estimador; }

    public Medicion medir(ParametrosLCG parametros, int puntos, int repeticiones) {
        if (repeticiones < 1) throw new IllegalArgumentException("Se necesita al menos una repeticion.");
        for (int i = 0; i < 3; i++) {
            ultimoCalentamiento = estimador.estimar(parametros, Math.min(puntos, 10000)).estimacion();
        }
        double[] tiempos = new double[repeticiones];
        ResultadoPi resultado = null;
        for (int i = 0; i < repeticiones; i++) {
            long inicio = System.nanoTime();
            resultado = estimador.estimar(parametros, puntos);
            tiempos[i] = (System.nanoTime() - inicio) / 1_000_000_000.0;
        }
        return new Medicion(parametros, resultado, tiempos);
    }
}
