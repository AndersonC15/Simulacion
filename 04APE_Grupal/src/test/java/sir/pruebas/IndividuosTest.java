package sir.pruebas;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.io.TempDir;
import sir.controller.ControladorSIR;
import sir.io.ExportadorCsv;
import sir.io.LectorCsv;
import sir.io.LectorIndividuos;
import sir.model.ParametrosSIR;
import sir.model.ResultadoPaso;

import static org.junit.jupiter.api.Assertions.*;

final class IndividuosTest {
    @TempDir Path temporal;
    private static final String CABECERA="tiempo,id,estado\n";
    private static final String DETALLE=CABECERA
            +"0,0,INFECTADO\n0,1,SUSCEPTIBLE\n0,2,SUSCEPTIBLE\n"
            +"1,0,RECUPERADO\n1,1,INFECTADO\n1,2,SUSCEPTIBLE\n"
            +"2,0,RECUPERADO\n2,1,INFECTADO\n2,2,INFECTADO\n"
            +"3,0,RECUPERADO\n3,1,RECUPERADO\n3,2,INFECTADO\n";
    private static final List<ResultadoPaso> SERIE=List.of(
            new ResultadoPaso(0,2,1,0),new ResultadoPaso(1,1,1,1),
            new ResultadoPaso(2,0,2,1),new ResultadoPaso(3,0,1,2));

    private Path agregado(String nombre) throws IOException {
        Path archivo=temporal.resolve(nombre+".csv");
        new ExportadorCsv().exportar(SERIE,archivo);
        return archivo;
    }
    private Path detalle(Path agregado,String contenido) throws IOException {
        Path detalle=LectorIndividuos.rutaCompanera(agregado);
        Files.writeString(detalle,contenido);
        return detalle;
    }
    @Test void aceptaDetalleRealCoherenteYNoModificaArchivos() throws Exception {
        Path agregado=agregado("correcto");
        Path detalle=detalle(agregado,DETALLE);
        assertEquals(detalle,new LectorIndividuos().validar(agregado,SERIE));
        assertEquals(DETALLE,Files.readString(detalle));
        assertEquals(SERIE.stream().map(ResultadoPaso::aCsv).toList(),
                new LectorCsv().leer(agregado).stream().map(ResultadoPaso::aCsv).toList());
    }
    @Test void csvAntiguoSinDetalleSigueDisponibleYNoInventaIdentidades() throws Exception {
        Path agregado=agregado("legado");
        assertNull(new LectorIndividuos().validar(agregado,SERIE));
        assertFalse(Files.exists(LectorIndividuos.rutaCompanera(agregado)));
        assertEquals(4,new LectorCsv().leer(agregado).size());
    }
    @Test void aceptaBomCrlfYUltimaLineaSinSalto() throws Exception {
        Path agregado=agregado("portable");
        String portable="\uFEFF"+DETALLE.stripTrailing().replace("\n","\r\n");
        Path archivo=detalle(agregado,portable);
        assertEquals(archivo,new LectorIndividuos().validar(agregado,SERIE));
    }
    @Test void huellaDetectaDetalleSustituidoAunqueSusConteosCoincidan() throws Exception {
        Path agregado=temporal.resolve("identidad.csv");
        var serie=new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(2,1,.3,.1,0,1),42,agregado);
        Path archivo=LectorIndividuos.rutaCompanera(agregado);
        String original=Files.readString(archivo);
        String sustituido=original.replace("INFECTADO","CAMBIO").replace("SUSCEPTIBLE","INFECTADO").replace("CAMBIO","SUSCEPTIBLE");
        assertNotEquals(original,sustituido);Files.writeString(archivo,sustituido);
        assertThrows(IOException.class,()->new LectorIndividuos().validar(agregado,serie));
        assertEquals(sustituido,Files.readString(archivo));
    }
    @TestFactory List<DynamicTest> rechazosIndividuales() {
        Map<String,String> malos=new LinkedHashMap<>();
        malos.put("vacio","");
        malos.put("solo encabezado",CABECERA);
        malos.put("encabezado agregado",DETALLE.replace("tiempo,id,estado","tiempo,susceptibles,infectados,recuperados"));
        malos.put("encabezado reordenado",DETALLE.replace("tiempo,id,estado","id,tiempo,estado"));
        malos.put("separador incorrecto",DETALLE.replace(',',';'));
        malos.put("ID negativo",DETALLE.replace("0,0,INFECTADO","0,-1,INFECTADO"));
        malos.put("ID fuera de poblacion",DETALLE.replace("0,2,SUSCEPTIBLE","0,3,SUSCEPTIBLE"));
        malos.put("ID duplicado",DETALLE.replace("0,1,SUSCEPTIBLE","0,0,SUSCEPTIBLE"));
        malos.put("ID fraccionario",DETALLE.replace("0,1,SUSCEPTIBLE","0,1.0,SUSCEPTIBLE"));
        malos.put("ID desbordado",DETALLE.replace("0,1,SUSCEPTIBLE","0,2147483648,SUSCEPTIBLE"));
        malos.put("IDs sin orden",DETALLE.replace("0,1,SUSCEPTIBLE\n0,2,SUSCEPTIBLE","0,2,SUSCEPTIBLE\n0,1,SUSCEPTIBLE"));
        malos.put("estado desconocido",DETALLE.replace("0,0,INFECTADO","0,0,ENFERMO"));
        malos.put("estado vacio",DETALLE.replace("0,0,INFECTADO","0,0,"));
        malos.put("individuo ausente",DETALLE.replace("1,2,SUSCEPTIBLE\n",""));
        malos.put("paso ausente",DETALLE.replace("1,0,RECUPERADO\n1,1,INFECTADO\n1,2,SUSCEPTIBLE\n",""));
        malos.put("tiempo inicial uno",DETALLE.replace("0,","1,"));
        malos.put("tiempo con salto",DETALLE.replace("2,0,RECUPERADO","3,0,RECUPERADO"));
        malos.put("tiempo retrocede",DETALLE.replace("2,0,RECUPERADO","0,0,RECUPERADO"));
        malos.put("tiempo negativo",DETALLE.replace("0,0,INFECTADO","-1,0,INFECTADO"));
        malos.put("fila extra",DETALLE+"4,0,RECUPERADO\n");
        malos.put("truncado",DETALLE.substring(0,DETALLE.lastIndexOf("3,2,")));
        malos.put("columna extra",DETALLE.replace("0,0,INFECTADO","0,0,INFECTADO,extra"));
        malos.put("fila vacia",DETALLE.replace("1,0,RECUPERADO","\n1,0,RECUPERADO"));
        malos.put("conteos de otra ejecucion",DETALLE.replace("1,1,INFECTADO","1,1,SUSCEPTIBLE"));
        malos.put("R vuelve a I con mismos conteos",DETALLE.replace("2,0,RECUPERADO\n2,1,INFECTADO","2,0,INFECTADO\n2,1,RECUPERADO"));
        malos.put("S pasa directamente a R con mismos conteos",DETALLE.replace("1,0,RECUPERADO\n1,1,INFECTADO\n1,2,SUSCEPTIBLE","1,0,SUSCEPTIBLE\n1,1,INFECTADO\n1,2,RECUPERADO"));
        malos.put("linea excesiva",DETALLE.replace("0,0,INFECTADO","0,0,"+"X".repeat(300)));
        List<DynamicTest> casos=new ArrayList<>();
        for(var caso:malos.entrySet())casos.add(DynamicTest.dynamicTest(caso.getKey(),()->{
            Path agregado=agregado("invalido_"+casosNombre(caso.getKey()));
            Path archivo=detalle(agregado,caso.getValue());
            assertThrows(IOException.class,()->new LectorIndividuos().validar(agregado,SERIE));
            assertEquals(caso.getValue(),Files.readString(archivo));
            assertEquals(4,new LectorCsv().leer(agregado).size());
        }));
        return casos;
    }
    private String casosNombre(String s) { return s.replaceAll("[^a-zA-Z0-9]","_"); }
    @Test void rechazaCodificacionUtf8Corrupta() throws Exception {
        Path agregado=agregado("utf8");
        Files.write(LectorIndividuos.rutaCompanera(agregado),new byte[]{(byte)0xc3,(byte)0x28});
        assertThrows(IOException.class,()->new LectorIndividuos().validar(agregado,SERIE));
    }
    @Test void rechazaCompaneroQueEsDirectorio() throws Exception {
        Path agregado=agregado("directorio");
        Files.createDirectory(LectorIndividuos.rutaCompanera(agregado));
        assertThrows(IOException.class,()->new LectorIndividuos().validar(agregado,SERIE));
    }
    @Test void rechazaArchivoSuperiorAlLimiteAntesDeLeerlo() throws Exception {
        Path agregado=agregado("enorme");
        Path archivo=LectorIndividuos.rutaCompanera(agregado);
        try(var canal=FileChannel.open(archivo,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)) {
            canal.position(512L*1024*1024); canal.write(ByteBuffer.wrap(new byte[]{0}));
        }
        assertThrows(IOException.class,()->new LectorIndividuos().validar(agregado,SERIE));
    }
    @Test void exporta10100RegistrosConIdentidadConteosYTransicionesReales() throws Exception {
        Path salida=temporal.resolve("ejecucion.csv");
        List<ResultadoPaso> serie=new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,salida);
        assertEquals(LectorIndividuos.rutaCompanera(salida),new LectorIndividuos().validar(salida,serie));
        try(var lector=Files.newBufferedReader(LectorIndividuos.rutaCompanera(salida))) {
            assertEquals("tiempo,id,estado",lector.readLine());
            String[] anteriores=new String[100]; int filas=0;
            for(ResultadoPaso paso:serie) {
                int s=0,i=0,r=0;
                for(int id=0;id<100;id++) {
                    String fila=lector.readLine(); assertNotNull(fila);
                    String[] valores=fila.split(",",-1);
                    assertEquals(3,valores.length); assertEquals(paso.getTiempo(),Integer.parseInt(valores[0]));
                    assertEquals(id,Integer.parseInt(valores[1]));
                    switch(valores[2]) {case "SUSCEPTIBLE" -> s++;case "INFECTADO" -> i++;case "RECUPERADO" -> r++;default -> fail("Estado desconocido");}
                    if(anteriores[id]!=null) {
                        assertFalse(anteriores[id].equals("RECUPERADO")&&!valores[2].equals("RECUPERADO"));
                        assertFalse(anteriores[id].equals("INFECTADO")&&valores[2].equals("SUSCEPTIBLE"));
                        assertFalse(anteriores[id].equals("SUSCEPTIBLE")&&valores[2].equals("RECUPERADO"));
                    }
                    anteriores[id]=valores[2]; filas++;
                }
                assertEquals(paso.getSusceptibles(),s);assertEquals(paso.getInfectados(),i);assertEquals(paso.getRecuperados(),r);
            }
            assertEquals(10100,filas);assertNull(lector.readLine());
        }
        assertEquals("100,4,0,96",serie.getLast().aCsv());
    }
    @Test void exportacionDeterministaIncluyeHorizonteCeroYSinInfectados() throws Exception {
        var p=new ParametrosSIR(1,0,1,1,0,1);
        Path uno=temporal.resolve("cero.csv"),dos=temporal.resolve("repetida.csv");
        var controlador=new ControladorSIR(new ExportadorCsv());
        controlador.ejecutar(p,42,uno);controlador.ejecutar(p,42,dos);
        assertEquals("tiempo,id,estado\n0,0,SUSCEPTIBLE\n",Files.readString(LectorIndividuos.rutaCompanera(uno)));
        assertEquals(Files.readString(LectorIndividuos.rutaCompanera(uno)),Files.readString(LectorIndividuos.rutaCompanera(dos)));
    }
    @TestFactory List<DynamicTest> protegeLasCuatroSalidasExistentes() {
        return List.of(".csv",".png",".properties","_individuos.csv").stream().map(extension->DynamicTest.dynamicTest(extension,()->{
            Path dir=Files.createTempDirectory(temporal,"existente-");
            Path existente=dir.resolve("datos"+extension);Files.writeString(existente,"contenido del usuario");
            assertThrows(IOException.class,()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,dir.resolve("datos.csv")));
            assertEquals("contenido del usuario",Files.readString(existente));
            try(var archivos=Files.list(dir)){assertEquals(List.of(existente),archivos.toList());}
        })).toList();
    }
    @Test void falloNoDejaNingunaDeLasCuatroSalidasNiReservas() throws Exception {
        Path salida=temporal.resolve("fallo.csv");
        var controlador=new ControladorSIR((serie,ruta)->{Files.writeString(ruta,"parcial");throw new IOException("Fallo inducido en CSV");});
        assertThrows(IOException.class,()->controlador.ejecutar(new ParametrosSIR(),42,salida));
        try(var archivos=Files.list(temporal)){assertEquals(0,archivos.count());}
    }
    @Test void destinosQueCompartenArchivoIndividualNoSeSobrescriben() throws Exception {
        Path uno=temporal.resolve("compartido.csv"),dos=temporal.resolve("compartido_individuos.csv");
        CountDownLatch inicio=new CountDownLatch(1);
        var pool=Executors.newFixedThreadPool(2);
        try {
            List<Future<Boolean>> resultados=new ArrayList<>();
            for(Path salida:List.of(uno,dos))resultados.add(pool.submit(()->{
                inicio.await();try{new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,salida);return true;}catch(IOException esperado){return false;}
            }));
            inicio.countDown();int exitos=0;for(var resultado:resultados)if(resultado.get(20,TimeUnit.SECONDS))exitos++;
            assertEquals(1,exitos);
            if(Files.exists(uno))assertNotNull(new LectorIndividuos().validar(uno,new LectorCsv().leer(uno)));
            else assertNotNull(new LectorIndividuos().validar(dos,new LectorCsv().leer(dos)));
            try(var archivos=Files.list(temporal)){assertEquals(4,archivos.count());}
        }finally{pool.shutdownNow();}
    }
}
