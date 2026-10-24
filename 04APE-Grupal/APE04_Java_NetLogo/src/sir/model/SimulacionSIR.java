package sir.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

public class SimulacionSIR {

    private final ParametrosSIR parametros;
    private final List<Individuo> poblacion;
    private final Random aleatorio;
    private final long semilla;
    private int tiempoActual;

    public SimulacionSIR(ParametrosSIR parametros) {
        this(parametros, System.nanoTime());
    }

    public SimulacionSIR(ParametrosSIR parametros, long semilla) {
        this.parametros = parametros;
        this.semilla = semilla;
        this.aleatorio = new Random(semilla);
        this.poblacion = new ArrayList<Individuo>();
        this.tiempoActual = 0;
        crearPoblacion();
        seleccionarInfectadosIniciales();
    }

    private void crearPoblacion() {
        for (int i = 0; i < parametros.getPoblacion(); i++) {
            poblacion.add(new Individuo(i, Estado.SUSCEPTIBLE));
        }
    }

    private void seleccionarInfectadosIniciales() {
        int seleccionados = 0;
        while (seleccionados < parametros.getInfectadosIniciales()) {
            Individuo individuo = poblacion.get(aleatorio.nextInt(poblacion.size()));
            if (individuo.getEstado() == Estado.SUSCEPTIBLE) {
                individuo.setEstado(Estado.INFECTADO);
                seleccionados++;
            }
        }
    }

    public ResultadoPaso contarPoblacion() {
        int susceptibles = 0;
        int infectados = 0;
        int recuperados = 0;
        for (Individuo individuo : poblacion) {
            switch (individuo.getEstado()) {
                case SUSCEPTIBLE:
                    susceptibles++;
                    break;
                case INFECTADO:
                    infectados++;
                    break;
                default:
                    recuperados++;
                    break;
            }
        }
        return new ResultadoPaso(tiempoActual, susceptibles, infectados, recuperados);
    }

    public ResultadoPaso paso() {
        Estado[] copia = new Estado[poblacion.size()];
        for (int i = 0; i < poblacion.size(); i++) {
            copia[i] = poblacion.get(i).getEstado();
        }

        for (int i = 0; i < poblacion.size(); i++) {
            if (copia[i] != Estado.INFECTADO) {
                continue;
            }

            for (int c = 0; c < parametros.getContactosPorInfectado(); c++) {
                int contacto = aleatorio.nextInt(poblacion.size());
                if (copia[contacto] == Estado.SUSCEPTIBLE
                        && aleatorio.nextDouble() < parametros.getBeta()) {
                    poblacion.get(contacto).setEstado(Estado.INFECTADO);
                }
            }

            if (aleatorio.nextDouble() < parametros.getGamma()) {
                poblacion.get(i).setEstado(Estado.RECUPERADO);
            }
        }

        tiempoActual++;
        return contarPoblacion();
    }

    public ParametrosSIR getParametros() {
        return parametros;
    }

    public long getSemilla() {
        return semilla;
    }

    public int getTiempoActual() {
        return tiempoActual;
    }

    public List<Individuo> getPoblacion() {
        return Collections.unmodifiableList(poblacion);
    }
}
