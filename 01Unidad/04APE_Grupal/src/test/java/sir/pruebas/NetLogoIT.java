package sir.pruebas;

import java.nio.file.Path;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.TreeMap;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.io.TempDir;
import sir.controller.ControladorSIR;
import sir.io.ExportadorCsv;
import sir.io.LectorIndividuos;
import sir.model.ParametrosSIR;
import sir.view.PuenteNetLogo;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
final class NetLogoIT {
    @TempDir Path temporal;
    private CasosRegresion casos;
    @TestFactory List<DynamicTest> casos() throws Exception {
        String home=System.getProperty("netlogo.home",System.getenv().getOrDefault("NETLOGO_HOME",""));
        org.junit.jupiter.api.Assumptions.assumeTrue(!home.isBlank()&&Files.isRegularFile(Path.of(home,"lib/app/netlogo-7.0.4.jar")),
                "NetLogoIT no ejecutado: configura -Dnetlogo.home con una instalacion local de NetLogo 7.0.4.");
        casos=new CasosRegresion(temporal);
        casos.netlogo();
        personas();
        return casos.pruebas;
    }
    private void personas() throws Exception {
        var controlador=new ControladorSIR(new ExportadorCsv());
        Path a=temporal.resolve("personas A.csv"),b=temporal.resolve("personas B.csv");
        controlador.ejecutar(new ParametrosSIR(6,2,.8,.25,5,1),42,a);
        controlador.ejecutar(new ParametrosSIR(3,1,.2,.8,2,1),7,b);
        casos.caso("Personas A corresponden a los IDs y estados Java de t0",()->{
            cargar(a,b);verificarPersonas("A",a,0);verificarPersonas("B",b,0);
            assertEquals(true,casos.rep("detalle-a? and detalle-b?"));
            assertEquals(true,casos.rep("all? personas with [ejecucion = \"A\"] [xcor < 100] and all? personas with [ejecucion = \"B\"] [xcor >= 100]"));
        });
        casos.caso("La paleta de personas conserva los tres colores de las curvas",()->{
            assertEquals(true,casos.rep("color-estado \"SUSCEPTIBLE\" = [0 171 77]"));
            assertEquals(true,casos.rep("color-estado \"INFECTADO\" = [11 18 32]"));
            assertEquals(true,casos.rep("color-estado \"RECUPERADO\" = [130 154 144]"));
            assertEquals(true,casos.rep("all? personas [color != [pcolor] of patch-here]"));
        });
        casos.caso("Un avance sincroniza personas y filas de A y B",()->{
            cargar(a,b);casos.cmd("avanzar");
            assertEquals(1.0,casos.rep("indice"));verificarPersonas("A",a,1);verificarPersonas("B",b,1);
        });
        casos.caso("Completo conserva ultimo estado de B con horizonte menor",()->{
            cargar(a,b);casos.cmd("mostrar-completo repeat 100 [avanzar]");
            assertEquals(5.0,casos.rep("indice"));verificarPersonas("A",a,5);verificarPersonas("B",b,2);
            assertEquals(true,casos.rep("valor-java 0 = 5 and valor-referencia 0 = 2"));
        });
        casos.caso("Reiniciar restaura personas t0 y posiciones deterministas",()->{
            cargar(a,b);Object posiciones=casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [xcor] of p [ycor] of p)] sort personas");
            casos.cmd("mostrar-completo reiniciar");
            verificarPersonas("A",a,0);verificarPersonas("B",b,0);
            assertEquals(posiciones,casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [xcor] of p [ycor] of p)] sort personas"));
        });
        casos.caso("Retirar B elimina solo sus personas y conserva estado A",()->{
            cargar(a,b);casos.cmd("avanzar quitar-referencia");
            assertEquals(0.0,casos.rep("count personas with [ejecucion = \"B\"]"));
            verificarPersonas("A",a,1);assertEquals(false,casos.rep("detalle-b?"));
        });
        casos.caso("Mismo archivo en A y B mantiene lectores e identidades independientes",()->{
            cargar(a,a);
            verificarPersonas("A",a,0);verificarPersonas("B",a,0);
            casos.cmd("avanzar");verificarPersonas("A",a,1);verificarPersonas("B",a,1);
            casos.cmd("mostrar-completo");verificarPersonas("A",a,5);verificarPersonas("B",a,5);
            casos.cmd("reiniciar avanzar");verificarPersonas("A",a,1);verificarPersonas("B",a,1);
        });
        casos.caso("CSV antiguo conserva curvas e indica ausencia de personas",()->{
            casos.cmd("cargar-java-desde \"datos/resultados_java.csv\" quitar-referencia");
            assertEquals(101.0,casos.rep("length datos-java"));assertEquals(false,casos.rep("detalle-a?"));
            assertEquals(0.0,casos.rep("count personas with [ejecucion = \"A\"]"));
        });
        casos.caso("Detalle individual corrupto conserva vista previa completa",()->{
            cargar(a,b);casos.cmd("avanzar");Object datos=casos.rep("datos-java"),personas=casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [estado-persona] of p)] sort personas");
            Path malo=temporal.resolve("corrupto.csv");Files.copy(a,malo);Files.writeString(LectorIndividuos.rutaCompanera(malo),"tiempo,id,estado\n0,0,DESCONOCIDO\n");
            assertThrows(Exception.class,()->casos.cmd("cargar-java-desde "+PuenteNetLogo.texto(malo.toString())));
            assertEquals(datos,casos.rep("datos-java"));assertEquals(personas,casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [estado-persona] of p)] sort personas"));assertEquals(1.0,casos.rep("indice"));
            casos.cmd("avanzar");verificarPersonas("A",a,2);verificarPersonas("B",b,2);
        });
        casos.caso("Seleccionar CSV individual como agregado conserva vista",()->{
            cargar(a,b);Object datos=casos.rep("datos-java");
            assertThrows(Exception.class,()->casos.cmd("cargar-java-desde "+PuenteNetLogo.texto(LectorIndividuos.rutaCompanera(a).toString())));
            assertEquals(datos,casos.rep("datos-java"));verificarPersonas("A",a,0);
        });
        String original=Files.readString(LectorIndividuos.rutaCompanera(a));
        Map<String,String> invalidos=new LinkedHashMap<>();
        invalidos.put("vacio","");
        invalidos.put("solo encabezado","tiempo,id,estado\n");
        invalidos.put("encabezado incorrecto",original.replace("tiempo,id,estado","id,tiempo,estado"));
        invalidos.put("ID negativo",original.replaceFirst("0,0,","0,-1,"));
        invalidos.put("ID duplicado",original.replaceFirst("0,1,","0,0,"));
        invalidos.put("ID fuera de poblacion",original.replaceFirst("0,0,","0,6,"));
        invalidos.put("ID desbordado",original.replaceFirst("0,0,","0,2147483648,"));
        invalidos.put("estado desconocido",original.replaceFirst("SUSCEPTIBLE|INFECTADO|RECUPERADO","DESCONOCIDO"));
        invalidos.put("individuo ausente",original.replaceFirst("0,0,[A-Z]+\\R",""));
        invalidos.put("tiempo con salto",original.replaceFirst("1,0,","2,0,"));
        invalidos.put("truncado",original.substring(0,original.lastIndexOf("5,5,")));
        invalidos.put("linea fuera de limite",original+"X".repeat(300)+"\n");
        int id=0;
        for(var invalido:invalidos.entrySet()) {
            Path ruta=temporal.resolve("netlogo_individual_invalido_"+(id++)+".csv");
            casos.caso("NetLogo detalle invalido conserva ejecuciones: "+invalido.getKey(),()->{
                cargar(a,b);casos.cmd("avanzar");
                Object datos=casos.rep("datos-java"),personas=casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [estado-persona] of p)] sort personas");
                Files.copy(a,ruta);Files.writeString(LectorIndividuos.rutaCompanera(ruta),invalido.getValue());
                assertThrows(Exception.class,()->casos.cmd("cargar-java-desde "+PuenteNetLogo.texto(ruta.toString())));
                assertEquals(datos,casos.rep("datos-java"));assertEquals(personas,casos.rep("map [p -> (list [ejecucion] of p [identificador] of p [estado-persona] of p)] sort personas"));
                casos.cmd("avanzar");verificarPersonas("A",a,2);verificarPersonas("B",b,2);
            });
        }
    }
    private void cargar(Path a,Path b) throws Exception {
        casos.cmd("cargar-java-desde "+PuenteNetLogo.texto(a.toString())+" cargar-referencia-desde "+PuenteNetLogo.texto(b.toString()));
    }
    private void verificarPersonas(String ejecucion,Path csv,int tiempo) throws Exception {
        Map<Integer,String> esperados=new TreeMap<>();
        try(var lector=Files.newBufferedReader(LectorIndividuos.rutaCompanera(csv))) {
            lector.readLine();String fila;
            while((fila=lector.readLine())!=null) {
                String[] v=fila.split(",");int t=Integer.parseInt(v[0]);
                if(t==tiempo)esperados.put(Integer.parseInt(v[1]),v[2]);
                if(t>tiempo)break;
            }
        }
        String grupo="personas with [ejecucion = \""+ejecucion+"\"]";
        assertEquals((double)esperados.size(),casos.rep("count "+grupo));
        for(var individuo:esperados.entrySet()) {
            String persona="personas with [ejecucion = \""+ejecucion+"\" and identificador = "+individuo.getKey()+"]";
            assertEquals(1.0,casos.rep("count "+persona));
            assertEquals(true,casos.rep("all? "+persona+" [estado-persona = \""+individuo.getValue()+"\" and color = color-estado estado-persona]"));
        }
    }
    @AfterAll void cerrarMotor() throws Exception { if(casos!=null)casos.cerrarNetLogo(); }
}
