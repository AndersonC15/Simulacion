package ec.edu.simulacion.ape06.modelo;

import java.util.ArrayList;
import java.util.Map;
import org.apache.commons.math3.distribution.ChiSquaredDistribution;
import org.apache.commons.math3.special.Gamma;

public final class ChiCuadrado implements PruebaEstadistica {
    @Override
    public ResultadoPrueba evaluar(double[] valores, double alfa) {
        PruebaEstadistica.validar(valores, alfa);
        double esperada = valores.length / 10.0;
        if (esperada < 5) throw new IllegalArgumentException("Chi-cuadrado requiere N >= 50 y Ei >= 5.");
        long[] frecuencias = new long[10];
        for (double u : valores) {
            int intervalo = 0;
            while (intervalo < 9 && u >= (intervalo + 1) / 10.0) intervalo++;
            frecuencias[intervalo]++;
        }
        var intervalos = new ArrayList<Intervalo>();
        double estadistico = 0;
        for (int i = 0; i < 10; i++) {
            double diferencia = frecuencias[i] - esperada;
            double aporte = diferencia * diferencia / esperada;
            estadistico += aporte;
            intervalos.add(new Intervalo(i / 10.0, (i + 1) / 10.0, frecuencias[i], esperada, aporte));
        }
        // Q evita restar 1-CDF y perder precision para valores p muy pequenos.
        double valorP = Gamma.regularizedGammaQ(4.5, estadistico / 2.0);
        double critico = new ChiSquaredDistribution(9).inverseCumulativeProbability(1 - alfa);
        return new ResultadoPrueba("chi_cuadrado", "Uniformidad U(0,1)", estadistico, valorP, critico,
                alfa, "Chi-cuadrado con 9 gl; cola superior", Map.of("gl", 9.0), intervalos, "");
    }
}
