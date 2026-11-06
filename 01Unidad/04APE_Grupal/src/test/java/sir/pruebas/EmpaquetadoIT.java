package sir.pruebas;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.jar.JarFile;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import sir.Main;
import sir.io.LectorCsv;
import sir.io.LectorIndividuos;

import static org.junit.jupiter.api.Assertions.*;

/** Ejecuta el JAR empaquetado en otra JVM: los System.exit del CLI quedan aislados. */
final class EmpaquetadoIT {
    @TempDir Path temporal;
    private final Path proyecto=Path.of(System.getProperty("sir.proyecto",System.getProperty("user.dir"))).toAbsolutePath();
    private record Ejecucion(int codigo,String salida) { }
    private Ejecucion ejecutar(Path jar,Path directorio,String... argumentos) throws Exception {
        List<String> comando=new ArrayList<>(List.of(Path.of(System.getProperty("java.home"),"bin","java").toString(),"-jar",jar.toString()));
        comando.addAll(List.of(argumentos));
        Path salida=Files.createTempFile(temporal,"proceso-",".log");
        ProcessBuilder lanzador=new ProcessBuilder(comando).directory(directorio.toFile()).redirectErrorStream(true).redirectOutput(salida.toFile());
        // --sin-netlogo debe generar PNG incluso con una pantalla declarada pero inaccesible.
        lanzador.environment().put("DISPLAY",":987654");
        Process proceso=lanzador.start();
        try {
            assertTrue(proceso.waitFor(30,TimeUnit.SECONDS),"El CLI no termino en 30 segundos");
            return new Ejecucion(proceso.exitValue(),Files.readString(salida));
        }finally{if(proceso.isAlive())proceso.destroyForcibly();}
    }
    private Path copiaConEspacios() throws Exception {
        Path copia=temporal.resolve("proyecto SIR con espacios");
        Files.createDirectories(copia.resolve("target"));Files.createDirectories(copia.resolve("netlogo/datos"));
        Files.copy(proyecto.resolve("pom.xml"),copia.resolve("pom.xml"));
        Files.copy(proyecto.resolve("target/sir.jar"),copia.resolve("target/sir.jar"));
        Files.copy(proyecto.resolve("netlogo/modelo_sir_netlogo.nlogox"),copia.resolve("netlogo/modelo_sir_netlogo.nlogox"));
        return copia;
    }
    private void verificarCuatroSalidas(Path csv,int registros) throws Exception {
        var serie=new LectorCsv().leer(csv);assertEquals(registros,serie.size());
        assertEquals(LectorIndividuos.rutaCompanera(csv),new LectorIndividuos().validar(csv,serie));
        String base=csv.getFileName().toString().replaceFirst("\\.csv$","");
        assertNotNull(javax.imageio.ImageIO.read(csv.resolveSibling(base+".png").toFile()));
        assertTrue(Files.readString(csv.resolveSibling(base+".properties")).contains("semilla=42"));
    }
    @Test void manifestDeclaraClasePrincipalYNoIncluyeDependenciasDePruebas() throws Exception {
        try(JarFile jar=new JarFile(proyecto.resolve("target/sir.jar").toFile())) {
            assertEquals("sir.Main",jar.getManifest().getMainAttributes().getValue("Main-Class"));
            assertNotNull(jar.getEntry("sir/Main.class"));
            assertTrue(jar.stream().noneMatch(e->e.getName().startsWith("sir/pruebas/")||e.getName().startsWith("org/junit/")));
        }
        assertEquals(proyecto.toRealPath(),Main.raiz());
    }
    @Test void jarRelativoFuncionaDesdeRaizYConservaRegresion42() throws Exception {
        Path salida=temporal.resolve("desde raiz.csv");
        Ejecucion resultado=ejecutar(Path.of("target/sir.jar"),proyecto,"--sin-netlogo","--csv",salida.toString());
        assertEquals(0,resultado.codigo,resultado.salida);assertTrue(resultado.salida.contains("final=100,4,0,96"),resultado.salida);
        verificarCuatroSalidas(salida,101);
    }
    @Test void jarAbsolutoConEspaciosFuncionaDesdeOtroDirectorioYUsaDatosDelProyecto() throws Exception {
        Path copia=copiaConEspacios(),externo=Files.createDirectory(temporal.resolve("otro directorio"));
        Ejecucion resultado=ejecutar(copia.resolve("target/sir.jar"),externo,"--sin-netlogo","--poblacion","3","--infectados","1","--pasos","2");
        assertEquals(0,resultado.codigo,resultado.salida);
        List<Path> agregados;
        try(var archivos=Files.list(copia.resolve("netlogo/datos"))) {
            agregados=archivos.filter(f->f.toString().endsWith(".csv")&&!f.toString().endsWith("_individuos.csv")).toList();
        }
        assertEquals(1,agregados.size());verificarCuatroSalidas(agregados.getFirst(),3);
        assertFalse(Files.exists(copia.resolve("target/classes/netlogo")));
        try(var archivos=Files.list(externo)){assertEquals(0,archivos.count());}
    }
    @Test void csvRelativoConEspaciosSeResuelveDesdeDirectorioActual() throws Exception {
        Path copia=copiaConEspacios(),externo=Files.createDirectory(temporal.resolve("directorio externo"));
        Ejecucion resultado=ejecutar(copia.resolve("target/sir.jar"),externo,"--sin-netlogo","--pasos","0","--csv","mis datos/estado inicial.csv");
        assertEquals(0,resultado.codigo,resultado.salida);verificarCuatroSalidas(externo.resolve("mis datos/estado inicial.csv"),1);
    }
    @Test void ayudaNoEjecutaSimulacionYDescribeArtefactoCanonico() throws Exception {
        Path copia=copiaConEspacios();
        Ejecucion resultado=ejecutar(copia.resolve("target/sir.jar"),temporal,"--ayuda");
        assertEquals(0,resultado.codigo);assertTrue(resultado.salida.contains("target/sir.jar"));assertTrue(resultado.salida.contains("_individuos.csv"));
        try(var archivos=Files.list(copia.resolve("netlogo/datos"))){assertEquals(0,archivos.count());}
    }
    @Test void entradaInvalidaDevuelveCodigoNoCeroSinCrearDatos() throws Exception {
        Path copia=copiaConEspacios();
        Ejecucion resultado=ejecutar(copia.resolve("target/sir.jar"),temporal,"--sin-netlogo","--beta","NaN");
        assertNotEquals(0,resultado.codigo);assertTrue(resultado.salida.contains("No se pudo completar"));
        try(var archivos=Files.list(copia.resolve("netlogo/datos"))){assertEquals(0,archivos.count());}
    }
    @Test void cliNoSobrescribeCompaneroIndividualExistente() throws Exception {
        Path salida=temporal.resolve("protegido.csv"),detalle=LectorIndividuos.rutaCompanera(salida);Files.writeString(detalle,"datos previos");
        Ejecucion resultado=ejecutar(proyecto.resolve("target/sir.jar"),temporal,"--sin-netlogo","--csv",salida.toString());
        assertNotEquals(0,resultado.codigo);assertEquals("datos previos",Files.readString(detalle));assertFalse(Files.exists(salida));
    }
}
