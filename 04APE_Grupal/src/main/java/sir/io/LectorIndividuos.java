package sir.io;

import sir.model.Estado;
import sir.model.ResultadoPaso;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Properties;

/** Valida el archivo completo con una sola instantanea de estados en memoria. */
public final class LectorIndividuos {
    public static final String ENCABEZADO = "tiempo,id,estado";
    public static final long MAX_BYTES = 512L * 1024 * 1024;
    public static final long MAX_REGISTROS = 20_010_000L;

    public static Path rutaCompanera(Path agregado) {
        if (agregado.getFileName() == null) {
            throw new IllegalArgumentException("El archivo agregado debe tener nombre.");
        }
        return agregado.resolveSibling(nombreBase(agregado) + "_individuos.csv");
    }

    private static String nombreBase(Path agregado) {
        String nombre = agregado.getFileName().toString();
        return nombre.toLowerCase(Locale.ROOT).endsWith(".csv")
                ? nombre.substring(0, nombre.length() - 4) : nombre;
    }

    /** Retorna null si el CSV antiguo no tiene detalle. No inventa identidades. */
    public Path validar(Path agregado, List<ResultadoPaso> serie) throws IOException {
        validarSerie(serie);
        Path detalle = rutaCompanera(agregado);
        if (!Files.exists(detalle, LinkOption.NOFOLLOW_LINKS)) { return null; }
        if (!Files.isRegularFile(detalle) || Files.size(detalle) > MAX_BYTES) {
            throw new IOException("El CSV individual debe ser un archivo regular de hasta 512 MiB.");
        }
        int poblacion = serie.get(0).getTotal();
        if ((long) poblacion * serie.size() > MAX_REGISTROS) {
            throw new IOException("El detalle individual supera el limite de registros.");
        }
        Estado[] anteriores = new Estado[poblacion];
        MessageDigest huella = HuellasArchivos.nuevaHuella();
        // El decodificador rechaza UTF-8 invalido; leerLinea limita cada fila a 256 caracteres.
        try (var bytes = new DigestInputStream(Files.newInputStream(detalle), huella);
             var entrada = new BufferedReader(new InputStreamReader(bytes, StandardCharsets.UTF_8.newDecoder()))) {
            String encabezado = LectorCsv.leerLinea(entrada);
            if (encabezado != null && encabezado.startsWith("\uFEFF")) { encabezado = encabezado.substring(1); }
            if (!ENCABEZADO.equals(encabezado)) {
                throw new IOException("Encabezado individual incorrecto: se espera tiempo,id,estado.");
            }
            for (ResultadoPaso paso : serie) {
                int susceptibles = 0;
                int infectados = 0;
                int recuperados = 0;
                for (int id = 0; id < poblacion; id++) {
                    String linea = LectorCsv.leerLinea(entrada);
                    if (linea == null) {
                        throw new IOException("Detalle individual truncado: faltan individuos en t=" + paso.getTiempo() + ".");
                    }
                    String[] campos = linea.split(",", -1);
                    if (campos.length != 3) { throw new IOException("Cada fila individual debe tener tres columnas."); }
                    if (entero(campos[0]) != paso.getTiempo() || entero(campos[1]) != id) {
                        throw new IOException("Tiempo/ID individual fuera de orden, ausente o duplicado en t=" + paso.getTiempo() + ".");
                    }
                    Estado estado;
                    try { estado = Estado.valueOf(campos[2]); }
                    catch (IllegalArgumentException error) { throw new IOException("Estado individual desconocido: " + campos[2] + ".", error); }
                    if (!transicionValida(anteriores[id], estado)) {
                        throw new IOException("Transicion individual imposible para ID=" + id + " en t=" + paso.getTiempo() + ".");
                    }
                    anteriores[id] = estado;
                    switch (estado) {
                        case SUSCEPTIBLE -> susceptibles++;
                        case INFECTADO -> infectados++;
                        case RECUPERADO -> recuperados++;
                    }
                }
                if (susceptibles != paso.getSusceptibles() || infectados != paso.getInfectados()
                        || recuperados != paso.getRecuperados()) {
                    throw new IOException("El detalle individual no coincide con los conteos S/I/R en t=" + paso.getTiempo() + ".");
                }
            }
            if (LectorCsv.leerLinea(entrada) != null) {
                throw new IOException("El detalle individual contiene registros adicionales.");
            }
        }
        validarHuellas(agregado, HexFormat.of().formatHex(huella.digest()));
        return detalle;
    }

    private static int entero(String campo) throws IOException {
        if (!campo.matches("[0-9]{1,9}")) {
            throw new IOException("Tiempo e ID deben ser enteros no negativos.");
        }
        return Integer.parseInt(campo);
    }

    private static boolean transicionValida(Estado anterior, Estado actual) {
        return anterior == null || anterior == actual
                || (anterior == Estado.SUSCEPTIBLE && actual == Estado.INFECTADO)
                || (anterior == Estado.INFECTADO && actual == Estado.RECUPERADO);
    }

    private static void validarSerie(List<ResultadoPaso> serie) throws IOException {
        if (serie == null || serie.isEmpty() || serie.size() > 2001) {
            throw new IOException("Se requiere una serie agregada de 1 a 2001 instantes.");
        }
        try {
            for (int i = 0; i < serie.size(); i++) {
                if (serie.get(i) == null) { throw new IllegalArgumentException("Hay un instante nulo."); }
                LectorCsv.validarTransicion(serie.subList(0, i), serie.get(i));
            }
        } catch (IllegalArgumentException error) { throw new IOException("Serie agregada invalida: " + error.getMessage(), error); }
    }

    private static void validarHuellas(Path agregado, String huellaDetalle) throws IOException {
        Path configuracion = agregado.resolveSibling(nombreBase(agregado) + ".properties");
        if (!Files.exists(configuracion, LinkOption.NOFOLLOW_LINKS)) { return; }
        if (!Files.isRegularFile(configuracion) || Files.size(configuracion) > 16384) {
            throw new IOException("El archivo de parametros debe ser regular y de hasta 16 KiB.");
        }
        Properties propiedades = new Properties();
        try (var lector = Files.newBufferedReader(configuracion, StandardCharsets.UTF_8)) {
            propiedades.load(lector);
        } catch (IllegalArgumentException error) {
            throw new IOException("Archivo de parametros invalido.", error);
        }
        String huellaAgregado = propiedades.getProperty("csv_sha256");
        String esperadaDetalle = propiedades.getProperty("individuos_sha256");
        // Las ejecuciones antiguas no incluian estas huellas.
        if (huellaAgregado == null && esperadaDetalle == null) { return; }
        if (huellaAgregado == null || esperadaDetalle == null || !huellaAgregado.matches("[0-9a-f]{64}")
                || !esperadaDetalle.matches("[0-9a-f]{64}")
                || !esperadaDetalle.equals(huellaDetalle) || !huellaAgregado.equals(HuellasArchivos.calcular(agregado))) {
            throw new IOException("Las huellas de los CSV no coinciden: los archivos fueron modificados o pertenecen a ejecuciones distintas.");
        }
    }
}
