package sir.view;

import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;

import java.util.List;
import java.util.Locale;

public class VistaConsola {

    public void mostrarInicio(ParametrosSIR parametros, long semilla) {
        System.out.println();
        System.out.println("=============================================================");
        System.out.println("   MODELO SIR - SIMULACION EN JAVA (arquitectura MVC)");
        System.out.println("=============================================================");
        System.out.printf(Locale.ROOT, "  Poblacion total (N)          : %d%n", parametros.getPoblacion());
        System.out.printf(Locale.ROOT, "  Susceptibles iniciales (S0)  : %d%n", parametros.getSusceptiblesIniciales());
        System.out.printf(Locale.ROOT, "  Infectados iniciales (I0)    : %d%n", parametros.getInfectadosIniciales());
        System.out.printf(Locale.ROOT, "  beta (tasa de infeccion)     : %.2f%n", parametros.getBeta());
        System.out.printf(Locale.ROOT, "  gamma (tasa de recuperacion) : %.2f%n", parametros.getGamma());
        System.out.printf(Locale.ROOT, "  Tiempo de simulacion         : %d%n", parametros.getTiempoSimulacion());
        System.out.printf(Locale.ROOT, "  R0 = beta / gamma            : %.2f%n", parametros.getR0());
        System.out.printf(Locale.ROOT, "  Semilla aleatoria            : %d%n", semilla);
        System.out.println("-------------------------------------------------------------");
        System.out.printf(Locale.ROOT, "%-10s %-15s %-15s %-15s%n",
                "Tiempo", "Susceptibles", "Infectados", "Recuperados");
        System.out.println("-------------------------------------------------------------");
    }

    public void mostrarPaso(ResultadoPaso resultado) {
        System.out.printf(Locale.ROOT, "%-10d %-15d %-15d %-15d%n",
                resultado.getTiempo(),
                resultado.getSusceptibles(),
                resultado.getInfectados(),
                resultado.getRecuperados());
    }

    public void mostrarResumen(ParametrosSIR parametros, List<ResultadoPaso> historial) {
        if (historial.isEmpty()) {
            return;
        }

        ResultadoPaso pico = historial.get(0);
        for (ResultadoPaso resultado : historial) {
            if (resultado.getInfectados() > pico.getInfectados()) {
                pico = resultado;
            }
        }
        ResultadoPaso ultimo = historial.get(historial.size() - 1);

        System.out.println("-------------------------------------------------------------");
        System.out.println("RESUMEN DE LA SIMULACION");
        System.out.printf(Locale.ROOT, "  Pico de infeccion            : t = %d con %d infectados%n",
                pico.getTiempo(), pico.getInfectados());
        System.out.printf(Locale.ROOT, "  Estado final (t = %d)         : S = %d, I = %d, R = %d%n",
                ultimo.getTiempo(), ultimo.getSusceptibles(),
                ultimo.getInfectados(), ultimo.getRecuperados());
        System.out.printf(Locale.ROOT, "  Total verificado (S+I+R)     : %d (N = %d)%n",
                ultimo.getTotal(), parametros.getPoblacion());
        System.out.println("=============================================================");
        System.out.println();
    }

    public void mostrarMensaje(String mensaje) {
        System.out.println(mensaje);
    }
}
