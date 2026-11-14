package ec.edu.simulacion.ape07.vista;

import ec.edu.simulacion.ape07.modelo.*;
import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.DigestOutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public final class VistaResultados {
    public void guardar(Parametros parametros, List<Medicion> mediciones, Path salida) throws IOException {
        Files.createDirectories(salida);
        var resumen = new StringBuilder("n,dentro,pi_estimado,error_absoluto,tiempo_mediana_s,tiempo_minimo_s,repeticiones\n");
        var tiempos = new StringBuilder("n,repeticion,segundos\n");
        for (Medicion medicion : mediciones) {
            Resultado resultado = medicion.resultado();
            resumen.append(String.format(Locale.ROOT, "%d,%d,%s,%s,%s,%s,%d%n", resultado.puntos(),
                    resultado.dentro(), resultado.estimacion(), resultado.errorAbsoluto(), medicion.mediana(),
                    medicion.segundos().stream().min(Double::compare).orElseThrow(), medicion.segundos().size()));
            for (int indice = 0; indice < medicion.segundos().size(); indice++) {
                tiempos.append(resultado.puntos()).append(',').append(indice + 1).append(',')
                        .append(medicion.segundos().get(indice)).append('\n');
            }
        }
        Files.writeString(salida.resolve("resumen.csv"), resumen, StandardCharsets.UTF_8);
        Files.writeString(salida.resolve("tiempos.csv"), tiempos, StandardCharsets.UTF_8);
        int cantidad = 2 * mediciones.getLast().resultado().puntos();
        MessageDigest huella;
        try {
            huella = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException error) {
            throw new IllegalStateException(error);
        }
        var generador = new GeneradorLCG(parametros);
        try (var archivo = new DataOutputStream(new DigestOutputStream(
                new BufferedOutputStream(Files.newOutputStream(salida.resolve("secuencia.bin"))), huella))) {
            for (int indice = 0; indice < cantidad; indice++) {
                archivo.writeInt((int) generador.siguienteEntero());
            }
        }
        generador = new GeneradorLCG(parametros);
        var primeros = new StringBuilder("punto,estado_x,estado_y,x,y,dentro\n");
        for (int indice = 1; indice <= Math.min(20, cantidad / 2); indice++) {
            long estadoX = generador.siguienteEntero();
            long estadoY = generador.siguienteEntero();
            double coordenadaX = 2.0 * (estadoX / (double) Parametros.MODULO) - 1.0;
            double coordenadaY = 2.0 * (estadoY / (double) Parametros.MODULO) - 1.0;
            int dentro = coordenadaX * coordenadaX + coordenadaY * coordenadaY <= 1.0 ? 1 : 0;
            primeros.append(String.format(Locale.ROOT, "%d,%d,%d,%s,%s,%d%n", indice, estadoX, estadoY,
                    coordenadaX, coordenadaY, dentro));
        }
        Files.writeString(salida.resolve("primeros20.csv"), primeros, StandardCharsets.UTF_8);
        String tamanos = mediciones.stream().map(medicion -> Integer.toString(medicion.resultado().puntos()))
                .collect(Collectors.joining(","));
        String entorno = """
                {
                  "lenguaje": "Java",
                  "version": "%s",
                  "parametros": {"semilla": %d, "a": 16807, "c": 0, "m": 2147483647},
                  "geometria": "cuadrado [-1,1)²; circulo x²+y²<=1",
                  "formato_secuencia": "uint32-be",
                  "valores_lcg": %d,
                  "sha256_secuencia": "%s",
                  "tamanos": [%s],
                  "repeticiones": %d,
                  "calentamientos": 3,
                  "reloj": "System.nanoTime",
                  "incluye_io_en_tiempo": false
                }
                """.formatted(System.getProperty("java.version"), parametros.semilla(), cantidad,
                        HexFormat.of().formatHex(huella.digest()), tamanos, mediciones.getFirst().segundos().size());
        Files.writeString(salida.resolve("entorno.json"), entorno, StandardCharsets.UTF_8);
    }

    public void mostrar(List<Medicion> mediciones, Path salida) {
        System.out.println("Monte Carlo | Java | cuadrado [-1,1)² y círculo de radio 1");
        System.out.printf("%10s %10s %15s %15s %15s%n", "N", "Dentro", "Pi estimado", "Error absoluto", "Mediana (s)");
        for (Medicion medicion : mediciones) {
            Resultado resultado = medicion.resultado();
            System.out.printf(Locale.ROOT, "%10d %10d %15.9f %15.9f %15.6f%n", resultado.puntos(),
                    resultado.dentro(), resultado.estimacion(), resultado.errorAbsoluto(), medicion.mediana());
        }
        System.out.println("Archivos: " + salida.toAbsolutePath());
    }
}
