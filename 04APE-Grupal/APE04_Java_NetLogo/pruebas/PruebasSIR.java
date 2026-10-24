package sir.pruebas;

import sir.io.ExportadorCsv;
import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;
import sir.model.SimulacionSIR;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Pruebas de propiedades del modelo y del contrato CSV, sin librerias externas. */
public final class PruebasSIR {
    private static int comprobaciones;
    private PruebasSIR() { }

    public static void main(String[] args) throws Exception {
        ParametrosSIR normales = new ParametrosSIR();
        for (int semilla = 0; semilla < 30; semilla++) {
            List<ResultadoPaso> datos = ejecutar(normales, semilla);
            exigir(datos.size() == 101, "Debe haber 101 registros.");
            exigir(datos.get(0).aCsv().equals("0,95,5,0"), "Estado inicial incorrecto.");
            for (int t = 0; t < datos.size(); t++) {
                ResultadoPaso actual = datos.get(t);
                exigir(actual.getTiempo() == t, "Tiempo discontinuo.");
                exigir(actual.getTotal() == 100, "Se perdio poblacion.");
                exigir(actual.getSusceptibles() >= 0 && actual.getInfectados() >= 0
                        && actual.getRecuperados() >= 0, "Conteo negativo.");
                if (t > 0) {
                    ResultadoPaso anterior = datos.get(t - 1);
                    exigir(actual.getSusceptibles() <= anterior.getSusceptibles(), "S aumento.");
                    exigir(actual.getRecuperados() >= anterior.getRecuperados(), "R disminuyo.");
                }
            }
        }
        exigir(csv(ejecutar(normales, 42)).equals(csv(ejecutar(normales, 42))),
                "La misma semilla debe reproducir la serie.");
        exigir(!csv(ejecutar(normales, 42)).equals(csv(ejecutar(normales, 7))),
                "Las semillas de ejemplo deben producir series distintas.");
        exigir(ejecutar(normales, 42).get(100).aCsv().equals("100,4,0,96"),
                "Se altero el resultado del algoritmo original para semilla 42.");

        List<ResultadoPaso> sinContagios = ejecutar(new ParametrosSIR(100, 5, 0, 1, 2, 1), 42);
        exigir(sinContagios.get(1).aCsv().equals("1,95,0,5"),
                "Beta=0, gamma=1: solo se recuperan los cinco iniciales.");
        List<ResultadoPaso> sinInfectados = ejecutar(new ParametrosSIR(100, 0, .3, .1, 100, 1), 1);
        exigir(sinInfectados.get(100).aCsv().equals("100,100,0,0"),
                "Sin infectados iniciales no debe aparecer infeccion.");
        List<ResultadoPaso> sinRecuperacion = ejecutar(new ParametrosSIR(100, 5, .3, 0, 100, 1), 2);
        exigir(sinRecuperacion.stream().allMatch(p -> p.getRecuperados() == 0),
                "Gamma=0 no puede generar recuperaciones.");

        boolean huboContagio = false;
        for (int semilla = 0; semilla < 100 && !huboContagio; semilla++) {
            ResultadoPaso paso = ejecutar(new ParametrosSIR(2, 1, 1, 1, 1, 1), semilla).get(1);
            if (paso.getSusceptibles() == 0) {
                huboContagio = true;
                exigir(paso.getInfectados() == 1 && paso.getRecuperados() == 1,
                        "Un recien infectado no puede recuperarse en su mismo paso.");
            }
        }
        exigir(huboContagio, "No se alcanzo el caso de contagio de prueba.");
        rechazar(() -> new ParametrosSIR(0, 0, .3, .1, 100, 1));
        rechazar(() -> new ParametrosSIR(100, 101, .3, .1, 100, 1));
        rechazar(() -> new ParametrosSIR(100, 5, Double.NaN, .1, 100, 1));
        rechazar(() -> new ParametrosSIR(100, 5, .3, 1.1, 100, 1));
        rechazar(() -> new ParametrosSIR(100, 5, .3, .1, -1, 1));

        Path carpeta = Files.createTempDirectory("ape04-prueba-csv-");
        Path destino = carpeta.resolve("subcarpeta/resultados.csv");
        try {
            new ExportadorCsv().exportar(ejecutar(normales, 42), destino);
            List<String> lineas = Files.readAllLines(destino);
            exigir(lineas.size() == 102, "CSV: encabezado + 101 registros.");
            exigir(lineas.get(0).equals(ExportadorCsv.ENCABEZADO), "Encabezado incorrecto.");
            exigir(lineas.get(1).equals("0,95,5,0"), "Fila inicial incorrecta.");
            exigir(lineas.get(101).equals("100,4,0,96"), "Fila final incorrecta.");
        } finally {
            Files.deleteIfExists(destino);
            Files.deleteIfExists(destino.getParent());
            Files.deleteIfExists(carpeta);
        }
        System.out.println("OK: " + comprobaciones + " comprobaciones Java. Conservacion, semillas, limites y CSV.");
    }

    private static List<ResultadoPaso> ejecutar(ParametrosSIR parametros, long semilla) {
        SimulacionSIR modelo = new SimulacionSIR(parametros, semilla);
        List<ResultadoPaso> datos = new ArrayList<ResultadoPaso>();
        datos.add(modelo.contarPoblacion());
        for (int t = 0; t < parametros.getTiempoSimulacion(); t++) {
            datos.add(modelo.paso());
        }
        return datos;
    }

    private static String csv(List<ResultadoPaso> datos) {
        StringBuilder texto = new StringBuilder();
        for (ResultadoPaso p : datos) { texto.append(p.aCsv()).append('\n'); }
        return texto.toString();
    }

    private static void rechazar(Runnable accion) {
        boolean rechazo = false;
        try { accion.run(); } catch (IllegalArgumentException e) { rechazo = true; }
        exigir(rechazo, "Se acepto un parametro invalido.");
    }

    private static void exigir(boolean condicion, String mensaje) {
        comprobaciones++;
        if (!condicion) { throw new AssertionError(mensaje); }
    }
}
