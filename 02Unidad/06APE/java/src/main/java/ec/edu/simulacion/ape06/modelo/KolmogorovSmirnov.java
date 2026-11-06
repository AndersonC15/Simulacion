package ec.edu.simulacion.ape06.modelo;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

public final class KolmogorovSmirnov implements PruebaEstadistica {
    @Override
    public ResultadoPrueba evaluar(double[] valores, double alfa) {
        PruebaEstadistica.validar(valores, alfa);
        double[] ordenados = valores.clone();
        Arrays.sort(ordenados);
        int n = ordenados.length;
        double dMas = 0;
        double dMenos = 0;
        for (int i = 0; i < n; i++) {
            dMas = Math.max(dMas, (i + 1.0) / n - ordenados[i]);
            dMenos = Math.max(dMenos, ordenados[i] - (double) i / n);
        }
        double d = Math.max(dMas, dMenos);
        return new ResultadoPrueba("ks", "Uniformidad U(0,1)", d,
                DistribucionKolmogorov.supervivencia(Math.sqrt(n) * d),
                DistribucionKolmogorov.critico(alfa) / Math.sqrt(n), alfa,
                "KS bilateral, distribucion limite de Kolmogorov (asintotico)",
                Map.of("d_mas", dMas, "d_menos", dMenos, "critico_005_diapositiva", 1.36 / Math.sqrt(n)),
                List.of(), "El valor p es aproximado. Las diapositivas recomiendan N >= 35.");
    }
}
