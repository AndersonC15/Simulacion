package sir.pruebas;

import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.io.TempDir;

final class ArchivosTest {
    @TempDir Path temporal;
    @TestFactory List<DynamicTest> casos() throws Exception {
        CasosRegresion casos=new CasosRegresion(temporal);
        casos.archivos();
        return casos.pruebas;
    }
}
