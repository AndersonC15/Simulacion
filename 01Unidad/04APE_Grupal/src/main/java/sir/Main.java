package sir;

import java.nio.file.Path;
import java.util.Arrays;
import sir.controller.ControladorSIR;
import sir.io.ExportadorCsv;
import sir.model.ResultadoPaso;

public final class Main {
    private Main() { }
    public static void main(String[] args) {
        if (Arrays.asList(args).contains("--ayuda") || Arrays.asList(args).contains("-h")) { ayuda(); return; }
        try {
            Path raiz=raiz();
            Opciones opciones=Opciones.leer(args,raiz);
            // El PNG se dibuja en memoria: este modo no necesita ni intenta abrir X11.
            if (opciones.sinNetlogo()) { System.setProperty("java.awt.headless","true"); }
            var serie=new ControladorSIR(new ExportadorCsv()).ejecutar(opciones.parametros(),opciones.semilla(),opciones.csv());
            ResultadoPaso fin=serie.get(serie.size()-1);
            ResultadoPaso pico=serie.stream().max(java.util.Comparator.comparingInt(ResultadoPaso::getInfectados)).orElseThrow();
            System.out.println("CSV: " + opciones.csv());
            System.out.println("Detalle individual, PNG y parametros: mismo directorio y nombre base del CSV.");
            System.out.println("Semilla=" + opciones.semilla() + "; final=" + fin.aCsv() + "; pico I=" + pico.getInfectados() + " en t=" + pico.getTiempo());
            var parametros=opciones.parametros();
            String r0;
            if (parametros.getGamma()==0) {
                r0=parametros.getBeta()*parametros.getContactosPorInfectado()==0 ? "no definido (0/0)" : "sin limite: gamma es cero";
            } else {
                // Solo para presentar el cociente: evita mostrar 2.9999999999999996 en lugar de 3.
                r0=java.math.BigDecimal.valueOf(parametros.getBeta()).multiply(java.math.BigDecimal.valueOf(parametros.getContactosPorInfectado()))
                        .divide(java.math.BigDecimal.valueOf(parametros.getGamma()),java.math.MathContext.DECIMAL128).stripTrailingZeros().toString();
            }
            System.out.println("R0 nominal (contactos * beta / gamma): "+r0);
            if (!opciones.sinNetlogo()) { LanzadorNetLogo.abrir(raiz,opciones); }
        } catch (Exception e) {
            System.err.println("No se pudo completar: " + e.getMessage());
            System.err.println("Consulta java -jar target/sir.jar --ayuda. Los CSV ya generados se conservan.");
            System.exit(1);
        }
    }
    public static Path raiz() throws Exception {
        Path origen=ubicacionClases();
        // Se resuelve desde el artefacto, no desde el directorio de trabajo del usuario.
        Path carpeta=java.nio.file.Files.isDirectory(origen) ? origen : origen.getParent();
        for (Path candidata=carpeta; candidata!=null; candidata=candidata.getParent()) {
            if (java.nio.file.Files.isRegularFile(candidata.resolve("pom.xml"))
                    && java.nio.file.Files.isRegularFile(candidata.resolve("netlogo/modelo_sir_netlogo.nlogox"))) {
                return candidata;
            }
        }
        throw new java.io.IOException("No se encuentra la raiz del proyecto junto al artefacto. Conserva target/sir.jar dentro del proyecto con pom.xml y netlogo/.");
    }
    public static Path ubicacionClases() throws Exception {
        return Path.of(Main.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toRealPath();
    }
    private static void ayuda() {
        System.out.println("Uso: java -jar target/sir.jar [opciones]");
        System.out.println("--poblacion 100 --infectados 5 --beta 0.30 --gamma 0.10 --pasos 100 --contactos 1 --semilla 42");
        System.out.println("--csv ruta/nueva.csv     Guarda CSV, _individuos.csv, PNG y parametros juntos; no sobrescribe.");
        System.out.println("Sin --csv: netlogo/datos/ junto al proyecto. Las rutas --csv relativas usan el directorio actual.");
        System.out.println("--netlogo RUTA           Directorio de NetLogo 7.0.4, si no se detecta automaticamente.");
        System.out.println("--sin-netlogo            Solo genera resultados. --sin-grafica es un alias compatible.");
        System.out.println("Sin opciones: escenario de la guia y apertura del visor NetLogo con reproduccion progresiva.");
        System.out.println("Limites para la demostracion: N 1..10000; I0 0..N; beta/gamma 0..1; pasos 0..2000; contactos 0..20.");
    }
}
