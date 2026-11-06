package ec.edu.simulacion.ape06.modelo;

/** N puntos y 2N uniformes consecutivos; error absoluto respecto a Math.PI. */
public final class EstimadorPi {
    public ResultadoPi estimar(ParametrosLCG parametros, int puntos) {
        if (puntos < 1) throw new IllegalArgumentException("La cantidad de puntos debe ser positiva.");
        var generador = new GeneradorLCG(parametros);
        long dentro = 0;
        for (int i = 0; i < puntos; i++) {
            double x = generador.siguiente();
            double y = generador.siguiente();
            if (x * x + y * y <= 1) dentro++;
        }
        double estimacion = 4.0 * dentro / puntos;
        return new ResultadoPi(puntos, dentro, estimacion, Math.abs(estimacion - Math.PI));
    }
}
