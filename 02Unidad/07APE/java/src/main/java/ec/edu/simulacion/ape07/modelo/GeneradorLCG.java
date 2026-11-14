package ec.edu.simulacion.ape07.modelo;

public final class GeneradorLCG implements FuenteUniforme {
    private long estado;

    public GeneradorLCG(Parametros parametros) {
        estado = parametros.semilla();
    }

    public long siguienteEntero() {
        estado = Parametros.MULTIPLICADOR * estado % Parametros.MODULO;
        return estado;
    }

    @Override
    public double siguiente() {
        return siguienteEntero() / (double) Parametros.MODULO;
    }
}
