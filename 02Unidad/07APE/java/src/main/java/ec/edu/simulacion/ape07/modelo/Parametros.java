package ec.edu.simulacion.ape07.modelo;

public record Parametros(long semilla) {
    public static final long MULTIPLICADOR = 16807;
    public static final long MODULO = 2147483647;

    public Parametros {
        if (semilla < 1 || semilla >= MODULO) {
            throw new IllegalArgumentException("La semilla debe estar entre 1 y 2147483646.");
        }
    }
}
