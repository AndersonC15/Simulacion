package ec.edu.simulacion.vista;

import ec.edu.simulacion.controlador.VistaExperimento;
import ec.edu.simulacion.modelo.ResultadoExperimento;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

public final class VistaArchivosConsola implements VistaExperimento {
    @Override
    public void presentar(ResultadoExperimento resultado, Path destino) throws IOException {
        Files.createDirectories(destino);
        String nombre = "semilla_" + resultado.parametros().semilla();
        escribirCsv(resultado, destino.resolve(nombre + ".csv"));
        escribirResumen(resultado, destino.resolve(nombre + ".json"));
        new GraficaSecuencia().guardar(resultado, destino.resolve(nombre + ".png"));
        System.out.printf("%nJava | semilla=%d | n=%d%n",
                resultado.parametros().semilla(), resultado.estados().size());
        System.out.printf("%4s %12s %34s%n", "n", "Xn", "Un (decimal exacto)");
        for (int i = 0; i < Math.min(20, resultado.estados().size()); i++) {
            System.out.printf(Locale.ROOT, "%4d %12d %34s%n",
                    i + 1, resultado.estados().get(i),
                    new BigDecimal(resultado.normalizado(i)).toPlainString());
        }
        System.out.println("Período teórico (Hull–Dobell): " + resultado.periodo().periodoTeorico());
        System.out.println("Período observado: " + (resultado.periodo().periodoObservado() == null
                ? "no detectado en la muestra" : resultado.periodo().periodoObservado()));
        System.out.println("Archivos: " + destino.resolve(nombre) + ".csv / .json / .png");
    }

    private void escribirCsv(ResultadoExperimento resultado, Path destino) throws IOException {
        try (var escritor = Files.newBufferedWriter(destino, StandardCharsets.UTF_8)) {
            escritor.write("n,x,u\n");
            for (int i = 0; i < resultado.estados().size(); i++) {
                escritor.write((i + 1) + "," + resultado.estados().get(i)
                        + "," + Double.toString(resultado.normalizado(i)) + "\n");
            }
        }
    }

    private void escribirResumen(ResultadoExperimento r, Path destino) throws IOException {
        var p = r.parametros();
        var periodo = r.periodo();
        int cantidad = r.estados().size();
        double minimo = Double.POSITIVE_INFINITY;
        double maximo = Double.NEGATIVE_INFINITY;
        double suma = 0;
        for (int i = 0; i < cantidad; i++) {
            double valor = r.normalizado(i);
            minimo = Math.min(minimo, valor);
            maximo = Math.max(maximo, valor);
            suma += valor;
        }
        double media = suma / cantidad;
        double cuadrados = 0;
        for (int i = 0; i < cantidad; i++) {
            double diferencia = r.normalizado(i) - media;
            cuadrados += diferencia * diferencia;
        }
        String json = """
                {
                  "lenguaje": "Java",
                  "parametros": {"a": %d, "c": %d, "m": %d, "semilla": %d},
                  "cantidad": %d,
                  "periodo": {
                    "coprimos": %s,
                    "factores_dividen": %s,
                    "regla_cuatro": %s,
                    "periodo_teorico": %s,
                    "preperiodo_observado": %s,
                    "periodo_observado": %s
                  },
                  "estadisticas_descriptivas": {
                    "minimo": %s, "maximo": %s, "media": %s, "varianza_poblacional": %s
                  }
                }
                """.formatted(p.a(), p.c(), p.m(), p.semilla(), cantidad,
                        periodo.coprimos(), periodo.factoresDividen(), periodo.reglaCuatro(),
                        periodo.periodoTeorico(), periodo.preperiodoObservado(), periodo.periodoObservado(),
                        minimo, maximo, media, cuadrados / cantidad);
        Files.writeString(destino, json, StandardCharsets.UTF_8);
    }
}

