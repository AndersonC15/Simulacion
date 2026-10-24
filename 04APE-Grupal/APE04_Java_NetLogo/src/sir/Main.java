package sir;

import sir.controller.ControladorSIR;
import sir.io.ExportadorCsv;
import sir.model.ParametrosSIR;
import sir.model.SimulacionSIR;
import sir.view.VistaConsola;
import java.io.IOException;
import java.nio.file.Path;
import java.security.SecureRandom;

/** Entrada: interpreta opciones y conecta los objetos del MVC. */
public final class Main {
    private Main() { }

    public static void main(String[] args) {
        long semilla = new SecureRandom().nextLong();
        boolean mostrarGrafica = true;
        Path csv = Path.of(ControladorSIR.CSV_POR_DEFECTO);
        Path png = Path.of(ControladorSIR.PNG_POR_DEFECTO);
        try {
            for (int i = 0; i < args.length; i++) {
                String opcion = args[i];
                switch (opcion) {
                    case "--semilla":
                        semilla = Long.parseLong(valor(args, ++i, opcion));
                        break;
                    case "--csv":
                        csv = Path.of(valor(args, ++i, opcion));
                        break;
                    case "--png":
                        png = Path.of(valor(args, ++i, opcion));
                        break;
                    case "--sin-grafica":
                        mostrarGrafica = false;
                        break;
                    case "--ayuda":
                    case "-h":
                        imprimirAyuda();
                        return;
                    default:
                        throw new IllegalArgumentException("Opcion desconocida: " + opcion);
                }
            }
            ParametrosSIR parametros = new ParametrosSIR();
            SimulacionSIR modelo = new SimulacionSIR(parametros, semilla);
            ControladorSIR controlador = new ControladorSIR(modelo, new VistaConsola(),
                    new ExportadorCsv(), csv, png, mostrarGrafica);
            controlador.ejecutar();
        } catch (IllegalArgumentException | IOException e) {
            System.err.println("Error: " + e.getMessage());
            System.err.println("Consulta las opciones con --ayuda.");
            System.exit(1);
        }
    }

    private static String valor(String[] args, int indice, String opcion) {
        if (indice >= args.length) {
            throw new IllegalArgumentException("Falta el valor de " + opcion);
        }
        return args[indice];
    }

    private static void imprimirAyuda() {
        System.out.println("Uso: java -cp out sir.Main [opciones]");
        System.out.println("  --semilla <entero>   Repetir una ejecucion (ejemplo: 42)");
        System.out.println("  --csv <archivo>     Salida CSV; defecto: " + ControladorSIR.CSV_POR_DEFECTO);
        System.out.println("  --png <archivo>     Salida PNG; defecto: " + ControladorSIR.PNG_POR_DEFECTO);
        System.out.println("  --sin-grafica       Guarda el PNG sin abrir la ventana");
        System.out.println("  --ayuda, -h         Mostrar esta ayuda");
        System.out.println("N=100, I0=5, S0=95, beta=0.30, gamma=0.10, tiempo=100, contactos=1.");
    }
}
