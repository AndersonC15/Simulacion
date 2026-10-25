package sir.pruebas;

import sir.view.VentanaSimulacion;
import sir.model.ResultadoPaso;
import java.awt.*;
import java.awt.event.WindowEvent;
import java.nio.file.*;
import java.util.List;
import java.util.ArrayList;
import javax.swing.*;
import javax.imageio.ImageIO;

/** Ejecuta los botones reales de Swing con un motor grafico NetLogo 7.0.4. */
@org.junit.jupiter.api.TestInstance(org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS)
final class VisorGuiIT {
    VentanaSimulacion ventana;
    Path raiz;
    @org.junit.jupiter.api.io.TempDir Path temporal;
    final List<org.junit.jupiter.api.DynamicTest> pruebas=new ArrayList<>();
    @FunctionalInterface interface Caso{void ejecutar()throws Exception;}
    void caso(String nombre,Caso accion) {
        pruebas.add(org.junit.jupiter.api.DynamicTest.dynamicTest(nombre,accion::ejecutar));
    }
    void exigir(boolean condicion){if(!condicion)throw new AssertionError("Resultado inesperado.");}
    Component buscar(Component c,String nombre){
        if(nombre.equals(c.getName()))return c;
        if(c instanceof Container)for(Component h:((Container)c).getComponents()){Component r=buscar(h,nombre);if(r!=null)return r;}
        return null;
    }
    void click(String nombre)throws Exception{SwingUtilities.invokeAndWait(()->((JButton)buscar(ventana,nombre)).doClick());}
    void campo(String nombre,String valor)throws Exception{SwingUtilities.invokeAndWait(()->((JTextField)buscar(ventana,nombre)).setText(valor));}
    void listo()throws Exception{
        long fin=System.nanoTime()+15_000_000_000L;
        while(ventana.ocupado()&&System.nanoTime()<fin)Thread.sleep(10);
        exigir(!ventana.ocupado());SwingUtilities.invokeAndWait(()->{});
    }
    double indice()throws Exception{return ((Number)ventana.puente().consultar("indice")).doubleValue();}
    void pausar()throws Exception{JButton b=(JButton)buscar(ventana,"PAUSAR");if(b.getText().equals("PAUSAR")){click("PAUSAR");}listo();}
    void foto(String nombre)throws Exception{
        Robot robot=new Robot();robot.mouseMove(3,3);robot.waitForIdle();Thread.sleep(150);
        var imagen=robot.createScreenCapture(new Rectangle(ventana.getLocationOnScreen(),ventana.getSize()));
        ImageIO.write(imagen,"png",raiz.resolve("resultados/"+nombre).toFile());
    }
    @org.junit.jupiter.api.TestFactory
    List<org.junit.jupiter.api.DynamicTest> casos() throws Exception {
        org.junit.jupiter.api.Assertions.assertFalse(GraphicsEnvironment.isHeadless(),"El perfil gui requiere una pantalla X11 disponible.");
        raiz=temporal;
        Path original=Path.of(System.getProperty("sir.proyecto",System.getProperty("user.dir")));
        Files.createDirectories(raiz.resolve("netlogo/datos"));
        Files.createDirectories(raiz.resolve("resultados"));
        try(var archivos=Files.list(original.resolve("netlogo"))) {
            for(Path f:archivos.filter(Files::isRegularFile).toList()) {
                if(f.toString().endsWith(".nls")||f.toString().endsWith(".nlogox"))Files.copy(f,raiz.resolve("netlogo").resolve(f.getFileName()));
            }
        }
        var controlador=new sir.controller.ControladorSIR(new sir.io.ExportadorCsv());
        controlador.ejecutar(new sir.model.ParametrosSIR(),42,raiz.resolve("netlogo/datos/resultados_java.csv"));
        controlador.ejecutar(new sir.model.ParametrosSIR(),7,raiz.resolve("netlogo/datos/otra_semilla.csv"));
            SwingUtilities.invokeAndWait(()->{try{ventana=new VentanaSimulacion(raiz,raiz.resolve("netlogo/datos/resultados_java.csv"));ventana.setVisible(true);}catch(Exception e){throw new RuntimeException(e);}});
            listo();Thread.sleep(450);pausar();
            caso("Ventana abre y anima automaticamente",()->exigir(indice()>0&&indice()<100));
            caso("Sin pestanas de editor/Informacion",()->exigir(!hayPestanas(ventana)));
            caso("Pausa conserva el paso",()->{double t=indice();Thread.sleep(300);listo();exigir(indice()==t);});
            caso("Reiniciar muestra t=0",()->{click("REINICIAR");listo();exigir(indice()==0);});
            caso("Un paso llega a t=1",()->{click("UN PASO");listo();exigir(indice()==1);});
            caso("Continuar avanza desde el paso pausado",()->{click("PAUSAR");Thread.sleep(400);pausar();exigir(indice()>1);});
            caso("Ver completo llega al ultimo registro",()->{click("VER COMPLETO");listo();exigir(indice()==100);foto("vista_netlogo.png");});
            caso("Un paso al final no excede 100",()->{click("UN PASO");listo();exigir(indice()==100);});
            caso("Continuar al final reinicia y reproduce",()->{click("PAUSAR");Thread.sleep(400);pausar();exigir(indice()>0&&indice()<100);});
            caso("Reiniciar varias veces no acumula curvas",()->{for(int i=0;i<20;i++){click("REINICIAR");listo();}exigir(indice()==0);});
            caso("Velocidad minima permitida",()->SwingUtilities.invokeAndWait(()->{JSlider s=(JSlider)buscar(ventana,"velocidad");s.setValue(20);exigir(s.getValue()==20);}));
            caso("Velocidad maxima permitida",()->SwingUtilities.invokeAndWait(()->{JSlider s=(JSlider)buscar(ventana,"velocidad");s.setValue(500);exigir(s.getValue()==500);}));
            caso("Interfaz rechaza beta=2.9999",()->{campo("beta","2.9999");Object antes=ventana.puente().consultar("datos-java");click("GENERAR ESCENARIO");listo();exigir(antes.equals(ventana.puente().consultar("datos-java")));});
            caso("Interfaz rechaza gamma=3",()->{campo("beta",".3");campo("gamma","3");Object antes=ventana.puente().consultar("datos-java");click("GENERAR ESCENARIO");listo();exigir(antes.equals(ventana.puente().consultar("datos-java")));});
            caso("Interfaz rechaza campo vacio",()->{campo("gamma",".1");campo("poblacion","");Object antes=ventana.puente().consultar("datos-java");click("GENERAR ESCENARIO");listo();exigir(antes.equals(ventana.puente().consultar("datos-java")));});
            caso("Interfaz rechaza I0 mayor que N",()->{campo("poblacion","1");campo("infectados","5");click("GENERAR ESCENARIO");listo();exigir(ventana.puente().consultar("length datos-java").equals(101.0));});
            caso("Interfaz rechaza NaN",()->{campo("poblacion","100");campo("beta","NaN");click("GENERAR ESCENARIO");listo();exigir(ventana.puente().consultar("length datos-java").equals(101.0));});
            caso("Interfaz genera escenario sin recuperacion",()->{campo("beta",".3");campo("gamma","0");click("GENERAR ESCENARIO");listo();pausar();exigir(ventana.puente().consultar("not member? false (map [fila -> item 3 fila = 0] datos-java)").equals(true));});
            caso("Interfaz genera horizonte cero y conserva un registro",()->{campo("gamma",".1");campo("pasos","0");click("GENERAR ESCENARIO");listo();pausar();exigir(ventana.puente().consultar("length datos-java = 1 and indice = 0").equals(true));});
            caso("Comparacion usa otro CSV Java con distinta semilla",()->{ventana.cargar(raiz.resolve("netlogo/datos/resultados_java.csv"),false);ventana.cargar(raiz.resolve("netlogo/datos/otra_semilla.csv"),true);click("VER COMPLETO");listo();exigir(ventana.puente().consultar("length datos-referencia = 101 and item 1 last datos-referencia = 9").equals(true));foto("comparacion_netlogo.png");});
            caso("Quitar comparacion borra solo escenario B",()->{click("QUITAR COMPARACION");listo();exigir(ventana.puente().consultar("empty? datos-referencia and length datos-java = 101").equals(true));});
            caso("CSV invalido preserva vista anterior",()->{Path f=Files.createTempFile(temporal,"mal-",".csv");Files.writeString(f,"mal\n");Object antes=ventana.puente().consultar("datos-java");try{ventana.cargar(f,false);throw new AssertionError("CSV invalido aceptado");}catch(java.io.IOException esperado){}exigir(antes.equals(ventana.puente().consultar("datos-java")));});
            caso("Parametros auxiliares corruptos no impiden visualizar CSV valido",()->{
                Path dir=Files.createTempDirectory(temporal,"sir-props-");Path f=dir.resolve("datos.csv");Files.writeString(f,"tiempo,susceptibles,infectados,recuperados\n0,95,5,0\n");Files.writeString(dir.resolve("datos.properties"),"beta=\\uXXXX\n");
                ventana.cargar(f,false);exigir(ventana.puente().consultar("length datos-java").equals(1.0));
            });
            caso("Archivo con contenido CSV y extension txt no rompe metadatos",()->{
                Path f=Files.createTempFile(temporal,"datos-",".txt");Files.writeString(f,"tiempo,susceptibles,infectados,recuperados\n0,95,5,0\n");ventana.cargar(f,false);exigir(ventana.puente().consultar("length datos-java").equals(1.0));
            });
            caso("Cancelar selector de CSV conserva datos y ventana",()->{
                Object antes=ventana.puente().consultar("datos-java");SwingUtilities.invokeLater(()->((JButton)buscar(ventana,"ABRIR CSV")).doClick());
                long limite=System.nanoTime()+3000000000L;JFileChooser[] selector={null};
                while(selector[0]==null&&System.nanoTime()<limite){SwingUtilities.invokeAndWait(()->{for(Window w:Window.getWindows()){if(w.isShowing())selector[0]=encontrarSelector(w);}});Thread.sleep(10);}
                exigir(selector[0]!=null);SwingUtilities.invokeAndWait(()->selector[0].cancelSelection());listo();exigir(antes.equals(ventana.puente().consultar("datos-java")));
            });
            caso("Redimensionar ventana mantiene componentes",()->{SwingUtilities.invokeAndWait(()->ventana.setSize(900,650));exigir(ventana.isDisplayable());SwingUtilities.invokeAndWait(()->ventana.setSize(1270,920));});
            caso("Guardar vista crea PNG valido",()->{long antes;try(var s=Files.list(raiz.resolve("resultados"))){antes=s.filter(p->p.getFileName().toString().startsWith("netlogo_")).count();}click("GUARDAR VISTA PNG");listo();try(var s=Files.list(raiz.resolve("resultados"))){exigir(s.filter(p->p.getFileName().toString().startsWith("netlogo_")).count()==antes+1);}});
            caso("Rafaga de botones durante reproduccion no rompe el visor",()->{ventana.cargar(raiz.resolve("netlogo/datos/resultados_java.csv"),false);for(int i=0;i<30;i++){click(i%2==0?"VER COMPLETO":"REINICIAR");}listo();click("VER COMPLETO");listo();exigir(indice()==100);});
        caso("Ctrl+Q cierra ventana y libera trabajador",()->{
            SwingUtilities.invokeAndWait(()->{
                var mapa=ventana.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW);
                Object clave=mapa.get(KeyStroke.getKeyStroke("control Q"));
                exigir(clave!=null);
                ventana.getRootPane().getActionMap().get(clave).actionPerformed(new java.awt.event.ActionEvent(ventana,0,"control Q"));
            });
            long limite=System.nanoTime()+15_000_000_000L;
            while(ventana.isDisplayable()&&System.nanoTime()<limite)Thread.sleep(10);
            exigir(!ventana.isDisplayable());
        });
        return pruebas;
    }
    @org.junit.jupiter.api.AfterAll void cerrar() throws Exception {
        if(ventana!=null&&ventana.isDisplayable()) {
            SwingUtilities.invokeAndWait(()->ventana.dispatchEvent(new WindowEvent(ventana,WindowEvent.WINDOW_CLOSING)));
            long limite=System.nanoTime()+15_000_000_000L;
            while(ventana.isDisplayable()&&System.nanoTime()<limite)Thread.sleep(10);
            exigir(!ventana.isDisplayable());
        }
    }
    boolean hayPestanas(Component c){if(c instanceof JTabbedPane)return true;if(c instanceof Container)for(Component h:((Container)c).getComponents())if(hayPestanas(h))return true;return false;}
    JFileChooser encontrarSelector(Component c){if(c instanceof JFileChooser)return (JFileChooser)c;if(c instanceof Container)for(Component h:((Container)c).getComponents()){JFileChooser r=encontrarSelector(h);if(r!=null)return r;}return null;}
}
