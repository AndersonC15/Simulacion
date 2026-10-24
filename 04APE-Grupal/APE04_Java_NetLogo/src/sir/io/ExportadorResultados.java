package sir.io;

import sir.model.ResultadoPaso;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

/** El controlador solicita una exportacion sin conocer el formato. */
public interface ExportadorResultados {
    void exportar(List<ResultadoPaso> historial, Path destino) throws IOException;
}
