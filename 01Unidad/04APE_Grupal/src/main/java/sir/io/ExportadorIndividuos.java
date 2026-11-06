package sir.io;

import sir.model.Individuo;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;

/** Escribe solamente la instantanea actual; no conserva el historial individual. */
public final class ExportadorIndividuos implements AutoCloseable {
    private final BufferedWriter salida;
    private int tiempoEsperado;
    private int poblacion;

    public ExportadorIndividuos(Path destino) throws IOException {
        salida = Files.newBufferedWriter(destino, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        try {
            salida.write(LectorIndividuos.ENCABEZADO);
            salida.newLine();
        } catch (IOException error) {
            try { salida.close(); } catch (IOException cierre) { error.addSuppressed(cierre); }
            throw error;
        }
    }

    public void escribirPaso(int tiempo, List<Individuo> individuos) throws IOException {
        if (tiempo != tiempoEsperado || tiempo > 2000 || individuos.isEmpty() || individuos.size() > 10000
                || (tiempo > 0 && individuos.size() != poblacion)) {
            throw new IllegalArgumentException("Instantanea individual fuera de orden o poblacion invalida.");
        }
        for (int id = 0; id < individuos.size(); id++) {
            if (individuos.get(id).getId() != id || individuos.get(id).getEstado() == null) {
                throw new IllegalArgumentException("Los individuos deben estar ordenados por ID desde 0.");
            }
        }
        poblacion = individuos.size();
        for (Individuo individuo : individuos) {
            salida.write(Integer.toString(tiempo));
            salida.write(',');
            salida.write(Integer.toString(individuo.getId()));
            salida.write(',');
            salida.write(individuo.getEstado().name());
            salida.newLine();
        }
        tiempoEsperado++;
    }

    @Override
    public void close() throws IOException {
        salida.close();
    }
}
