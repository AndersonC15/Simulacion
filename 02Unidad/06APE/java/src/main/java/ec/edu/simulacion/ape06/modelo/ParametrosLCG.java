package ec.edu.simulacion.ape06.modelo;

/** Parametros de la recurrencia presentada en la Semana 5. */
public record ParametrosLCG(String nombre, long semilla, long a, long c, long m, String fuente) {
    public ParametrosLCG {
        if (nombre == null || !nombre.matches("[a-z][a-z0-9_]*")) {
            throw new IllegalArgumentException("Nombre invalido: usa minusculas, numeros y guion bajo.");
        }
        if (m < 1 || m > (1L << 53)) {
            throw new IllegalArgumentException("Se requiere 1 <= m <= 2^53 para normalizar sin obtener 1.");
        }
        if (semilla < 0 || semilla >= m || a < 0 || a >= m || c < 0 || c >= m) {
            throw new IllegalArgumentException("Se requiere 0 <= semilla, a, c < m.");
        }
    }
}
