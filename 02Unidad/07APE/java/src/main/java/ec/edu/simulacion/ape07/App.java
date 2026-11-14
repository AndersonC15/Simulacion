package ec.edu.simulacion.ape07;

import ec.edu.simulacion.ape07.controlador.ControladorExperimento;
import ec.edu.simulacion.ape07.modelo.*;
import ec.edu.simulacion.ape07.vista.VistaResultados;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;

public final class App {
    private App() { }

    public static void main(String[] argumentos) {
        try {
            ejecutar(argumentos);
        } catch (IllegalArgumentException | IOException error) {
            System.err.println("Error: " + error.getMessage());
            System.exit(2);
        }
    }

    private static void ejecutar(String[] argumentos) throws IOException {
        long semilla = 123457;
        int[] tamanos = {1000, 10000, 100000, 1000000};
        int repeticiones = 5;
        Path salida = Path.of("resultados/java");
        for (int indice = 0; indice < argumentos.length; indice++) {
            if (argumentos[indice].equals("--help")) {
                System.out.println("Uso: java -jar ape07.jar [--semilla N] [--tamanos 1000,10000,100000,1000000] "
                        + "[--repeticiones 5] [--salida RUTA]");
                return;
            }
            String opcion = argumentos[indice];
            if (++indice == argumentos.length) {
                throw new IllegalArgumentException("Falta el valor de " + opcion);
            }
            String valor = argumentos[indice];
            switch (opcion) {
                case "--semilla" -> semilla = Long.parseLong(valor);
                case "--tamanos" -> tamanos = Arrays.stream(valor.split(",", -1)).mapToInt(Integer::parseInt).toArray();
                case "--repeticiones" -> repeticiones = Integer.parseInt(valor);
                case "--salida" -> salida = Path.of(valor);
                default -> throw new IllegalArgumentException("Opción desconocida: " + opcion);
            }
        }
        var controlador = new ControladorExperimento(new MedidorRendimiento(new EstimadorPi()), new VistaResultados());
        controlador.ejecutar(new Parametros(semilla), tamanos, repeticiones, salida);
    }
}
