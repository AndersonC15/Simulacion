package ec.edu.simulacion.modelo;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.List;

public final class AnalizadorPeriodo {
    public AnalisisPeriodo analizar(ParametrosLCG p, List<Long> estados) {
        boolean coprimos = BigInteger.valueOf(p.c()).gcd(BigInteger.valueOf(p.m()))
                .equals(BigInteger.ONE);
        boolean factores = factoresDividen(p.a() - 1, p.m());
        boolean reglaCuatro = p.m() % 4 != 0 || (p.a() - 1) % 4 == 0;
        Long teorico = coprimos && factores && reglaCuatro ? p.m() : null;
        var vistos = new HashMap<Long, Integer>();
        vistos.put(p.semilla(), 0);
        for (int i = 0; i < estados.size(); i++) {
            int indice = i + 1;
            Integer inicio = vistos.putIfAbsent(estados.get(i), indice);
            if (inicio != null) {
                return new AnalisisPeriodo(coprimos, factores, reglaCuatro,
                        teorico, inicio, indice - inicio);
            }
        }
        return new AnalisisPeriodo(coprimos, factores, reglaCuatro, teorico, null, null);
    }

    private boolean factoresDividen(long anterior, long modulo) {
        long restante = modulo;
        for (long divisor = 2; divisor * divisor <= restante; divisor++) {
            if (restante % divisor == 0) {
                if (anterior % divisor != 0) {
                    return false;
                }
                while (restante % divisor == 0) {
                    restante /= divisor;
                }
            }
        }
        return restante <= 1 || anterior % restante == 0;
    }
}

