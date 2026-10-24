package sir.pruebas;
import org.nlogo.headless.HeadlessWorkspace;
public final class PruebasNetLogo {
  private PruebasNetLogo() { }
  public static void main(String[] args) throws Exception {
    HeadlessWorkspace w = HeadlessWorkspace.newInstance();
    try {
      w.open(java.nio.file.Path.of(args[0], "netlogo/modelo_sir_netlogo.nlogox").toAbsolutePath().toString());
      w.command("startup");
      exigir(w,"length datos-java = 101");
      exigir(w,"length datos-referencia = 101");
      exigir(w,"datos-java = but-first (csv:from-file \"java_simulado.csv\")");
      exigir(w,"datos-referencia = but-first (csv:from-file \"java_referencia.csv\")");
      w.command("reiniciar repeat 100 [avanzar]");
      exigir(w,"indice = 100");
      exigir(w,"valor-java 1 + valor-java 2 + valor-java 3 = 100");
      System.out.println("OK: NetLogo 7.0.4 importa exactamente ambos CSV Java y reproduce t=0..100.");
    } finally { w.dispose(); }
  }
  private static void exigir(HeadlessWorkspace w,String r) throws Exception {
    if (!Boolean.TRUE.equals(w.report(r))) throw new AssertionError(r);
  }
}
