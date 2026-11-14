package ec.edu.simulacion.ape07.modelo;

import java.util.ArrayList;

public final class MedidorRendimiento {
    private final EstimadorPi estimador;

    public MedidorRendimiento(EstimadorPi estimador) {
        this.estimador = estimador;
    }

    public Medicion medir(Parametros parametros, int puntos, int repeticiones) {
        if (repeticiones < 1 || repeticiones > 30) {
            throw new IllegalArgumentException("Las repeticiones deben estar entre 1 y 30.");
        }
        for (int indice = 0; indice < 3; indice++) {
            estimador.estimar(Math.min(puntos, 10000), new GeneradorLCG(parametros));
        }
        var tiempos = new ArrayList<Double>();
        Resultado resultado = null;
        for (int indice = 0; indice < repeticiones; indice++) {
            long inicio = System.nanoTime();
            Resultado actual = estimador.estimar(puntos, new GeneradorLCG(parametros));
            double segundos = (System.nanoTime() - inicio) / 1e9;
            if (resultado != null && !actual.equals(resultado)) {
                throw new IllegalArgumentException("El experimento no fue reproducible.");
            }
            resultado = actual;
            tiempos.add(segundos);
        }
        return new Medicion(resultado, tiempos);
    }
}
