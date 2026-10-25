package sir.io;

import sir.model.ResultadoPaso;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

/** Estrategia de exportacion inyectada al controlador, como en el proyecto anterior. */
public interface ExportadorResultados {
    void exportar(List<ResultadoPaso> historial, Path destino) throws IOException;
}
