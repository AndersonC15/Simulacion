package ec.edu.simulacion.ape07.modelo;

public final class EstimadorPi {
    public Resultado estimar(int puntos, FuenteUniforme fuente) {
        if (puntos < 1 || puntos > 1000000) {
            throw new IllegalArgumentException("La cantidad de puntos debe estar entre 1 y 1000000.");
        }
        int dentro = 0;
        for (int indice = 0; indice < puntos; indice++) {
            double uniformeX = fuente.siguiente();
            double uniformeY = fuente.siguiente();
            if (!(uniformeX >= 0 && uniformeX < 1 && uniformeY >= 0 && uniformeY < 1)) {
                throw new IllegalArgumentException("La fuente debe producir valores finitos en [0,1).");
            }
            double coordenadaX = 2.0 * uniformeX - 1.0;
            double coordenadaY = 2.0 * uniformeY - 1.0;
            if (coordenadaX * coordenadaX + coordenadaY * coordenadaY <= 1.0) {
                dentro++;
            }
        }
        return new Resultado(puntos, dentro);
    }
}
