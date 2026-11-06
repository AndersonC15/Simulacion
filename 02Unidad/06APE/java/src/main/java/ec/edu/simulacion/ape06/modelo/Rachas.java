package ec.edu.simulacion.ape06.modelo;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import org.apache.commons.math3.special.Erf;

public final class Rachas implements PruebaEstadistica {
    @Override
    public ResultadoPrueba evaluar(double[] valores, double alfa) {
        PruebaEstadistica.validar(valores, alfa);
        double[] ordenados = valores.clone();
        Arrays.sort(ordenados);
        int n = ordenados.length;
        double mediana = n % 2 == 1 ? ordenados[n / 2] : (ordenados[n / 2 - 1] + ordenados[n / 2]) / 2;
        int n1 = 0, n2 = 0, r = 0;
        Boolean anterior = null;
        for (double valor : valores) {
            if (valor == mediana) continue; // Convencion: eliminar empates, conservando el orden.
            boolean positivo = valor > mediana;
            if (positivo) n1++; else n2++;
            if (anterior == null || positivo != anterior) r++;
            anterior = positivo;
        }
        var detalles = new LinkedHashMap<String, Double>();
        detalles.put("mediana", mediana);
        detalles.put("n1", (double) n1);
        detalles.put("n2", (double) n2);
        detalles.put("rachas", (double) r);
        detalles.put("empates", (double) n - n1 - n2);
        String metodo = "Rachas sobre/bajo mediana; normal bilateral sin correccion de continuidad";
        String h0 = "Orden aleatorio de signos respecto a la mediana";
        if (n1 <= 10 || n2 <= 10) {
            return new ResultadoPrueba("rachas", h0, null, null, null, alfa, metodo, detalles,
                    List.of(), "No se usa la aproximacion normal: n1 y n2 deben ser > 10.");
        }
        double total = (double) n1 + n2;
        double media = 2.0 * n1 * n2 / total + 1;
        double varianza = 2.0 * n1 * n2 * (2.0 * n1 * n2 - total) / (total * total * (total - 1));
        double z = (r - media) / Math.sqrt(varianza);
        detalles.put("media_rachas", media);
        detalles.put("varianza_rachas", varianza);
        return new ResultadoPrueba("rachas", h0, z, Erf.erfc(Math.abs(z) / Math.sqrt(2)),
                Math.sqrt(2) * Erf.erfcInv(alfa), alfa, metodo, detalles, List.of(), "");
    }
}
