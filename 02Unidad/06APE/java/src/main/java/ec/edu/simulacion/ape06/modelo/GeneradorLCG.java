package ec.edu.simulacion.ape06.modelo;

import java.math.BigInteger;

/** Usa long si es seguro; BigInteger evita desbordamiento para parametros grandes. */
public final class GeneradorLCG {
    private final ParametrosLCG parametros;
    private final boolean usaLong;
    private final BigInteger multiplicador;
    private final BigInteger incremento;
    private final BigInteger modulo;
    private long estado;

    public GeneradorLCG(ParametrosLCG parametros) {
        this.parametros = parametros;
        this.estado = parametros.semilla();
        this.multiplicador = BigInteger.valueOf(parametros.a());
        this.incremento = BigInteger.valueOf(parametros.c());
        this.modulo = BigInteger.valueOf(parametros.m());
        this.usaLong = multiplicador.multiply(modulo.subtract(BigInteger.ONE)).add(incremento)
                .compareTo(BigInteger.valueOf(Long.MAX_VALUE)) <= 0;
    }

    public long siguienteEntero() {
        if (usaLong) {
            estado = (parametros.a() * estado + parametros.c()) % parametros.m();
        } else {
            estado = multiplicador.multiply(BigInteger.valueOf(estado)).add(incremento).mod(modulo).longValueExact();
        }
        return estado;
    }

    public double siguiente() { return (double) siguienteEntero() / parametros.m(); }

    public Muestra generar(int cantidad) {
        if (cantidad < 1) throw new IllegalArgumentException("La cantidad debe ser positiva.");
        long[] estados = new long[cantidad];
        double[] valores = new double[cantidad];
        for (int i = 0; i < cantidad; i++) {
            estados[i] = siguienteEntero();
            valores[i] = (double) estados[i] / parametros.m();
        }
        return new Muestra(parametros, estados, valores);
    }
}
