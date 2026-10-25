package sir.io;

import sir.model.ResultadoPaso;
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Valida antes de cambiar la pantalla. Nunca ejecuta texto del archivo. */
public final class LectorCsv {
    public static final String ENCABEZADO = "tiempo,susceptibles,infectados,recuperados";

    public List<ResultadoPaso> leer(Path ruta) throws IOException {
        if (!Files.isRegularFile(ruta) || Files.size(ruta) > 1048576) {
            throw new IOException("Se requiere un CSV regular de hasta 1 MiB.");
        }
        List<ResultadoPaso> serie = new ArrayList<>();
        try (BufferedReader entrada = Files.newBufferedReader(ruta, StandardCharsets.UTF_8)) {
            String cabecera = leerLinea(entrada);
            if (cabecera != null && cabecera.startsWith("\uFEFF")) { cabecera = cabecera.substring(1); }
            if (!ENCABEZADO.equals(cabecera)) { throw new IOException("Encabezado CSV incorrecto."); }
            String linea;
            while ((linea = leerLinea(entrada)) != null) {
                if (linea.length() > 256 || serie.size() >= 2001) {
                    throw new IOException("CSV demasiado largo; maximo 2001 registros.");
                }
                String[] campos = linea.split(",", -1);
                if (campos.length != 4) { throw new IOException("Cada fila debe tener cuatro columnas."); }
                int[] valores = new int[4];
                for (int i = 0; i < 4; i++) {
                    String campo = campos[i].trim();
                    if (!campo.matches("[0-9]{1,9}")) { throw new IOException("Solo se aceptan enteros no negativos."); }
                    valores[i] = Integer.parseInt(campo);
                }
                try {
                    ResultadoPaso fila = new ResultadoPaso(valores[0], valores[1], valores[2], valores[3]);
                    validarTransicion(serie, fila);
                    serie.add(fila);
                } catch (IllegalArgumentException e) { throw new IOException(e.getMessage(), e); }
            }
        }
        if (serie.isEmpty()) { throw new IOException("El CSV no tiene registros."); }
        return List.copyOf(serie);
    }

    private static String leerLinea(BufferedReader entrada) throws IOException {
        StringBuilder texto = new StringBuilder();
        int caracter;
        while ((caracter = entrada.read()) != -1) {
            if (caracter == '\n') { break; }
            texto.append((char) caracter);
            if (texto.length() > 256) { throw new IOException("Una linea supera 256 caracteres."); }
        }
        if (caracter == -1 && texto.length() == 0) { return null; }
        if (texto.length() > 0 && texto.charAt(texto.length()-1) == '\r') { texto.setLength(texto.length()-1); }
        return texto.toString();
    }

    public static void validarTransicion(List<ResultadoPaso> anteriores, ResultadoPaso fila) {
        if (fila.getTiempo() != anteriores.size()) { throw new IllegalArgumentException("Tiempo discontinuo: debe empezar en 0."); }
        if (anteriores.isEmpty()) {
            if (fila.getRecuperados() != 0) { throw new IllegalArgumentException("El escenario Java comienza con R=0."); }
            return;
        }
        ResultadoPaso previo = anteriores.get(anteriores.size() - 1);
        if (fila.getTotal() != previo.getTotal() || fila.getSusceptibles() > previo.getSusceptibles()
                || fila.getRecuperados() < previo.getRecuperados()) {
            throw new IllegalArgumentException("No se conserva la poblacion o S/R cambian en sentido incorrecto.");
        }
        if (fila.getRecuperados() - previo.getRecuperados() > previo.getInfectados()
                || (previo.getInfectados() == 0 && fila.getSusceptibles() != previo.getSusceptibles())) {
            throw new IllegalArgumentException("Transicion imposible: no se recuperan mas que los I previos ni hay contagios sin I.");
        }
    }
}
