package ec.edu.simulacion.ape06;

import ec.edu.simulacion.ape06.controlador.ControladorSimulacion;
import ec.edu.simulacion.ape06.infraestructura.Archivos;
import ec.edu.simulacion.ape06.infraestructura.RepositorioResultados;
import ec.edu.simulacion.ape06.modelo.ChiCuadrado;
import ec.edu.simulacion.ape06.modelo.EstimadorPi;
import ec.edu.simulacion.ape06.modelo.KolmogorovSmirnov;
import ec.edu.simulacion.ape06.modelo.MedidorRendimiento;
import ec.edu.simulacion.ape06.modelo.Rachas;
import ec.edu.simulacion.ape06.modelo.ServicioSimulacion;
import ec.edu.simulacion.ape06.vista.VistaConsola;
import ec.edu.simulacion.ape06.vista.VistaGraficas;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

/** Raiz de composicion: conecta las dependencias concretas del programa. */
public final class Main {
    private Main() { }

    public static void main(String[] args) { System.exit(ejecutar(args)); }

    public static int ejecutar(String[] args) {
        System.setProperty("java.awt.headless", "true");
        if (args.length == 0 || args[0].equals("--help")) {
            System.out.println("Uso: java -jar java/target/ape06.jar ejecutar|benchmark [opciones]\n"
                    + "--config config/generadores.csv --generadores minstd,glibc,zx81\n"
                    + "--salida resultados/java --n 10000 --alfa 0.05\n"
                    + "--tamanos 1000,10000,100000,1000000 --repeticiones 5");
            return args.length == 0 ? 2 : 0;
        }
        try {
            if (!Set.of("ejecutar", "benchmark").contains(args[0])) throw new IllegalArgumentException("Comando desconocido.");
            var opciones = new HashMap<String, String>();
            Set<String> permitidas = Set.of("--config", "--generadores", "--salida", "--n", "--alfa", "--tamanos", "--repeticiones");
            for (int i = 1; i < args.length; i += 2) {
                if (!permitidas.contains(args[i]) || i + 1 >= args.length || opciones.putIfAbsent(args[i], args[i + 1]) != null) {
                    throw new IllegalArgumentException("Opcion desconocida, duplicada o sin valor: " + args[i]);
                }
            }
            var parametros = Archivos.leerParametros(Path.of(opciones.getOrDefault("--config", "config/generadores.csv")),
                    Arrays.asList(opciones.getOrDefault("--generadores", "minstd,glibc,zx81").split(",", -1)));
            int n = Integer.parseInt(opciones.getOrDefault("--n", "10000"));
            double alfa = Double.parseDouble(opciones.getOrDefault("--alfa", "0.05"));
            if (n < 50 || !Double.isFinite(alfa) || alfa <= 0 || alfa >= 1) {
                throw new IllegalArgumentException("Se requiere N >= 50 y 0 < alfa < 1.");
            }
            var tamanos = Arrays.stream(opciones.getOrDefault("--tamanos", "1000,10000,100000,1000000").split(",", -1))
                    .map(Integer::parseInt).toList();
            int repeticiones = Integer.parseInt(opciones.getOrDefault("--repeticiones", "5"));
            if (tamanos.stream().anyMatch(t -> t < 1) || tamanos.stream().distinct().count() != tamanos.size() || repeticiones < 1) {
                throw new IllegalArgumentException("Tamanos positivos sin duplicados y repeticiones >= 1.");
            }
            var controlador = new ControladorSimulacion(
                    new ServicioSimulacion(List.of(new ChiCuadrado(), new KolmogorovSmirnov(), new Rachas())),
                    new MedidorRendimiento(new EstimadorPi()), new VistaConsola(), new VistaGraficas(),
                    new RepositorioResultados(Path.of(opciones.getOrDefault("--salida", "resultados/java"))));
            if (args[0].equals("ejecutar")) controlador.ejecutar(parametros, n, alfa);
            else controlador.benchmark(parametros, tamanos, repeticiones);
            return 0;
        } catch (IllegalArgumentException | IOException | ArithmeticException error) {
            System.err.println("Error: " + error.getMessage());
            return 2;
        }
    }
}
