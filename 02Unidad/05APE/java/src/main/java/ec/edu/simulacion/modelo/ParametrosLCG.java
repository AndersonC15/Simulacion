package ec.edu.simulacion.modelo;

/** Parámetros inmutables del dominio. El alcance admite módulos hasta 2^32. */
public record ParametrosLCG(long a, long c, long m, long semilla) {
    public ParametrosLCG {
        if (m < 1 || m > (1L << 32)) {
            throw new IllegalArgumentException("El módulo debe estar entre 1 y 2^32.");
        }
        if (a < 0 || a >= m || c < 0 || c >= m || semilla < 0 || semilla >= m) {
            throw new IllegalArgumentException("Se requiere 0 <= a, c y semilla < m.");
        }
    }

    public static ParametrosLCG deLaGuia(long semilla) {
        return new ParametrosLCG(1_664_525L, 1_013_904_223L, 1L << 32, semilla);
    }
}

