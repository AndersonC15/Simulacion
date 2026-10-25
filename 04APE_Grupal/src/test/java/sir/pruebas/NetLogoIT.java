package sir.pruebas;

import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.io.TempDir;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
final class NetLogoIT {
    @TempDir Path temporal;
    private CasosRegresion casos;
    @TestFactory List<DynamicTest> casos() throws Exception {
        casos=new CasosRegresion(temporal);
        casos.netlogo();
        return casos.pruebas;
    }
    @AfterAll void cerrarMotor() throws Exception { if(casos!=null)casos.cerrarNetLogo(); }
}
