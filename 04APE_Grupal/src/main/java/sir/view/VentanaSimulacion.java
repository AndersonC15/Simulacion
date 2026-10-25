package sir.view;

import sir.Opciones;
import sir.controller.ControladorSIR;
import sir.io.ExportadorCsv;
import sir.io.LectorCsv;
import sir.io.LectorIndividuos;
import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import javax.swing.*;

/** Vista Swing con graficas reales de NetLogo, sin las pestanas del editor. */
@SuppressWarnings("serial") // La ventana no se serializa.
public final class VentanaSimulacion extends JFrame {
    private static final long serialVersionUID=1L;
    public static final Color FONDO=new Color(11,18,32), VERDE=new Color(57,255,136), TEXTO=new Color(224,247,239);
    private final Path raiz;
    private final PuenteNetLogo netlogo;
    private final ExecutorService tareas=Executors.newSingleThreadExecutor();
    private final AtomicInteger pendientes=new AtomicInteger();
    private final Map<String,JTextField> campos=new LinkedHashMap<>();
    private final JLabel estado=new JLabel("Abriendo NetLogo...");
    private final JButton reproducir=new JButton("PAUSAR");
    private final JSlider velocidad=new JSlider(20,500,100);
    private final Timer reloj;
    private volatile boolean enMarcha=true;
    private volatile boolean cerrado;
    private volatile long revisionReproduccion;

    public VentanaSimulacion(Path raiz,Path csv) throws Exception {
        super("APE 04 | SIR - Java + NetLogo");
        this.raiz=raiz;
        setDefaultCloseOperation(DO_NOTHING_ON_CLOSE);
        setLayout(new BorderLayout(8,8));
        getContentPane().setBackground(FONDO);
        JPanel cabecera=new JPanel(new GridLayout(4,1,0,2));
        JLabel titulo=new JLabel("SIR  /  JAVA GENERA · NETLOGO REPRESENTA"); titulo.setFont(new Font("SansSerif",Font.BOLD,18)); titulo.setForeground(VERDE);
        JPanel filaTitulo=new JPanel(new FlowLayout(FlowLayout.LEFT,8,0));filaTitulo.add(titulo);cabecera.add(filaTitulo);
        JPanel entradas=new JPanel(new FlowLayout(FlowLayout.LEFT,8,5));
        String[][] parametros={{"poblacion","100"},{"infectados","5"},{"beta","0.30"},{"gamma","0.10"},{"pasos","100"},{"semilla","42"}};
        for (String[] par:parametros) {
            entradas.add(new JLabel(par[0])); JTextField campo=new JTextField(par[1],par[0].equals("semilla")?6:4);
            campo.setName(par[0]); campos.put(par[0],campo); entradas.add(campo);
        }
        entradas.add(boton("GENERAR ESCENARIO",this::generar));
        cabecera.add(entradas);
        JPanel controles=new JPanel(new FlowLayout(FlowLayout.LEFT,8,4));
        controles.add(boton("ABRIR CSV",()->elegir(false)));
        JButton comparar=boton("COMPARAR CON OTRO CSV",()->elegir(true));
        comparar.setToolTipText("Carga otra ejecucion de Java en Escenario B y compara S, I y R."); controles.add(comparar);
        controles.add(boton("QUITAR COMPARACION",()->{ pausa(); orden("quitar-referencia"); }));
        controles.add(boton("REINICIAR",()->{ pausa(); orden("reiniciar"); }));
        reproducir.setName("PAUSAR"); reproducir.addActionListener(e->alternar()); controles.add(reproducir);
        controles.add(boton("UN PASO",()->{ pausa(); orden("avanzar"); }));
        controles.add(boton("VER COMPLETO",()->{ pausa(); orden("mostrar-completo"); }));
        cabecera.add(controles);
        JPanel extras=new JPanel(new FlowLayout(FlowLayout.LEFT,8,3));
        extras.add(new JLabel("Pausa entre pasos (ms):")); velocidad.setPreferredSize(new Dimension(160,25));
        velocidad.setName("velocidad"); velocidad.addChangeListener(e->relojDelay()); extras.add(velocidad);
        extras.add(boton("GUARDAR VISTA PNG",this::exportar)); extras.add(estado); cabecera.add(extras);
        cabecera.setBorder(BorderFactory.createEmptyBorder(22,14,6,8));
        tema(cabecera); titulo.setForeground(VERDE); add(cabecera,BorderLayout.NORTH);
        netlogo=new PuenteNetLogo(this);
        JScrollPane scroll=new JScrollPane(netlogo.componente()); scroll.setBorder(null); scroll.getViewport().setBackground(FONDO);
        add(scroll,BorderLayout.CENTER);
        reloj=new Timer(100,e->tick());
        pack();
        Dimension pantalla=Toolkit.getDefaultToolkit().getScreenSize();
        setSize(Math.min(1270,pantalla.width-30),Math.min(840,pantalla.height-45));
        setMinimumSize(new Dimension(1120,650)); setLocationRelativeTo(null);
        addWindowListener(new WindowAdapter(){ @Override public void windowClosing(WindowEvent e){ cerrar(); } });
        getRootPane().registerKeyboardAction(e->cerrar(),KeyStroke.getKeyStroke("control Q"),JComponent.WHEN_IN_FOCUSED_WINDOW);
        ejecutar(()->{
            netlogo.abrir(raiz.resolve("netlogo/modelo_sir_netlogo.nlogox").toString());
            SwingUtilities.invokeLater(()->scroll.revalidate());
            netlogo.ordenar("startup");
            cargarArchivos(csv,false);
            iniciarSiVigente(0);
        });
    }
    private JButton boton(String texto,Runnable accion) {
        JButton boton=new JButton(texto); boton.setName(texto); boton.addActionListener(e->accion.run()); return boton;
    }
    private void tema(Component componente) {
        componente.setBackground(FONDO); componente.setForeground(TEXTO);
        if (componente instanceof JButton) { componente.setBackground(VERDE); componente.setForeground(FONDO); }
        if (componente instanceof JTextField) { ((JTextField)componente).setCaretColor(VERDE); }
        if (componente instanceof Container) { for (Component hijo:((Container)componente).getComponents()) { tema(hijo); } }
    }
    private void relojDelay() { if (reloj!=null) { reloj.setDelay(velocidad.getValue()); } }
    private void pausa() { revisionReproduccion++; enMarcha=false; reloj.stop(); reproducir.setText("CONTINUAR"); }
    private void iniciarSiVigente(long revision) {
        SwingUtilities.invokeLater(()->{
            if (cerrado || revision != revisionReproduccion) { return; }
            enMarcha=true; reproducir.setText("PAUSAR"); reloj.start();
        });
    }
    private void alternar() {
        if (enMarcha) { pausa(); return; }
        long revision=++revisionReproduccion;
        enMarcha=true; reproducir.setText("PAUSAR");
        ejecutar(()->{
            if (Boolean.TRUE.equals(netlogo.consultar("terminado?"))) { netlogo.ordenar("reiniciar"); }
            iniciarSiVigente(revision);
        });
    }
    private void tick() {
        if (!enMarcha || pendientes.get()!=0) { return; }
        long revision=revisionReproduccion;
        ejecutar(()->{
            if (!enMarcha || revision != revisionReproduccion) { return; }
            netlogo.ordenar("avanzar");
            if (Boolean.TRUE.equals(netlogo.consultar("terminado?"))) {
                SwingUtilities.invokeLater(()->{ if (revision==revisionReproduccion) { pausa(); } });
            }
        });
    }
    private void orden(String codigo) { ejecutar(()->netlogo.ordenar(codigo)); }
    private void elegir(boolean referencia) {
        pausa();
        JFileChooser selector=new JFileChooser(raiz.resolve("netlogo/datos").toFile());
        selector.setFileFilter(new javax.swing.filechooser.FileNameExtensionFilter("CSV agregado Java (no *_individuos.csv)","csv"));
        if (selector.showOpenDialog(this)==JFileChooser.APPROVE_OPTION) {
            Path ruta=selector.getSelectedFile().toPath(); ejecutar(()->cargarArchivos(ruta,referencia));
        }
    }
    public void cargar(Path ruta,boolean referencia) throws Exception {
        if (cerrado) { throw new IllegalStateException("El visor esta cerrado."); }
        if (SwingUtilities.isEventDispatchThread()) {
            pausa();
            ejecutar(()->cargarArchivos(ruta,referencia));
        } else {
            SwingUtilities.invokeAndWait(this::pausa);
            pendientes.incrementAndGet();
            var carga=tareas.submit(()->{
                try { cargarArchivos(ruta,referencia); }
                finally { pendientes.decrementAndGet(); }
                return null;
            });
            try { carga.get(); }
            catch (java.util.concurrent.ExecutionException error) {
                if (error.getCause() instanceof Exception causa) { throw causa; }
                throw error;
            }
        }
    }
    private void cargarArchivos(Path ruta,boolean referencia) throws Exception {
        // Ambas validaciones terminan antes de sustituir el escenario visible.
        ruta=ruta.toRealPath();
        var serie=new LectorCsv().leer(ruta);
        new LectorIndividuos().validar(ruta,serie);
        netlogo.ordenar((referencia?"cargar-referencia-desde ":"cargar-java-desde ")+PuenteNetLogo.texto(ruta.toAbsolutePath().toString()));
        if (!referencia) {
            try { leerParametros(ruta); }
            catch (java.io.IOException | IllegalArgumentException e) { mensaje("CSV valido; parametros auxiliares no disponibles: "+e.getMessage()); }
        }
    }
    private void leerParametros(Path csv) throws java.io.IOException {
        String nombre=csv.getFileName().toString();
        if (!nombre.toLowerCase(java.util.Locale.ROOT).endsWith(".csv") || nombre.length() <= 4) { return; }
        Path archivo=csv.resolveSibling(nombre.substring(0,nombre.length()-4)+".properties");
        java.util.Properties propiedades=new java.util.Properties();
        if (java.nio.file.Files.isRegularFile(archivo) && java.nio.file.Files.size(archivo)<8192) {
            try (var lector=java.nio.file.Files.newBufferedReader(archivo)) { propiedades.load(lector); }
            SwingUtilities.invokeLater(()->campos.forEach((clave,campo)->{
                if (propiedades.containsKey(clave)) { campo.setText(propiedades.getProperty(clave)); }
            }));
        }
    }
    private void generar() {
        pausa();
        long revision=revisionReproduccion;
        java.util.List<String> args=new java.util.ArrayList<>();
        campos.forEach((nombre,campo)->{ args.add("--"+nombre); args.add(campo.getText().trim()); });
        try {
            Opciones opciones=Opciones.leer(args.toArray(String[]::new),raiz);
            enMarcha=true; reproducir.setText("PAUSAR");
            ejecutar(()->{
                new ControladorSIR(new ExportadorCsv()).ejecutar(opciones.parametros(),opciones.semilla(),opciones.csv());
                cargarArchivos(opciones.csv(),false);
                iniciarSiVigente(revision);
            });
        } catch (Exception e) { mensaje("Entrada invalida: "+e.getMessage()); }
    }
    private void exportar() {
        pausa();
        ejecutar(()->{
            Path carpeta=raiz.resolve("resultados"); java.nio.file.Files.createDirectories(carpeta);
            Path salida=carpeta.resolve("netlogo_"+java.util.UUID.randomUUID().toString().substring(0,8)+".png");
            // Cada grafica se obtiene del motor NetLogo, no se recalculan puntos.
            final java.awt.image.BufferedImage[] imagen={null};
            SwingUtilities.invokeAndWait(()->{
                Component vista=netlogo.componente(); imagen[0]=new java.awt.image.BufferedImage(vista.getWidth(),vista.getHeight(),java.awt.image.BufferedImage.TYPE_INT_RGB);
                Graphics2D g=imagen[0].createGraphics(); try { vista.printAll(g); } finally { g.dispose(); }
            });
            javax.imageio.ImageIO.write(imagen[0],"png",salida.toFile());
            netlogo.ordenar("set estado-mensaje "+PuenteNetLogo.texto("Vista guardada: "+salida.getFileName()));
        });
    }
    @FunctionalInterface private interface Trabajo { void ejecutar() throws Exception; }
    private void ejecutar(Trabajo trabajo) {
        if (cerrado) { return; }
        pendientes.incrementAndGet();
        tareas.submit(()->{
            try {
                if (cerrado) { return; }
                trabajo.ejecutar(); mensaje(String.valueOf(netlogo.consultar("estado-mensaje")));
            }
            catch (Exception e) { mensaje("No se aplico: "+e.getMessage()); SwingUtilities.invokeLater(this::pausa); }
            finally { pendientes.decrementAndGet(); }
        });
    }
    private void mensaje(String texto) {
        SwingUtilities.invokeLater(()->{ estado.setText(texto.length()>85?texto.substring(0,82)+"...":texto); estado.setToolTipText(texto); });
        if (texto.startsWith("No se aplico") || texto.startsWith("Entrada invalida")) { System.err.println(texto); }
    }
    private void cerrar() {
        if (cerrado) { return; } cerrado=true; pausa();
        tareas.submit(()->{ try { netlogo.cerrar(); } catch (Exception e) { System.err.println(e.getMessage()); }
            finally { tareas.shutdown(); SwingUtilities.invokeLater(this::dispose); } });
    }
    public PuenteNetLogo puente() { return netlogo; }
    public boolean ocupado() { return pendientes.get()!=0; }
    public static void main(String[] args) throws Exception {
        UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        SwingUtilities.invokeAndWait(()->{
            try { new VentanaSimulacion(Path.of(args[0]),Path.of(args[1])).setVisible(true); }
            catch (Exception e) { e.printStackTrace(); System.exit(1); }
        });
    }
}
