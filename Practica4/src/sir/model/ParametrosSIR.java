package sir.model;

public class ParametrosSIR {

    public static final int POBLACION = 100;
    public static final int INFECTADOS_INICIALES = 5;
    public static final double BETA = 0.30;
    public static final double GAMMA = 0.10;
    public static final int TIEMPO_SIMULACION = 100;
    public static final int CONTACTOS_POR_INFECTADO = 1;

    private final int poblacion;
    private final int infectadosIniciales;
    private final double beta;
    private final double gamma;
    private final int tiempoSimulacion;
    private final int contactosPorInfectado;

    public ParametrosSIR() {
        this(POBLACION, INFECTADOS_INICIALES, BETA, GAMMA, TIEMPO_SIMULACION, CONTACTOS_POR_INFECTADO);
    }

    public ParametrosSIR(int poblacion, int infectadosIniciales, double beta, double gamma,
                         int tiempoSimulacion, int contactosPorInfectado) {
        this.poblacion = poblacion;
        this.infectadosIniciales = infectadosIniciales;
        this.beta = beta;
        this.gamma = gamma;
        this.tiempoSimulacion = tiempoSimulacion;
        this.contactosPorInfectado = contactosPorInfectado;
    }

    public int getPoblacion() {
        return poblacion;
    }

    public int getInfectadosIniciales() {
        return infectadosIniciales;
    }

    public int getSusceptiblesIniciales() {
        return poblacion - infectadosIniciales;
    }

    public double getBeta() {
        return beta;
    }

    public double getGamma() {
        return gamma;
    }

    public int getTiempoSimulacion() {
        return tiempoSimulacion;
    }

    public int getContactosPorInfectado() {
        return contactosPorInfectado;
    }

    public double getR0() {
        return gamma == 0.0 ? 0.0 : beta / gamma;
    }
}
