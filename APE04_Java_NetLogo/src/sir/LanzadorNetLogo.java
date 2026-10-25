package sir;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Usa las bibliotecas instaladas de NetLogo; no descarga nada al ejecutar. */
public final class LanzadorNetLogo {
    private LanzadorNetLogo() { }
    public static void abrir(Path raiz, Opciones opciones) throws Exception {
        if (java.awt.GraphicsEnvironment.isHeadless()) {
            throw new IllegalStateException("No hay pantalla grafica. Los resultados estan guardados; usa --sin-netlogo en servidores.");
        }
        Path home=localizar(opciones.netlogo());
        String cp=raiz.resolve("sir.jar") + File.pathSeparator + home.resolve("lib/app/*");
        List<String> comando=new ArrayList<>(List.of(
                Path.of(System.getProperty("java.home"),"bin","java").toString(), "-Xmx768m", "-Dfile.encoding=UTF-8",
                "--add-exports=java.desktop/sun.awt=ALL-UNNAMED", "--add-exports=java.desktop/sun.java2d=ALL-UNNAMED",
                "-Dnetlogo.extensions.dir="+home.resolve("extensions"),
                "-Dnetlogo.models.dir="+home.resolve("models"),
                "-Djava.library.path="+home.resolve("natives/linux-amd64"),
                "-cp",cp,"sir.view.VentanaSimulacion",raiz.toString(),opciones.csv().toString()));
        // InterfaceComponent resuelve __includes desde el directorio de trabajo.
        int codigo=new ProcessBuilder(comando).directory(raiz.resolve("netlogo").toFile()).inheritIO().start().waitFor();
        if (codigo!=0) { throw new IllegalStateException("El visor NetLogo termino con codigo "+codigo+". Revisa la ruta y que uses Java 21."); }
    }

    public static Path localizar(Path explicita) throws Exception {
        List<Path> candidatas=new ArrayList<>();
        if (explicita!=null) { candidatas.add(explicita); }
        else {
            String variable=System.getenv("NETLOGO_HOME");
            if (variable!=null && !variable.isBlank()) { candidatas.add(Path.of(variable)); }
            String path=System.getenv("PATH");
            if (path!=null) {
                for (String carpeta:path.split(java.util.regex.Pattern.quote(File.pathSeparator))) {
                    if (carpeta.isBlank()) { continue; }
                    Path ejecutable=Path.of(carpeta,"netlogo");
                    if (Files.isRegularFile(ejecutable)) {
                        Path padre=ejecutable.toRealPath().getParent();
                        candidatas.add(padre); if (padre.getParent()!=null) { candidatas.add(padre.getParent()); }
                    }
                }
            }
            Path usuario=Path.of(System.getProperty("user.home"));
            for (Path padre:List.of(Path.of("/opt"),usuario.resolve("Escritorio"),usuario.resolve("Desktop"),usuario.resolve("Descargas"),usuario)) {
                if (Files.isDirectory(padre)) {
                    try (var hijos=Files.list(padre)) {
                        hijos.filter(p->p.getFileName().toString().toLowerCase(java.util.Locale.ROOT).startsWith("netlogo")).forEach(candidatas::add);
                    } catch (java.io.IOException e) { /* Una carpeta sin acceso no impide usar --netlogo. */ }
                }
            }
        }
        for (Path candidata:candidatas) {
            if (Files.isRegularFile(candidata.resolve("lib/app/netlogo-7.0.4.jar"))) { return candidata.toRealPath(); }
        }
        throw new IllegalArgumentException("No encontre NetLogo 7.0.4. Agrega --netlogo \"/ruta/NetLogo 7.0.4\" (la carpeta que contiene lib y extensions).");
    }
}
