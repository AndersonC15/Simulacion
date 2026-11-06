package ec.edu.simulacion.ape06.infraestructura;

import static ec.edu.simulacion.ape06.infraestructura.Archivos.fila;
import static ec.edu.simulacion.ape06.infraestructura.Archivos.mapa;
import ec.edu.simulacion.ape06.modelo.Analisis;
import ec.edu.simulacion.ape06.modelo.Medicion;
import ec.edu.simulacion.ape06.modelo.ResultadoPrueba;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public final class RepositorioResultados {
    private final Path directorio;

    public RepositorioResultados(Path directorio) throws IOException {
        this.directorio = directorio;
        Files.createDirectories(directorio);
    }

    public void entorno(String comando) throws IOException {
        Archivos.json(directorio.resolve("entorno_" + comando + ".json"), mapa(
                "lenguaje", "Java", "version", System.getProperty("java.version"),
                "sistema", System.getProperty("os.name") + " " + System.getProperty("os.version"),
                "comando", comando, "reloj", "System.nanoTime", "unidad_tiempo", "segundos"));
    }

    public Path guardarAnalisis(Analisis analisis) throws IOException {
        var muestra = analisis.muestra();
        Path carpeta = directorio.resolve(muestra.parametros().nombre());
        Files.createDirectories(carpeta);
        int n = muestra.valores().length;
        try (var escritor = Files.newBufferedWriter(carpeta.resolve("secuencia.csv"), StandardCharsets.UTF_8)) {
            fila(escritor, "posicion", "estado", "valor");
            for (int i = 0; i < n; i++) fila(escritor, i + 1, muestra.estados()[i], muestra.valores()[i]);
        }
        double[] ordenados = muestra.valores().clone();
        Arrays.sort(ordenados);
        try (var escritor = Files.newBufferedWriter(carpeta.resolve("ks_ordenados.csv"), StandardCharsets.UTF_8)) {
            fila(escritor, "i", "u_ordenado", "fn_derecha", "fn_izquierda", "d_mas", "d_menos");
            for (int i = 0; i < n; i++) {
                fila(escritor, i + 1, ordenados[i], (i + 1.0) / n, (double) i / n,
                        (i + 1.0) / n - ordenados[i], ordenados[i] - (double) i / n);
            }
        }
        var chi = analisis.pruebas().stream().filter(p -> p.nombre().equals("chi_cuadrado")).findFirst().orElseThrow();
        try (var escritor = Files.newBufferedWriter(carpeta.resolve("frecuencias.csv"), StandardCharsets.UTF_8)) {
            fila(escritor, "inferior", "superior", "observada", "esperada", "aporte");
            for (var intervalo : chi.intervalos()) {
                fila(escritor, intervalo.inferior(), intervalo.superior(), intervalo.observada(), intervalo.esperada(), intervalo.aporte());
            }
        }
        Archivos.json(carpeta.resolve("analisis.json"), mapa("lenguaje", "Java", "parametros", muestra.parametros(),
                "n", n, "resumen", mapa("minimo", analisis.minimo(), "maximo", analisis.maximo(),
                        "media", analisis.media(), "varianza", analisis.varianza(), "distintos", analisis.distintos(),
                        "periodo_observado", analisis.periodoObservado()),
                "pruebas", analisis.pruebas().stream().map(this::datosPrueba).toList()));
        return carpeta;
    }

    private Map<String, Object> datosPrueba(ResultadoPrueba p) {
        return mapa("nombre", p.nombre(), "hipotesis", p.hipotesis(), "estadistico", p.estadistico(),
                "valor_p", p.valorP(), "critico", p.critico(), "alfa", p.alfa(), "metodo", p.metodo(),
                "detalles", p.detalles(), "intervalos", p.intervalos(), "nota", p.nota(), "decision", p.decision());
    }

    public void guardarResumen(List<Analisis> analisis) throws IOException {
        try (var escritor = Files.newBufferedWriter(directorio.resolve("resumen.csv"), StandardCharsets.UTF_8)) {
            fila(escritor, "generador", "n", "prueba", "estadistico", "valor_p", "critico", "alfa", "decision", "metodo");
            for (var a : analisis) for (var p : a.pruebas()) {
                fila(escritor, a.muestra().parametros().nombre(), a.muestra().valores().length, p.nombre(),
                        p.estadistico(), p.valorP(), p.critico(), p.alfa(), p.decision(), p.metodo());
            }
        }
    }

    public void guardarMediciones(List<Medicion> mediciones) throws IOException {
        try (var escritor = Files.newBufferedWriter(directorio.resolve("benchmark.csv"), StandardCharsets.UTF_8);
             var tiempos = Files.newBufferedWriter(directorio.resolve("tiempos.csv"), StandardCharsets.UTF_8)) {
            fila(escritor, "generador", "n", "dentro", "pi_estimado", "error_absoluto", "tiempo_mediana_s", "tiempo_minimo_s", "repeticiones", "valores_lcg");
            fila(tiempos, "generador", "n", "repeticion", "segundos");
            for (var m : mediciones) {
                var r = m.resultado();
                fila(escritor, m.parametros().nombre(), r.puntos(), r.dentro(), r.estimacion(), r.errorAbsoluto(),
                        m.mediana(), m.minimo(), m.segundos().length, 2L * r.puntos());
                for (int i = 0; i < m.segundos().length; i++) {
                    fila(tiempos, m.parametros().nombre(), r.puntos(), i + 1, m.segundos()[i]);
                }
            }
        }
    }
}
