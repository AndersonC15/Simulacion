package ec.edu.simulacion.ape06;

import ec.edu.simulacion.ape06.modelo.*;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

class ModeloTest {
    private ParametrosLCG ejemplo() { return new ParametrosLCG("ejemplo", 1, 5, 1, 16, "Calculo manual"); }

    @Test void cicloCalculadoAMano() {
        var muestra = new GeneradorLCG(ejemplo()).generar(16);
        assertArrayEquals(new long[]{6, 15, 12, 13, 2, 11, 8, 9, 14, 7, 4, 5, 10, 3, 0, 1}, muestra.estados());
        assertEquals(6 / 16.0, muestra.valores()[0]);
    }

    @Test void vectorParkMillerYReproducibilidad() {
        var p = new ParametrosLCG("minstd", 1, 16807, 0, 2147483647, "Park-Miller");
        long[] esperado = {16807, 282475249, 1622650073, 984943658, 1144108930};
        assertArrayEquals(esperado, new GeneradorLCG(p).generar(5).estados());
        assertArrayEquals(esperado, new GeneradorLCG(p).generar(5).estados());
    }

    @Test void parametros48BitsUsanAritmeticaSinDesbordamiento() {
        var p = new ParametrosLCG("java48", 1, 25214903917L, 11, 1L << 48, "Semana 5");
        assertArrayEquals(new long[]{25214903928L, 206026503483683L, 245470556921330L, 105707381795861L, 223576932655868L},
                new GeneradorLCG(p).generar(5).estados());
    }

    @Test void validaParametros() {
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG("mal", 0, 1, 0, 0, ""));
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG("mal", 16, 5, 1, 16, ""));
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG("../salida", 1, 5, 1, 16, ""));
        assertThrows(IllegalArgumentException.class, () -> new ParametrosLCG("mal", 1, 5, 1, (1L << 53) + 1, ""));
    }

    @Test void chiRespetaLimitesYFrecuencias() {
        double[] valores = new double[50];
        for (int i = 0; i < 50; i++) valores[i] = (i % 10) / 10.0;
        var r = new ChiCuadrado().evaluar(valores, .05);
        assertTrue(r.intervalos().stream().allMatch(b -> b.observada() == 5));
        assertEquals(0, r.estadistico());
        assertEquals(1, r.valorP());
        assertEquals(16.9189776046, r.critico(), 1e-8);
        Arrays.fill(valores, 0);
        valores[48] = Math.nextDown(.3);
        valores[49] = .3;
        r = new ChiCuadrado().evaluar(valores, .05);
        assertEquals(1, r.intervalos().get(2).observada());
        assertEquals(1, r.intervalos().get(3).observada());
    }

    @Test void ksEjemploManualConservaOrden() {
        double[] valores = {.1, .4, .35, .8};
        double[] copia = valores.clone();
        var r = new KolmogorovSmirnov().evaluar(valores, .05);
        assertEquals(.35, r.detalles().get("d_mas"), 1e-15);
        assertEquals(.1, r.detalles().get("d_menos"), 1e-15);
        assertEquals(.35, r.estadistico(), 1e-15);
        assertArrayEquals(copia, valores);
    }

    @Test void distribucionLimiteConReferenciasScipy() {
        // Valores de referencia publicados/calculados con scipy.stats.kstwobign.sf.
        assertEquals(1, DistribucionKolmogorov.supervivencia(0));
        assertEquals(.9639452436648751, DistribucionKolmogorov.supervivencia(.5), 1e-14);
        assertEquals(.26999967167735456, DistribucionKolmogorov.supervivencia(1), 1e-14);
        assertEquals(.0006709252557796953, DistribucionKolmogorov.supervivencia(2), 1e-15);
        assertEquals(0, DistribucionKolmogorov.supervivencia(30));
        assertEquals(1.35809863932255, DistribucionKolmogorov.critico(.05), 1e-12);
    }

    @Test void uniformidadNoImplicaIndependencia() {
        var p = new ParametrosLCG("ordenada", 0, 1, 1, 100, "Caso de comprobacion");
        var valores = new GeneradorLCG(p).generar(100).valores();
        assertEquals(1, new ChiCuadrado().evaluar(valores, .05).valorP());
        assertTrue(new KolmogorovSmirnov().evaluar(valores, .05).valorP() > .05);
        assertTrue(new Rachas().evaluar(valores, .05).valorP() < .05);
    }

    @Test void rachasAlternadasYEmpates() {
        double[] valores = new double[24];
        for (int i = 0; i < 24; i++) valores[i] = i % 2 == 0 ? .2 : .8;
        var r = new Rachas().evaluar(valores, .05);
        assertEquals(24, r.detalles().get("rachas"));
        assertEquals(13, r.detalles().get("media_rachas"));
        assertTrue(r.valorP() < .05);
        r = new Rachas().evaluar(new double[]{.5, .1, .9}, .05);
        assertEquals(1, r.detalles().get("empates"));
        assertNull(r.valorP());
        assertEquals("No aplicable", r.decision());
    }

    @ParameterizedTest @ValueSource(doubles = {Double.NaN, Double.POSITIVE_INFINITY, 1, -.1})
    void rechazaDatosFueraDelDominio(double valor) {
        assertThrows(IllegalArgumentException.class, () -> new KolmogorovSmirnov().evaluar(new double[]{valor}, .05));
    }

    @Test void chiRechazaEsperadasPequenas() {
        assertThrows(IllegalArgumentException.class, () -> new ChiCuadrado().evaluar(new double[49], .05));
    }

    @Test void decisionEnElLimiteAlfa() {
        var r = new ResultadoPrueba("ejemplo", "h0", 0.0, .05, 0.0, .05, "prueba", Map.of(), List.of(), "");
        assertEquals("No se rechaza H0", r.decision());
    }

    @Test void piYPeriodoConEjemploManual() {
        var r = new EstimadorPi().estimar(ejemplo(), 8);
        assertEquals(6, r.dentro());
        assertEquals(3, r.estimacion());
        var a = new ServicioSimulacion(List.of(new ChiCuadrado(), new KolmogorovSmirnov(), new Rachas()))
                .analizar(ejemplo(), 50, .05);
        assertEquals(16, a.periodoObservado());
        assertEquals(16, a.distintos());
    }
}
