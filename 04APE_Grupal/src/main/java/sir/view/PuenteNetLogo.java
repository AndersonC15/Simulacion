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
    public void abrir(String modelo) throws Exception {
        // El editor completo resuelve __includes; InterfaceComponent no aporta esos editores.
        // Se unen los mismos archivos en una copia temporal, sin mantener codigo duplicado.
        java.nio.file.Path original=java.nio.file.Path.of(modelo);
        var fabrica=javax.xml.parsers.DocumentBuilderFactory.newInstance();
        fabrica.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        var documento=fabrica.newDocumentBuilder().parse(original.toFile());
        var nodo=documento.getElementsByTagName("code").item(0);
        String codigo=nodo.getTextContent().replaceAll("(?m)^__includes[^\\r\\n]*","");
        for(String archivo:new String[]{"datos.nls","vista.nls","controlador.nls"}) {
            codigo += "\n"+java.nio.file.Files.readString(original.resolveSibling(archivo));
        }
        nodo.setTextContent(codigo);
        java.nio.file.Path temporal=java.nio.file.Files.createTempFile(original.getParent(),".visor-",".nlogox");
        try {
            var transformador=javax.xml.transform.TransformerFactory.newInstance().newTransformer();
            transformador.transform(new javax.xml.transform.dom.DOMSource(documento),new javax.xml.transform.stream.StreamResult(temporal.toFile()));
            llamar("open",new Class<?>[]{String.class},temporal.toString());
        } finally { java.nio.file.Files.deleteIfExists(temporal); }
        llamar("compile",new Class<?>[0]);
        if (((String)llamar("getProcedures",new Class<?>[0])).isBlank()) {
            throw new java.io.IOException("NetLogo no cargo el codigo del modelo.");
        }
        for (String nombre:new String[]{"ABRIR CSV","COMPARAR CSV","REINICIAR","ANIMAR / PAUSAR","VER COMPLETO"}) {
            llamar("hideWidget",new Class<?>[]{String.class},nombre);
        }
    }
    // command/report se llaman desde un trabajador, nunca desde el hilo que dibuja Swing.
    public void ordenar(String codigo) throws Exception {
        llamar("command",new Class<?>[]{String.class},codigo);
        // El editor NetLogo tiene su propio refresco periodico; la ventana integrada lo solicita aqui.
        Object workspace=llamar("workspace",new Class<?>[0]);
        workspace.getClass().getMethod("periodicUpdate").invoke(workspace);
        javax.swing.SwingUtilities.invokeAndWait(()->componente().repaint());
    }
    public Object consultar(String codigo) throws Exception { return llamar("report",new Class<?>[]{String.class},codigo); }
    public Object instancia() { return interfaz; }
    public void cerrar() throws Exception {
        Object workspace=llamar("workspace",new Class<?>[0]);
        workspace.getClass().getMethod("dispose").invoke(workspace);
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
