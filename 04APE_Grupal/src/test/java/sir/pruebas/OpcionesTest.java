package sir.pruebas;

import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.io.TempDir;

final class OpcionesTest {
    @TempDir Path temporal;
    @TestFactory List<DynamicTest> casos() throws Exception {
        CasosRegresion casos=new CasosRegresion(temporal);
        casos.opciones();
        return casos.pruebas;
    }
}
