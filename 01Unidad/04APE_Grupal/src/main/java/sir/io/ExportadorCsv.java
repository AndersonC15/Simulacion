package sir.io;

import sir.model.ResultadoPaso;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class ExportadorCsv implements ExportadorResultados {
    @Override
    public void exportar(List<ResultadoPaso> historial, Path destino) throws IOException {
        StringBuilder texto = new StringBuilder(LectorCsv.ENCABEZADO).append('\n');
        for (int i = 0; i < historial.size(); i++) {
            LectorCsv.validarTransicion(historial.subList(0, i), historial.get(i));
            texto.append(historial.get(i).aCsv()).append('\n');
        }
        if (historial.isEmpty()) { throw new IllegalArgumentException("No hay resultados para guardar."); }
        Files.writeString(destino, texto, StandardCharsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW);
    }
}
