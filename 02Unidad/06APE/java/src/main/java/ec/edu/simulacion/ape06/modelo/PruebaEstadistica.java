package ec.edu.simulacion.ape06.modelo;

/** Strategy: el servicio depende del contrato, no de una prueba concreta. */
public interface PruebaEstadistica {
    ResultadoPrueba evaluar(double[] valores, double alfa);

    static void validar(double[] valores, double alfa) {
        if (valores.length == 0) throw new IllegalArgumentException("La secuencia no puede estar vacia.");
        if (!Double.isFinite(alfa) || alfa <= 0 || alfa >= 1) {
            throw new IllegalArgumentException("Se requiere 0 < alfa < 1.");
        }
        for (double u : valores) {
            if (!Double.isFinite(u) || u < 0 || u >= 1) {
                throw new IllegalArgumentException("Todos los valores deben ser finitos y estar en [0,1).");
            }
        }
    }
}
