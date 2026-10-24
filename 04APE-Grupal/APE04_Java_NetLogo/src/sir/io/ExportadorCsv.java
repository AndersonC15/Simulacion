package sir.io;

import sir.model.ResultadoPaso;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Solo se ocupa de escribir los datos de la simulacion. */
public final class ExportadorCsv implements ExportadorResultados {
    public static final String ENCABEZADO = "tiempo,susceptibles,infectados,recuperados";

    @Override
    public void exportar(List<ResultadoPaso> historial, Path destino) throws IOException {
        Path padre = destino.toAbsolutePath().getParent();
        if (padre != null) {
            Files.createDirectories(padre);
        }
        try (BufferedWriter escritor = Files.newBufferedWriter(destino, StandardCharsets.UTF_8)) {
            escritor.write(ENCABEZADO);
            escritor.newLine();
            for (ResultadoPaso paso : historial) {
                escritor.write(paso.aCsv());
                escritor.newLine();
            }
        }
    }
}
