package sir.controller;

import sir.io.ExportadorResultados;
import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;
import sir.model.SimulacionSIR;
import sir.view.GraficaSIR;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/** Orquesta cada ejecucion. Cada CSV tiene su PNG y sus parametros al lado. */
public final class ControladorSIR {
    private final ExportadorResultados exportador;
    public ControladorSIR(ExportadorResultados exportador) { this.exportador = java.util.Objects.requireNonNull(exportador); }

    public List<ResultadoPaso> ejecutar(ParametrosSIR parametros, long semilla, Path csv) throws IOException {
        java.util.Objects.requireNonNull(parametros,"Faltan parametros.");
        csv=csv.toAbsolutePath().normalize();
        if (csv.getFileName()==null || !csv.getFileName().toString().toLowerCase(Locale.ROOT).endsWith(".csv") || csv.getFileName().toString().length()<=4) {
            throw new IllegalArgumentException("La salida debe terminar en .csv y tener nombre.");
        }
        Files.createDirectories(csv.getParent());
        Path reserva=csv.resolveSibling(csv.getFileName()+".lock");
        // CREATE_NEW reserva ese nombre incluso si dos procesos Java arrancan al mismo tiempo.
        var bloqueo=java.nio.channels.FileChannel.open(reserva,java.nio.file.StandardOpenOption.CREATE_NEW,java.nio.file.StandardOpenOption.WRITE);
        try (bloqueo) {
            bloqueo.write(java.nio.ByteBuffer.wrap(Long.toString(ProcessHandle.current().pid()).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
            return ejecutarReservado(parametros,semilla,csv);
        } finally { Files.deleteIfExists(reserva); }
    }

    private List<ResultadoPaso> ejecutarReservado(ParametrosSIR parametros, long semilla, Path csv) throws IOException {
        csv = csv.toAbsolutePath().normalize();
        String nombre = csv.getFileName().toString();
        if (!nombre.toLowerCase(Locale.ROOT).endsWith(".csv") || nombre.length() <= 4) {
            throw new IllegalArgumentException("La salida debe terminar en .csv y tener nombre.");
        }
        Path png = csv.resolveSibling(nombre.substring(0, nombre.length() - 4) + ".png");
        Path configuracion = csv.resolveSibling(nombre.substring(0, nombre.length() - 4) + ".properties");
        Files.createDirectories(csv.getParent());
        for (Path salida : List.of(csv, png, configuracion)) {
            if (Files.exists(salida, java.nio.file.LinkOption.NOFOLLOW_LINKS)) {
                throw new IOException("Ya existe " + salida.getFileName() + ". Usa otro nombre para conservar tus resultados.");
            }
        }
        List<ResultadoPaso> historial = new ArrayList<>();
        SimulacionSIR modelo = new SimulacionSIR(parametros, semilla);
        long inicio = System.nanoTime();
        historial.add(modelo.contarPoblacion());
        for (int t = 0; t < parametros.getTiempoSimulacion(); t++) { historial.add(modelo.paso()); }
        double ms = (System.nanoTime() - inicio) / 1000000.0;
        // Primero se preparan los tres archivos. El CSV se publica al final: el visor nunca lee medio CSV.
        Path temporal = Files.createTempDirectory(csv.getParent(), ".sir-");
        List<Path> publicados = new ArrayList<>();
        try {
            Path csvTmp = temporal.resolve("serie.csv");
            Path pngTmp = temporal.resolve("serie.png");
            Path datosTmp = temporal.resolve("serie.properties");
            exportador.exportar(historial, csvTmp);
            new GraficaSIR(historial).guardarImagen(pngTmp.toString());
            String datos = String.format(Locale.ROOT,
                    "poblacion=%d%ninfectados=%d%nbeta=%s%ngamma=%s%npasos=%d%ncontactos=%d%nsemilla=%d%nmodelo_ms=%.6f%n",
                    parametros.getPoblacion(), parametros.getInfectadosIniciales(), parametros.getBeta(), parametros.getGamma(),
                    parametros.getTiempoSimulacion(), parametros.getContactosPorInfectado(), semilla, ms);
            Files.writeString(datosTmp, datos, java.nio.charset.StandardCharsets.UTF_8);
            Files.move(pngTmp, png); publicados.add(png);
            Files.move(datosTmp, configuracion); publicados.add(configuracion);
            Files.move(csvTmp, csv); publicados.add(csv);
        } catch (IOException | RuntimeException e) {
            for (Path creado : publicados) { Files.deleteIfExists(creado); }
            throw e;
        } finally {
            try (var archivos = Files.list(temporal)) {
                for (Path archivo : archivos.toList()) { Files.deleteIfExists(archivo); }
            }
            Files.deleteIfExists(temporal);
        }
        return List.copyOf(historial);
    }

    public static Path nuevaRuta(Path raiz) {
        return raiz.resolve("netlogo/datos/ejecucion_" + UUID.randomUUID().toString().substring(0, 12) + ".csv");
    }
}
