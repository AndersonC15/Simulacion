package ec.edu.simulacion.ape07;

import ec.edu.simulacion.ape07.modelo.*;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

final class ModeloTest {
    @Test void vectorConocido() {
        var fuente = new GeneradorLCG(new Parametros(1));
        assertArrayEquals(new long[]{16807, 282475249, 1622650073, 984943658, 1144108930},
                new long[]{fuente.siguienteEntero(), fuente.siguienteEntero(), fuente.siguienteEntero(),
                        fuente.siguienteEntero(), fuente.siguienteEntero()});
    }

    @Test void semillasInvalidas() {
        for (long semilla : new long[]{Long.MIN_VALUE, -1, 0, 2147483647, Long.MAX_VALUE}) {
            assertThrows(IllegalArgumentException.class, () -> new Parametros(semilla));
        }
    }

    @Test void limitesSemillaYRango() {
        for (long semilla : new long[]{1, 2147483646}) {
            var fuente = new GeneradorLCG(new Parametros(semilla));
            for (int indice = 0; indice < 10000; indice++) {
                double valor = fuente.siguiente();
                assertTrue(valor >= 0 && valor < 1);
            }
        }
    }

    @Test void geometriaCentroBordeYEsquina() {
        double[] valores = {.5, .5, 0, .5, .5, 0, 0, 0};
        var indice = new AtomicInteger();
        Resultado resultado = new EstimadorPi().estimar(4, () -> valores[indice.getAndIncrement()]);
        assertEquals(3, resultado.dentro());
        assertEquals(3.0, resultado.estimacion());
        assertEquals(8, indice.get());
    }

    @Test void fuenteInvalida() {
        for (double valor : new double[]{-0.1, 1, Double.NaN, Double.POSITIVE_INFINITY}) {
            assertThrows(IllegalArgumentException.class, () -> new EstimadorPi().estimar(1, () -> valor));
        }
    }

    @Test void tamanosInvalidos() {
        for (int cantidad : new int[]{Integer.MIN_VALUE, -1, 0, 1000001, Integer.MAX_VALUE}) {
            assertThrows(IllegalArgumentException.class,
                    () -> new EstimadorPi().estimar(cantidad, () -> .5));
        }
    }

    @Test void reproducibilidadYCambioDeSemilla() {
        var primera = new GeneradorLCG(new Parametros(123457));
        var segunda = new GeneradorLCG(new Parametros(123457));
        var tercera = new GeneradorLCG(new Parametros(1));
        for (int indice = 0; indice < 10000; indice++) {
            assertEquals(primera.siguienteEntero(), segunda.siguienteEntero());
        }
        assertNotEquals(new GeneradorLCG(new Parametros(123457)).siguienteEntero(), tercera.siguienteEntero());
    }

    @Test void limiteUnMillon() {
        Resultado resultado = new EstimadorPi().estimar(1000000, () -> .5);
        assertEquals(1000000, resultado.dentro());
        assertEquals(4.0, resultado.estimacion());
    }

    @Test void medianaParImparEInmutabilidad() {
        assertEquals(3, new Medicion(new Resultado(1, 1), List.of(9.0, 1.0, 3.0)).mediana());
        assertEquals(2, new Medicion(new Resultado(1, 1), List.of(3.0, 1.0)).mediana());
        assertThrows(UnsupportedOperationException.class,
                () -> new Medicion(new Resultado(1, 1), List.of(1.0)).segundos().add(2.0));
    }

    @Test void repeticionesInvalidasYReinicio() {
        var medidor = new MedidorRendimiento(new EstimadorPi());
        for (int repeticiones : new int[]{0, -1, 31}) {
            assertThrows(IllegalArgumentException.class, () -> medidor.medir(new Parametros(1), 100, repeticiones));
        }
        Medicion medicion = medidor.medir(new Parametros(1), 100, 3);
        assertEquals(new EstimadorPi().estimar(100, new GeneradorLCG(new Parametros(1))), medicion.resultado());
        assertEquals(3, medicion.segundos().size());
    }
}
