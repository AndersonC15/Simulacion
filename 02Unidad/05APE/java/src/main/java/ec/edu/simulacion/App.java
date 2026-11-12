package ec.edu.simulacion;

import ec.edu.simulacion.controlador.ControladorExperimento;
import ec.edu.simulacion.modelo.AnalizadorPeriodo;
import ec.edu.simulacion.modelo.GeneradorLCG;
import ec.edu.simulacion.modelo.ParametrosLCG;
import ec.edu.simulacion.vista.VistaArchivosConsola;
import java.io.IOException;
import java.nio.file.Path;

public final class App {
    private App() { }

    public static void main(String[] args) {
        try {
            ejecutar(args);
        } catch (IllegalArgumentException | IOException error) {
            System.err.println("Error: " + error.getMessage());
            System.exit(2);
        }
    }

    private static void ejecutar(String[] args) throws IOException {
        long semilla = 12_345;
        int cantidad = 10_000;
        Path salida = Path.of("resultados/java");
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--help")) {
                System.out.println("Uso: java -jar ape05-lcg-1.0.0.jar "
                        + "[--semilla ENTERO] [--cantidad ENTERO] [--salida RUTA]");
                return;
            }
            String opcion = args[i];
            if (i + 1 >= args.length) {
                throw new IllegalArgumentException("Falta el valor de " + opcion);
            }
            String valor = args[++i];
            switch (opcion) {
                case "--semilla" -> semilla = Long.parseLong(valor);
                case "--cantidad" -> cantidad = Integer.parseInt(valor);
                case "--salida" -> salida = Path.of(valor);
                default -> throw new IllegalArgumentException("Opción desconocida: " + opcion);
            }
        }
        var parametros = ParametrosLCG.deLaGuia(semilla);
        var controlador = new ControladorExperimento(new AnalizadorPeriodo(), new VistaArchivosConsola());
        controlador.ejecutar(parametros, new GeneradorLCG(parametros), cantidad, salida);
    }
}

