package ec.edu.simulacion.ape06.vista;

import ec.edu.simulacion.ape06.modelo.Analisis;
import ec.edu.simulacion.ape06.modelo.Medicion;
import java.util.Locale;

public final class VistaConsola {
    public void mostrarAnalisis(Analisis analisis) {
        var m = analisis.muestra();
        var p = m.parametros();
        System.out.printf(Locale.ROOT, "%n%s | N=%d | X0=%d, a=%d, c=%d, m=%d%n",
                p.nombre().toUpperCase(Locale.ROOT), m.valores().length, p.semilla(), p.a(), p.c(), p.m());
        System.out.println("Primeros 10 valores (secuencia completa en CSV):");
        for (int i = 0; i < Math.min(10, m.valores().length); i++) {
            System.out.printf(Locale.ROOT, "  %2d: X=%12d, U=%.12f%n", i + 1, m.estados()[i], m.valores()[i]);
        }
        System.out.printf(Locale.ROOT, "Media=%.8f, varianza poblacional=%.8f%n", analisis.media(), analisis.varianza());
        System.out.println("Periodo observado: " + (analisis.periodoObservado() == null
                ? "no detectado en la muestra; no se afirma el periodo total" : analisis.periodoObservado()));
        for (var prueba : analisis.pruebas()) {
            if (prueba.estadistico() == null) {
                System.out.println(prueba.nombre() + ": " + prueba.decision() + ". " + prueba.nota());
                continue;
            }
            System.out.printf(Locale.ROOT, "%s: T=%.10g, p=%.10g, critico=%.10g, alfa=%.4f: %s%n",
                    prueba.nombre(), prueba.estadistico(), prueba.valorP(), prueba.critico(), prueba.alfa(), prueba.decision());
            System.out.println("  " + prueba.detalles());
            for (var b : prueba.intervalos()) {
                System.out.printf(Locale.ROOT, "  [%.1f, %.1f): O=%d, E=%.2f, aporte=%.6f%n",
                        b.inferior(), b.superior(), b.observada(), b.esperada(), b.aporte());
            }
        }
        System.out.println("No rechazar H0 no demuestra aleatoriedad ni independencia completa.");
    }

    public void mostrarMedicion(Medicion medicion) {
        var r = medicion.resultado();
        System.out.printf(Locale.ROOT, "%8s N=%7d puntos | pi=%.8f | error=%.8f | mediana=%.6f s%n",
                medicion.parametros().nombre(), r.puntos(), r.estimacion(), r.errorAbsoluto(), medicion.mediana());
    }
}
