package sir.controller;

import sir.io.ExportadorResultados;
import sir.io.ExportadorIndividuos;
import sir.io.HuellasArchivos;
import sir.io.LectorIndividuos;
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
import java.nio.charset.StandardCharsets;
import java.nio.file.LinkOption;
import java.nio.file.StandardOpenOption;

/** Prepara cuatro salidas, publica el agregado al final y retira sus propios archivos si falla. */
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
        List<Path> reservas = new ArrayList<>();
        Exception errorOperacion = null;
        try {
            // Reservamos cada salida: a.csv y a_individuos.csv comparten un nombre de archivo.
            // CREATE_NEW protege tambien frente a otros procesos que usan este controlador.
            for (Path salida : rutasSalida(csv).stream().sorted().toList()) {
                Path reserva = salida.resolveSibling(salida.getFileName() + ".lock");
                try (var bloqueo = java.nio.channels.FileChannel.open(reserva,
                        StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
                    reservas.add(reserva);
                    bloqueo.write(java.nio.ByteBuffer.wrap(Long.toString(ProcessHandle.current().pid()).getBytes(StandardCharsets.UTF_8)));
                }
            }
            return ejecutarReservado(parametros, semilla, csv);
        } catch (IOException | RuntimeException error) {
            errorOperacion = error;
            throw error;
        } finally {
            limpiar(reservas, errorOperacion);
        }
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
        Path individuos = LectorIndividuos.rutaCompanera(csv);
        for (Path salida : rutasSalida(csv)) {
            if (Files.exists(salida, LinkOption.NOFOLLOW_LINKS)) {
                throw new IOException("Ya existe " + salida.getFileName() + ". Usa otro nombre para conservar tus resultados.");
            }
        }
        List<ResultadoPaso> historial = new ArrayList<>();
        // Primero se preparan los cuatro archivos. El agregado se publica al final.
        Path temporal = Files.createTempDirectory(csv.getParent(), ".sir-");
        List<Path> publicados = new ArrayList<>();
        Exception errorOperacion = null;
        try {
            Path csvTmp = temporal.resolve("serie.csv");
            Path pngTmp = temporal.resolve("serie.png");
            Path datosTmp = temporal.resolve("serie.properties");
            Path individuosTmp = temporal.resolve("serie_individuos.csv");
            SimulacionSIR modelo = new SimulacionSIR(parametros, semilla);
            long nanosModelo = 0;
            try (ExportadorIndividuos detalle = new ExportadorIndividuos(individuosTmp)) {
                long inicio = System.nanoTime();
                historial.add(modelo.contarPoblacion());
                nanosModelo += System.nanoTime() - inicio;
                detalle.escribirPaso(0, modelo.getPoblacion());
                for (int t = 0; t < parametros.getTiempoSimulacion(); t++) {
                    inicio = System.nanoTime();
                    historial.add(modelo.paso());
                    nanosModelo += System.nanoTime() - inicio;
                    detalle.escribirPaso(modelo.getTiempoActual(), modelo.getPoblacion());
                }
            }
            double ms = nanosModelo / 1000000.0;
            exportador.exportar(historial, csvTmp);
            new GraficaSIR(historial).guardarImagen(pngTmp.toString());
            String datos = String.format(Locale.ROOT,
                    "poblacion=%d%ninfectados=%d%nbeta=%s%ngamma=%s%npasos=%d%ncontactos=%d%nsemilla=%d%nmodelo_ms=%.6f%ncsv_sha256=%s%nindividuos_sha256=%s%n",
                    parametros.getPoblacion(), parametros.getInfectadosIniciales(), parametros.getBeta(), parametros.getGamma(),
                    parametros.getTiempoSimulacion(), parametros.getContactosPorInfectado(), semilla, ms,
                    HuellasArchivos.calcular(csvTmp), HuellasArchivos.calcular(individuosTmp));
            Files.writeString(datosTmp, datos, StandardCharsets.UTF_8);
            Files.move(pngTmp, png); publicados.add(png);
            Files.move(datosTmp, configuracion); publicados.add(configuracion);
            Files.move(individuosTmp, individuos); publicados.add(individuos);
            Files.move(csvTmp, csv); publicados.add(csv);
        } catch (IOException | RuntimeException e) {
            errorOperacion = e;
            limpiar(publicados, e);
            throw e;
        } finally {
            limpiarTemporal(temporal, errorOperacion);
        }
        return List.copyOf(historial);
    }

    private static List<Path> rutasSalida(Path csv) {
        String nombre = csv.getFileName().toString();
        String base = nombre.substring(0, nombre.length() - 4);
        return List.of(csv, csv.resolveSibling(base + ".png"), csv.resolveSibling(base + ".properties"),
                LectorIndividuos.rutaCompanera(csv));
    }

    private static void limpiar(List<Path> creados, Exception error) throws IOException {
        IOException fallo = null;
        for (Path creado : creados) {
            try { Files.deleteIfExists(creado); }
            catch (IOException limpieza) {
                if (error != null) { error.addSuppressed(limpieza); }
                else if (fallo == null) { fallo = limpieza; }
                else { fallo.addSuppressed(limpieza); }
            }
        }
        creados.clear();
        if (fallo != null) { throw fallo; }
    }

    private static void limpiarTemporal(Path temporal, Exception error) throws IOException {
        if (!Files.exists(temporal, LinkOption.NOFOLLOW_LINKS)) { return; }
        try {
            try (var archivos = Files.list(temporal)) {
                limpiar(new ArrayList<>(archivos.toList()), error);
            }
            Files.deleteIfExists(temporal);
        } catch (IOException limpieza) {
            if (error != null) { error.addSuppressed(limpieza); }
            else { throw limpieza; }
        }
    }

    public static Path nuevaRuta(Path raiz) {
        return raiz.resolve("netlogo/datos/ejecucion_" + UUID.randomUUID().toString().substring(0, 12) + ".csv");
    }
}
