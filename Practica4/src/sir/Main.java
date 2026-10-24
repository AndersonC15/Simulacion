package sir;

import sir.controller.ControladorSIR;
import sir.model.ParametrosSIR;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) {
        Long semilla = null;
        boolean mostrarGrafica = true;
        String rutaCsv = ControladorSIR.CSV_POR_DEFECTO;

        for (int i = 0; i < args.length; i++) {
            String argumento = args[i];

            if ("--semilla".equals(argumento)) {
                if (i + 1 >= args.length) {
                    fallo("Falta el valor de --semilla");
                    return;
                }
                i++;
                try {
                    semilla = Long.valueOf(args[i]);
                } catch (NumberFormatException e) {
                    fallo("Semilla invalida: " + args[i]);
                    return;
                }
            } else if ("--csv".equals(argumento)) {
                if (i + 1 >= args.length) {
                    fallo("Falta el valor de --csv");
                    return;
                }
                i++;
                rutaCsv = args[i];
            } else if ("--sin-grafica".equals(argumento)) {
                mostrarGrafica = false;
            } else if ("--ayuda".equals(argumento) || "-h".equals(argumento)) {
                imprimirAyuda();
                return;
            } else {
                fallo("Argumento desconocido: " + argumento);
                return;
            }
        }

        ControladorSIR controlador =
                new ControladorSIR(new ParametrosSIR(), semilla, mostrarGrafica, rutaCsv);
        controlador.ejecutar();
    }

    private static void fallo(String mensaje) {
        System.err.println("Error: " + mensaje);
        System.err.println();
        imprimirAyuda();
        System.exit(1);
    }

    private static void imprimirAyuda() {
        System.out.println("Uso: java sir.Main [opciones]");
        System.out.println();
        System.out.println("Opciones:");
        System.out.println("  --semilla <numero>  Fija la semilla del generador aleatorio");
        System.out.println("  --csv <archivo>     Ruta del CSV de salida (por defecto: "
                + ControladorSIR.CSV_POR_DEFECTO + ")");
        System.out.println("  --sin-grafica       No abre la ventana grafica");
        System.out.println("  --ayuda, -h         Muestra esta ayuda");
        System.out.println();
        System.out.println("Parametros del modelo (guia): N=100, I0=5, S0=95, "
                + "beta=0.30, gamma=0.10, tiempo=100, R0=3");
    }
}
