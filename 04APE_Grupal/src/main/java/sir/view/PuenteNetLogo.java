package sir.view;

import java.awt.Component;
import java.awt.Frame;
import java.lang.reflect.InvocationTargetException;

/** Adaptador pequeno: mantiene NetLogo fuera del modelo y permite compilar solo con el JDK. */
public final class PuenteNetLogo {
    private final Object interfaz;
    public PuenteNetLogo(Frame padre) throws Exception {
        interfaz=Class.forName("org.nlogo.lite.InterfaceComponent").getConstructor(Frame.class).newInstance(padre);
        llamar("setAdVisible",new Class<?>[]{boolean.class},false);
    }
    public Component componente() { return (Component) interfaz; }
    public synchronized void abrir(String modelo) throws Exception {
        // El editor completo resuelve __includes; InterfaceComponent no aporta esos editores.
        // Se unen los mismos archivos en una copia temporal, sin mantener codigo duplicado.
        java.nio.file.Path original=java.nio.file.Path.of(modelo);
        var fabrica=javax.xml.parsers.DocumentBuilderFactory.newInstance();
        fabrica.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        var documento=fabrica.newDocumentBuilder().parse(original.toFile());
        var nodo=documento.getElementsByTagName("code").item(0);
        String fuente=nodo.getTextContent();
        var includes=java.util.regex.Pattern.compile("(?m)^__includes\\s*\\[([^\\]]*)\\]").matcher(fuente);
        StringBuilder codigo=new StringBuilder(includes.replaceAll(""));
        includes.reset();
        while (includes.find()) {
            var archivos=java.util.regex.Pattern.compile("\"([^\"]+)\"").matcher(includes.group(1));
            while (archivos.find()) {
                codigo.append('\n').append(java.nio.file.Files.readString(original.resolveSibling(archivos.group(1))));
            }
        }
        nodo.setTextContent(codigo.toString());
        java.nio.file.Path temporal=java.nio.file.Files.createTempFile(original.getParent(),".visor-",".nlogox");
        try {
            var transformador=javax.xml.transform.TransformerFactory.newInstance().newTransformer();
            transformador.transform(new javax.xml.transform.dom.DOMSource(documento),new javax.xml.transform.stream.StreamResult(temporal.toFile()));
            // NetLogo exige EDT para crear widgets y compilar InterfaceComponent.
            // La preparacion de archivos y todas las ordenes/reportes quedan en el trabajador.
            enHiloGrafico(()->{
                llamar("open",new Class<?>[]{String.class},temporal.toString());
                llamar("compile",new Class<?>[0]);
                if (((String)llamar("getProcedures",new Class<?>[0])).isBlank()) {
                    throw new java.io.IOException("NetLogo no cargo el codigo del modelo.");
                }
                for (String nombre:new String[]{"ABRIR CSV","COMPARAR CSV","REINICIAR","ANIMAR / PAUSAR","VER COMPLETO"}) {
                    llamar("hideWidget",new Class<?>[]{String.class},nombre);
                }
                return null;
            });
        } finally { java.nio.file.Files.deleteIfExists(temporal); }
    }
    // command/report se llaman desde un trabajador, nunca desde el hilo que dibuja Swing.
    public synchronized void ordenar(String codigo) throws Exception {
        llamar("command",new Class<?>[]{String.class},codigo);
        // El editor NetLogo tiene su propio refresco periodico; la ventana integrada lo solicita aqui.
        Object workspace=llamar("workspace",new Class<?>[0]);
        workspace.getClass().getMethod("periodicUpdate").invoke(workspace);
        javax.swing.SwingUtilities.invokeAndWait(()->componente().repaint());
    }
    public synchronized Object consultar(String codigo) throws Exception { return llamar("report",new Class<?>[]{String.class},codigo); }
    public Object instancia() { return interfaz; }
    public synchronized void cerrar() throws Exception {
        Object workspace=llamar("workspace",new Class<?>[0]);
        workspace.getClass().getMethod("dispose").invoke(workspace);
    }
    private <T> T enHiloGrafico(java.util.concurrent.Callable<T> accion) throws Exception {
        var tarea=new java.util.concurrent.FutureTask<>(accion);
        if (javax.swing.SwingUtilities.isEventDispatchThread()) { tarea.run(); }
        else { javax.swing.SwingUtilities.invokeAndWait(tarea); }
        try { return tarea.get(); }
        catch (java.util.concurrent.ExecutionException error) {
            if (error.getCause() instanceof Exception causa) { throw causa; }
            throw error;
        }
    }
    private Object llamar(String metodo,Class<?>[] tipos,Object... args) throws Exception {
        try { return interfaz.getClass().getMethod(metodo,tipos).invoke(interfaz,args); }
        catch (InvocationTargetException e) {
            Throwable causa=e.getCause();
            if (causa instanceof Exception) { throw (Exception) causa; }
            throw e;
        }
    }
    public static String texto(String valor) {
        return "\""+valor.replace("\\","\\\\").replace("\"","\\\"").replace("\r","\\r").replace("\n","\\n")+"\"";
    }
}
