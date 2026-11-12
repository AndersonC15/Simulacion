package ec.edu.simulacion.modelo;

public record AnalisisPeriodo(
        boolean coprimos, boolean factoresDividen, boolean reglaCuatro,
        Long periodoTeorico, Integer preperiodoObservado, Integer periodoObservado) {
}

