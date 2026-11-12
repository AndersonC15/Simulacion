package ec.edu.simulacion.modelo;

import java.math.BigInteger;

public final class GeneradorLCG implements GeneradorPseudoaleatorio {
    private final BigInteger multiplicador;
    private final BigInteger incremento;
    private final BigInteger modulo;
    private long estado;

    public GeneradorLCG(ParametrosLCG parametros) {
        multiplicador = BigInteger.valueOf(parametros.a());
        incremento = BigInteger.valueOf(parametros.c());
        modulo = BigInteger.valueOf(parametros.m());
        estado = parametros.semilla();
    }

    @Override
    public long siguiente() {
        // Aritmética exacta incluso si a*X+c excediera el rango de long.
        estado = multiplicador.multiply(BigInteger.valueOf(estado))
                .add(incremento).mod(modulo).longValueExact();
        return estado;
    }
}

