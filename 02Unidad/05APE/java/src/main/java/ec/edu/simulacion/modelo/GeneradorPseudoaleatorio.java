package ec.edu.simulacion.modelo;

/** Contrato de la estrategia de generación, independiente de la presentación. */
@FunctionalInterface
public interface GeneradorPseudoaleatorio {
    long siguiente();
}

