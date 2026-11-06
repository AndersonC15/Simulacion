package ec.edu.simulacion.ape06.infraestructura;

import com.fasterxml.jackson.databind.ObjectMapper;
import ec.edu.simulacion.ape06.modelo.ParametrosLCG;
import java.io.IOException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.csv.CSVFormat;

public final class Archivos {
    private Archivos() { }

    public static List<ParametrosLCG> leerParametros(Path ruta, List<String> nombres) throws IOException {
        var parametros = new LinkedHashMap<String, ParametrosLCG>();
        try (var lector = Files.newBufferedReader(ruta, StandardCharsets.UTF_8);
             var csv = CSVFormat.DEFAULT.builder().setHeader().setSkipHeaderRecord(true).get().parse(lector)) {
            for (var fila : csv) {
                var p = new ParametrosLCG(fila.get("nombre"), Long.parseLong(fila.get("semilla")),
                        Long.parseLong(fila.get("a")), Long.parseLong(fila.get("c")),
                        Long.parseLong(fila.get("m")), fila.get("fuente"));
                if (parametros.putIfAbsent(p.nombre(), p) != null) {
                    throw new IllegalArgumentException("Generador duplicado: " + p.nombre());
                }
            }
        }
        if (parametros.isEmpty()) throw new IllegalArgumentException("Configuracion vacia.");
        if (nombres.isEmpty() || nombres.stream().distinct().count() != nombres.size()) {
            throw new IllegalArgumentException("Selecciona generadores sin nombres duplicados.");
        }
        var seleccionados = new ArrayList<ParametrosLCG>();
        for (String nombre : nombres) {
            if (!parametros.containsKey(nombre)) throw new IllegalArgumentException("Generador desconocido: " + nombre);
            seleccionados.add(parametros.get(nombre));
        }
        return List.copyOf(seleccionados);
    }

    public static void json(Path ruta, Object contenido) throws IOException {
        Files.createDirectories(ruta.toAbsolutePath().getParent());
        new ObjectMapper().writerWithDefaultPrettyPrinter().writeValue(ruta.toFile(), contenido);
    }

    public static Map<String, Object> mapa(Object... pares) {
        var resultado = new LinkedHashMap<String, Object>();
        for (int i = 0; i < pares.length; i += 2) resultado.put((String) pares[i], pares[i + 1]);
        return resultado;
    }

    public static void fila(Writer escritor, Object... campos) throws IOException {
        for (int i = 0; i < campos.length; i++) {
            if (i > 0) escritor.write(',');
            String texto = campos[i] == null ? "" : campos[i].toString();
            if (texto.contains(",") || texto.contains("\"") || texto.contains("\n") || texto.contains("\r")) {
                escritor.write("\"" + texto.replace("\"", "\"\"") + "\"");
            } else escritor.write(texto);
        }
        escritor.write('\n');
    }
}
