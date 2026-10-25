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
        if (poblacion <= 0 || poblacion > 10000 || infectadosIniciales < 0 || infectadosIniciales > poblacion) {
            throw new IllegalArgumentException("N debe estar entre 1 y 10000; I0 entre 0 y N.");
        }
        if (!Double.isFinite(beta) || !Double.isFinite(gamma)
                || beta < 0 || beta > 1 || gamma < 0 || gamma > 1) {
            throw new IllegalArgumentException("Beta y gamma deben estar entre 0 y 1.");
        }
        if (tiempoSimulacion < 0 || tiempoSimulacion > 2000 || contactosPorInfectado < 0 || contactosPorInfectado > 20) {
            throw new IllegalArgumentException("Pasos: 0..2000. Contactos por paso: 0..20.");
        }
        if ((long) poblacion * Math.max(1, tiempoSimulacion) * (contactosPorInfectado + 1) > 10000000L) {
            throw new IllegalArgumentException("Escenario demasiado grande: N * pasos * (contactos + 1) debe ser <= 10000000.");
        }
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
        if (gamma == 0) { return beta * contactosPorInfectado == 0 ? Double.NaN : Double.POSITIVE_INFINITY; }
        return contactosPorInfectado * beta / gamma;
    }
}
