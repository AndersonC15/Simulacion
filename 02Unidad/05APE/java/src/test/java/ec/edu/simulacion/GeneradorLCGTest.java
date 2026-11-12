package ec.edu.simulacion;

import ec.edu.simulacion.controlador.ControladorExperimento;
import ec.edu.simulacion.modelo.AnalizadorPeriodo;
import ec.edu.simulacion.modelo.GeneradorLCG;
import ec.edu.simulacion.modelo.GeneradorPseudoaleatorio;
import ec.edu.simulacion.modelo.ParametrosLCG;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class GeneradorLCGTest {
    private List<Long> generar(ParametrosLCG p, int cantidad) {
        var generador = new GeneradorLCG(p);
        var estados = new ArrayList<Long>();
        for (int i = 0; i < cantidad; i++) {
            estados.add(generador.siguiente());
        }
        return estados;
    }

    @Test
    void vectorConocidoYContinuidad() {
        var g = new GeneradorLCG(ParametrosLCG.deLaGuia(12_345));
        for (long esperado : new long[]{87_628_868L, 71_072_467L, 2_332_836_374L,
                2_726_892_157L, 3_908_547_000L, 483_019_191L}) {
            assertEquals(esperado, g.siguiente());
        }
    }

    @Test
    void reproducibilidadRangoYCambioDeSemilla() {
        var p = ParametrosLCG.deLaGuia(12_345);
        var estados = generar(p, 10_000);
        assertEquals(estados, generar(p, 10_000));
        assertTrue(estados.stream().allMatch(x -> x >= 0 && x < p.m()
                && x / (double) p.m() >= 0 && x / (double) p.m() < 1));
        assertNotEquals(estados.getFirst(), generar(ParametrosLCG.deLaGuia(54_321), 1).getFirst());
    }

    @Test
    void limitesYAritmeticaExacta() {
        assertThrows(IllegalArgumentException.class, () -> ParametrosLCG.deLaGuia(-1));
        assertThrows(IllegalArgumentException.class, () -> ParametrosLCG.deLaGuia(1L << 32));
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG(0, 0, 0, 0));
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG(16, 0, 16, 0));
        long limite = (1L << 32) - 1;
        assertEquals(0, new GeneradorLCG(new ParametrosLCG(limite, limite, 1L << 32, limite)).siguiente());
    }

    @Test
    void hullDobellDistingueTeoriaDeMuestra() {
        var p = ParametrosLCG.deLaGuia(12_345);
        var analisis = new AnalizadorPeriodo().analizar(p, generar(p, 10_000));
        assertEquals(Long.valueOf(4_294_967_296L), analisis.periodoTeorico());
        assertNull(analisis.periodoObservado());
    }

    @Test
    void cicloCompletoYPreperiodo() {
        var p = new ParametrosLCG(5, 1, 16, 0);
        var analisis = new AnalizadorPeriodo().analizar(p, generar(p, 16));
        assertEquals(Long.valueOf(16), analisis.periodoTeorico());
        assertEquals(Integer.valueOf(0), analisis.preperiodoObservado());
        assertEquals(Integer.valueOf(16), analisis.periodoObservado());
        p = new ParametrosLCG(2, 0, 8, 1);
        analisis = new AnalizadorPeriodo().analizar(p, generar(p, 5));
        assertNull(analisis.periodoTeorico());
        assertEquals(Integer.valueOf(3), analisis.preperiodoObservado());
        assertEquals(Integer.valueOf(1), analisis.periodoObservado());
    }

    @Test
    void cadaCondicionHullDobell() {
        var analizador = new AnalizadorPeriodo();
        assertFalse(analizador.analizar(new ParametrosLCG(5, 2, 16, 0), List.of()).coprimos());
        assertFalse(analizador.analizar(new ParametrosLCG(2, 1, 9, 0), List.of()).factoresDividen());
        assertFalse(analizador.analizar(new ParametrosLCG(3, 1, 8, 0), List.of()).reglaCuatro());
    }

    @Test
    void controladorAceptaEstrategiaInyectadaYValidaCantidad() throws Exception {
        GeneradorPseudoaleatorio estrategia = () -> 1;
        var controlador = new ControladorExperimento(new AnalizadorPeriodo(), (resultado, ruta) -> {
            assertEquals(List.of(1L, 1L, 1L), resultado.estados());
        });
        var p = ParametrosLCG.deLaGuia(12_345);
        var resultado = controlador.ejecutar(p, estrategia, 3, Path.of("."));
        assertThrows(UnsupportedOperationException.class, () -> resultado.estados().add(2L));
        assertThrows(IllegalArgumentException.class, () -> controlador.ejecutar(p, estrategia, 0, Path.of(".")));
        assertThrows(IllegalArgumentException.class, () -> controlador.ejecutar(p, estrategia, 1_000_001, Path.of(".")));
    }
}
