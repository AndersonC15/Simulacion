package ec.edu.simulacion.ape06.modelo;

/** Distribucion limite bilateral: dos series equivalentes para evitar cancelacion.
 * Se contrasta con scipy.stats.kstwobign; no es una distribucion exacta para N finito.
 */
public final class DistribucionKolmogorov {
    private DistribucionKolmogorov() { }

    public static double supervivencia(double t) {
        if (Double.isNaN(t) || t < 0) throw new IllegalArgumentException("t debe ser no negativo.");
        if (t == 0) return 1;
        if (Double.isInfinite(t)) return 0;
        double suma = 0;
        for (int k = 1; k <= 100; k++) {
            double termino;
            if (t < 1.18) {
                double impar = 2.0 * k - 1;
                termino = Math.exp(-impar * impar * Math.PI * Math.PI / (8 * t * t));
                suma += termino;
            } else {
                termino = Math.exp(-2.0 * k * k * t * t);
                suma += k % 2 == 1 ? termino : -termino;
            }
            if (termino == 0 || termino < 1e-16 * Math.abs(suma)) {
                double p = t < 1.18 ? 1 - Math.sqrt(2 * Math.PI) * suma / t : 2 * suma;
                return Math.max(0, Math.min(1, p));
            }
        }
        throw new ArithmeticException("La serie de Kolmogorov no convergio.");
    }

    public static double critico(double alfa) {
        double inferior = 0;
        double superior = 32;
        for (int i = 0; i < 100; i++) {
            double medio = (inferior + superior) / 2;
            if (supervivencia(medio) > alfa) inferior = medio;
            else superior = medio;
        }
        return (inferior + superior) / 2;
    }
}
