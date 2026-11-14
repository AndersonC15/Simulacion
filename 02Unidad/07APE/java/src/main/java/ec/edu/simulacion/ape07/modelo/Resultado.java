package ec.edu.simulacion.ape07.modelo;

public record Resultado(int puntos, int dentro) {
    public double estimacion() {
        return 4.0 * dentro / puntos;
    }

    public double errorAbsoluto() {
        return Math.abs(estimacion() - Math.PI);
    }
}
