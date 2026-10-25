package sir.pruebas;

import sir.*;
import sir.model.*;
import sir.io.*;
import sir.controller.ControladorSIR;
import sir.view.*;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import java.io.IOException;

/** Casos independientes y comprobaciones de propiedades. Sin JUnit ni datos inventados. */
public final class PruebasQA {
    @FunctionalInterface interface Caso { void ejecutar() throws Exception; }
    static final List<String> resultados=new ArrayList<>();
    static int fallos;
    static Path temporal,raiz;
    static Object motor;
    static final String H=LectorCsv.ENCABEZADO+"\n";
    public static void main(String[] args)throws Exception {
        raiz=Path.of(args[0]).toAbsolutePath(); temporal=Files.createTempDirectory("ape04-qa-");
        parametros(); opciones(); modelo(); archivos();
        if (args.length>1 && args[1].equals("netlogo")) { netlogo(); }
        Path informe=raiz.resolve("pruebas/RESULTADOS_QA.md");
        Files.writeString(informe,"# Pruebas ejecutadas\n\nJava: "+System.getProperty("java.version")+". Casos: "+resultados.size()+". Fallos: "+fallos+".\n\nCada fila es un caso ejecutado; los rechazos esperados cuentan como aprobados. Las semillas adicionales se agrupan en una prueba de propiedades.\n\n| ID | Caso | Resultado |\n|---|---|---|\n"+String.join("\n",resultados)+"\n");
        System.out.println("TOTAL="+resultados.size()+" FALLOS="+fallos+"; informe="+informe);
        if (fallos>0) { System.exit(1); }
    }
    static void caso(String nombre,Caso prueba) {
        String resultado="OK";
        try { prueba.ejecutar(); } catch(Throwable e) { fallos++; resultado="FALLO: "+e.getClass().getSimpleName()+": "+e.getMessage(); System.err.println(nombre+" -> "+resultado); }
        resultados.add("| "+String.format("Q%03d",resultados.size()+1)+" | "+nombre+" | "+resultado.replace('|','/').replace('\n',' ')+" |");
    }
    static void exigir(boolean condicion) { if(!condicion)throw new AssertionError("No se cumple el resultado esperado."); }
    static void rechaza(Caso accion)throws Exception {
        try {accion.ejecutar();}catch(Exception esperado){return;} throw new AssertionError("Se acepto una entrada que debia rechazarse.");
    }
    static ParametrosSIR p(int n,int i,double b,double g,int t,int c){return new ParametrosSIR(n,i,b,g,t,c);}
    static List<ResultadoPaso> serie(ParametrosSIR p,long seed) {
        SimulacionSIR s=new SimulacionSIR(p,seed); List<ResultadoPaso> datos=new ArrayList<>(); datos.add(s.contarPoblacion());
        for(int t=0;t<p.getTiempoSimulacion();t++)datos.add(s.paso());return datos;
    }
    static String csv(List<ResultadoPaso> serie){return H+String.join("\n",serie.stream().map(ResultadoPaso::aCsv).toList())+"\n";}
    static void propiedades(List<ResultadoPaso> s,int n) {
        for(int i=0;i<s.size();i++) { ResultadoPaso f=s.get(i); exigir(f.getTiempo()==i&&f.getTotal()==n); LectorCsv.validarTransicion(s.subList(0,i),f); }
    }
    static void parametros() {
        Object[][] invalidos={
            {"N cero",0,0,.3,.1,100,1},{"N negativo",-1,0,.3,.1,100,1},{"N mayor al limite",10001,5,.3,.1,100,1},
            {"N Integer.MAX_VALUE",Integer.MAX_VALUE,5,.3,.1,100,1},{"I0 negativo",100,-1,.3,.1,100,1},{"I0 mayor a N",100,101,.3,.1,100,1},
            {"beta negativa",100,5,-.00001,.1,100,1},{"beta mayor a uno",100,5,1.00001,.1,100,1},{"beta NaN",100,5,Double.NaN,.1,100,1},
            {"beta infinito",100,5,Double.POSITIVE_INFINITY,.1,100,1},{"beta menos infinito",100,5,Double.NEGATIVE_INFINITY,.1,100,1},
            {"gamma negativa",100,5,.3,-.00001,100,1},{"gamma mayor a uno",100,5,.3,1.00001,100,1},{"gamma NaN",100,5,.3,Double.NaN,100,1},
            {"gamma infinito",100,5,.3,Double.POSITIVE_INFINITY,100,1},{"pasos negativos",100,5,.3,.1,-1,1},{"pasos 2001",100,5,.3,.1,2001,1},
            {"pasos Integer.MAX_VALUE",100,5,.3,.1,Integer.MAX_VALUE,1},{"contactos negativos",100,5,.3,.1,100,-1},
            {"contactos 21",100,5,.3,.1,100,21},{"contactos Integer.MAX_VALUE",100,5,.3,.1,100,Integer.MAX_VALUE},
            {"Carga computacional excesiva",10000,5,.3,.1,2000,20}};
        for(Object[] v:invalidos)caso("Validacion: "+v[0],()->rechaza(()->p((int)v[1],(int)v[2],(double)v[3],(double)v[4],(int)v[5],(int)v[6])));
        caso("Parametros exactos de la guia",()->{ParametrosSIR x=new ParametrosSIR();exigir(x.getPoblacion()==100&&x.getSusceptiblesIniciales()==95&&Math.abs(x.getR0()-3)<1e-12);});
        caso("beta casi igual a gamma: precision sin redondear",()->exigir(p(100,5,.299999,.3,100,1).getR0()<1));
        caso("gamma cero: R0 infinito explicito",()->exigir(Double.isInfinite(p(100,5,.3,0,100,1).getR0())));
        caso("beta y gamma cero: R0 indefinido",()->exigir(Double.isNaN(p(100,5,0,0,100,1).getR0())));
        caso("R0 incluye contactos configurados",()->exigir(Math.abs(p(100,5,.3,.1,100,2).getR0()-6)<1e-12));
        caso("Probabilidades minimas representables",()->propiedades(serie(p(1,1,Double.MIN_VALUE,Double.MIN_VALUE,2,1),0),1));
        caso("N=1 e I0=0",()->exigir(serie(p(1,0,.3,.1,2,1),0).get(2).getSusceptibles()==1));
        caso("N=1 e I0=1",()->exigir(serie(p(1,1,.3,1,2,1),0).get(1).getRecuperados()==1));
    }
    static void opciones() {
        String[][] invalidas={{"--lambda","2.9999"},{"--mu","3"},{"--desconocido"},{"--beta"},{"--semilla"},{"--csv",""},
            {"--semilla","1.5"},{"--semilla","9223372036854775808"},{"--poblacion","2147483648"},{"--poblacion","10.0"},
            {"--beta","NaN"},{"--gamma","Infinity"},{"--beta","0,30"},{"--beta","0x1.0p-1"},{"--beta","1e999"},
            {"--gamma","texto"},{"--pasos"," "},{"--beta",".3","--beta",".4"},{"--sin-netlogo","--sin-netlogo"},
            {"--png","grafica.png"},{"--csv","a\0b.csv"},{"--infectados","-1"},{"--gamma","--pasos"}};
        for(int i=0;i<invalidas.length;i++){String[] entrada=invalidas[i];caso("CLI rechaza "+Arrays.toString(entrada).replace('\0','?'),()->rechaza(()->Opciones.leer(entrada,raiz)));}
        caso("CLI conserva Long.MIN_VALUE",()->exigir(Opciones.leer(new String[]{"--semilla",Long.toString(Long.MIN_VALUE)},raiz).semilla()==Long.MIN_VALUE));
        caso("CLI conserva Long.MAX_VALUE",()->exigir(Opciones.leer(new String[]{"--semilla",Long.toString(Long.MAX_VALUE)},raiz).semilla()==Long.MAX_VALUE));
        caso("CLI notacion cientifica valida",()->exigir(Opciones.leer(new String[]{"--beta","3e-1"},raiz).parametros().getBeta()==.3));
        caso("CLI alias anterior sin grafica",()->exigir(Opciones.leer(new String[]{"--sin-grafica"},raiz).sinNetlogo()));
        caso("Rutas automaticas distintas entre ejecuciones",()->exigir(!Opciones.leer(new String[0],raiz).csv().equals(Opciones.leer(new String[0],raiz).csv())));
        caso("Busqueda NetLogo explicita invalida controlada",()->rechaza(()->LanzadorNetLogo.localizar(temporal)));
    }
    static void modelo() {
        caso("Regresion semilla 42: final 4/0/96 y pico 49 en t20",()->{var s=serie(new ParametrosSIR(),42);exigir(s.get(100).aCsv().equals("100,4,0,96"));exigir(s.get(20).getInfectados()==49&&s.stream().mapToInt(ResultadoPaso::getInfectados).max().orElse(0)==49);});
        caso("Regresion semilla 7: final 9/0/91",()->exigir(serie(new ParametrosSIR(),7).get(100).aCsv().equals("100,9,0,91")));
        caso("Misma semilla repite todas las filas",()->exigir(csv(serie(new ParametrosSIR(),42)).equals(csv(serie(new ParametrosSIR(),42)))));
        caso("Semillas diferentes producen trayectorias diferentes",()->exigir(!csv(serie(new ParametrosSIR(),42)).equals(csv(serie(new ParametrosSIR(),7)))));
        caso("1000 semillas: conservacion y transiciones en cada paso",()->{for(long seed=0;seed<1000;seed++)propiedades(serie(new ParametrosSIR(),seed),100);});
        caso("500 escenarios aleatorios validos: no poblacion negativa",()->{Random r=new Random(2026);for(int k=0;k<500;k++){int n=1+r.nextInt(200);propiedades(serie(p(n,r.nextInt(n+1),r.nextDouble(),r.nextDouble(),r.nextInt(100),r.nextInt(5)),k),n);}});
        caso("Cero infectados: no aparecen contagios",()->exigir(serie(p(100,0,1,0,100,1),42).get(100).aCsv().equals("100,100,0,0")));
        caso("Todos infectados y gamma=1: todos recuperan",()->exigir(serie(p(100,100,.3,1,2,1),42).get(1).aCsv().equals("1,0,0,100")));
        caso("beta=gamma=0: poblacion estatica",()->exigir(serie(p(100,5,0,0,100,1),42).get(100).aCsv().equals("100,95,5,0")));
        caso("beta=0 y gamma=1: se recuperan cinco",()->exigir(serie(p(100,5,0,1,2,1),42).get(1).aCsv().equals("1,95,0,5")));
        caso("gamma=0: nadie recupera en 100 pasos",()->exigir(serie(p(100,5,1,0,100,1),42).stream().allMatch(f->f.getRecuperados()==0)));
        caso("Contactos=0: no contagios nuevos",()->exigir(serie(p(100,5,1,1,2,0),42).get(2).getSusceptibles()==95));
        caso("Foto del paso: recien contagiado no recupera inmediatamente",()->{boolean encontrado=false;for(long k=0;k<100;k++){var f=serie(p(2,1,1,1,1,1),k).get(1);if(f.getSusceptibles()==0){exigir(f.getInfectados()==1&&f.getRecuperados()==1);encontrado=true;break;}}exigir(encontrado);});
        caso("Horizonte cero: solo estado inicial y paso rechazado",()->{SimulacionSIR s=new SimulacionSIR(p(10,1,.3,.1,0,1),0);exigir(s.contarPoblacion().getTiempo()==0);rechaza(s::paso);});
        caso("No se permite avanzar despues del horizonte",()->{SimulacionSIR s=new SimulacionSIR(p(10,1,.3,.1,1,1),0);s.paso();rechaza(s::paso);exigir(s.getTiempoActual()==1);});
        caso("Modelo rechaza parametros null",()->rechaza(()->new SimulacionSIR(null,1)));
        caso("Getter no permite quitar individuos",()->rechaza(()->new SimulacionSIR(new ParametrosSIR(),1).getPoblacion().clear()));
        caso("Cambiar copia de individuo no altera modelo",()->{SimulacionSIR s=new SimulacionSIR(new ParametrosSIR(),1);String antes=s.contarPoblacion().aCsv();s.getPoblacion().get(0).setEstado(Estado.RECUPERADO);exigir(antes.equals(s.contarPoblacion().aCsv()));});
        caso("Individuo rechaza estado null",()->rechaza(()->new Individuo(0,null)));
        caso("Setter rechaza null",()->rechaza(()->new Individuo(0,Estado.INFECTADO).setEstado(null)));
        caso("Individuo rechaza ID negativo",()->rechaza(()->new Individuo(-1,Estado.INFECTADO)));
        int[][] malos={{-1,95,5,0},{0,-1,5,96},{0,95,-1,6},{0,95,6,-1},{0,Integer.MAX_VALUE,Integer.MAX_VALUE,0},{0,0,0,0}};
        for(int[] f:malos)caso("ResultadoPaso rechaza "+Arrays.toString(f),()->rechaza(()->new ResultadoPaso(f[0],f[1],f[2],f[3])));
        caso("N maximo con horizonte corto",()->propiedades(serie(p(10000,10000,1,1,1,1),42),10000));
        caso("2000 pasos con N pequeno",()->propiedades(serie(p(2,1,.3,.1,2000,1),42),2));
        caso("Imagen rechaza tamano negativo",()->rechaza(()->new GraficaSIR(List.of(),-1,600)));
        caso("Imagen rechaza tamano gigantesco",()->rechaza(()->new GraficaSIR(List.of(),100000,100000)));
        caso("Imagen sin datos no se cae",()->exigir(new GraficaSIR(List.of()).crearImagen().getWidth()==960));
    }
    static final Map<String,String> CSV_MALOS=new LinkedHashMap<>();
    static void prepararCsvMalos(){
        CSV_MALOS.put("Archivo vacio","");CSV_MALOS.put("Solo encabezado",H);CSV_MALOS.put("Sin encabezado","0,95,5,0\n");
        CSV_MALOS.put("Separador punto y coma",H.replace(',', ';')+"0;95;5;0\n");CSV_MALOS.put("Encabezado desordenado","tiempo,infectados,susceptibles,recuperados\n0,95,5,0\n");
        CSV_MALOS.put("Columna extra",H+"0,95,5,0,0\n");CSV_MALOS.put("Columna faltante",H+"0,95,5\n");
        CSV_MALOS.put("Texto en conteo",H+"0,hola,5,0\n");CSV_MALOS.put("Conteo negativo",H+"0,95,-5,10\n");
        CSV_MALOS.put("Conteo fraccionario",H+"0,94.5,5.5,0\n");CSV_MALOS.put("NaN en conteo",H+"0,NaN,5,0\n");CSV_MALOS.put("Infinity en conteo",H+"0,Infinity,5,0\n");
        CSV_MALOS.put("Tiempo inicial uno",H+"1,95,5,0\n");CSV_MALOS.put("Tiempo con salto",H+"0,95,5,0\n2,95,5,0\n");CSV_MALOS.put("Tiempo repetido",H+"0,95,5,0\n0,95,5,0\n");
        CSV_MALOS.put("Tiempo retrocede",H+"0,95,5,0\n1,95,5,0\n0,95,5,0\n");CSV_MALOS.put("N cero",H+"0,0,0,0\n");CSV_MALOS.put("N mayor al limite",H+"0,10000,1,0\n");
        CSV_MALOS.put("Poblacion cambia",H+"0,95,5,0\n1,94,5,0\n");CSV_MALOS.put("Susceptibles aumentan",H+"0,95,5,0\n1,96,4,0\n");
        CSV_MALOS.put("Recuperados disminuyen",H+"0,95,5,0\n1,95,4,1\n2,95,5,0\n");CSV_MALOS.put("Recuperaciones imposibles",H+"0,95,5,0\n1,0,0,100\n");
        CSV_MALOS.put("Contagios sin infectados",H+"0,100,0,0\n1,99,1,0\n");CSV_MALOS.put("R inicial distinto de cero",H+"0,94,5,1\n");
        CSV_MALOS.put("Fila en blanco intermedia",H+"0,95,5,0\n\n1,95,5,0\n");CSV_MALOS.put("Celda vacia",H+"0,,5,0\n");
        CSV_MALOS.put("Formula de hoja de calculo",H+"0,=95,5,0\n");CSV_MALOS.put("Texto con instrucciones",H+"0,clear-all,5,0\n");
        CSV_MALOS.put("Entero desbordado",H+"0,999999999999999999999,5,0\n");CSV_MALOS.put("Linea enorme",H+"9".repeat(300)+"\n");
        StringBuilder largo=new StringBuilder(H);for(int t=0;t<=2001;t++)largo.append(t+",100,0,0\n");CSV_MALOS.put("2002 registros",largo.toString());
    }
    static Path escribir(String nombre,String texto)throws Exception{Path f=temporal.resolve(nombre+".csv");Files.writeString(f,texto);return f;}
    static void archivos() throws Exception {
        prepararCsvMalos();
        for(var v:CSV_MALOS.entrySet())caso("CSV Java rechaza: "+v.getKey(),()->rechaza(()->new LectorCsv().leer(escribir(v.getKey(),v.getValue()))));
        caso("CSV Java: cabecera BOM aceptada",()->exigir(new LectorCsv().leer(escribir("bom","\uFEFF"+H+"0,95,5,0\n")).size()==1));
        caso("CSV Java: saltos CRLF aceptados",()->exigir(new LectorCsv().leer(escribir("crlf",(H+"0,95,5,0\n1,95,5,0\n").replace("\n","\r\n"))).size()==2));
        caso("CSV Java: espacios alrededor de enteros",()->exigir(new LectorCsv().leer(escribir("espacios",H+" 0, 95, 5, 0\n")).size()==1));
        caso("CSV Java: archivo inexistente",()->rechaza(()->new LectorCsv().leer(temporal.resolve("ausente.csv"))));
        caso("CSV Java: directorio en vez de archivo",()->rechaza(()->new LectorCsv().leer(temporal)));
        caso("CSV Java: archivo mayor a 1 MiB rechazado",()->rechaza(()->new LectorCsv().leer(escribir("gigante","x".repeat(1048577)))));
        caso("CSV Java: ruta con Unicode, espacios y comillas",()->exigir(new LectorCsv().leer(escribir("niño \"ruta\"",H+"0,95,5,0\n")).size()==1));
        caso("Exportacion: CSV PNG parametros por cada ejecucion",()->{
            Path f=temporal.resolve("salidas/datos.csv");new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f);
            exigir(Files.exists(f)&&javax.imageio.ImageIO.read(f.resolveSibling("datos.png").toFile())!=null&&Files.readString(f.resolveSibling("datos.properties")).contains("semilla=42"));
            exigir(new LectorCsv().leer(f).get(100).aCsv().equals("100,4,0,96"));
        });
        caso("No sobrescribe CSV existente",()->{
            Path f=escribir("conservar","contenido original");rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f));exigir(Files.readString(f).equals("contenido original"));
        });
        caso("No sobrescribe PNG existente aunque no haya CSV",()->{
            Path f=temporal.resolve("conservar_png.csv"),png=temporal.resolve("conservar_png.png");Files.writeString(png,"original");
            rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f));exigir(!Files.exists(f)&&Files.readString(png).equals("original"));
        });
        caso("No sobrescribe parametros existentes",()->{
            Path f=temporal.resolve("conservar_props.csv"),props=temporal.resolve("conservar_props.properties");Files.writeString(props,"original");
            rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f));exigir(!Files.exists(f));
        });
        caso("Extension de salida incorrecta rechazada",()->rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,temporal.resolve("dato.png"))));
        caso("Nombre sin base rechazado",()->rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,temporal.resolve(".csv"))));
        caso("Padre es un archivo: error controlado",()->{Path f=escribir("padre","original");rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f.resolve("dato.csv")));});
        caso("Fallo del exportador no deja CSV ni PNG parciales",()->{
            Path f=temporal.resolve("fallido.csv");ExportadorResultados malo=(s,r)->{Files.writeString(r,"parcial");throw new IOException("fallo simulado");};
            rechaza(()->new ControladorSIR(malo).ejecutar(new ParametrosSIR(),42,f));exigir(!Files.exists(f)&&!Files.exists(temporal.resolve("fallido.png")));
        });
        caso("Mismo controlador dos veces no duplica historial",()->{
            var c=new ControladorSIR(new ExportadorCsv());c.ejecutar(p(10,1,.3,.1,2,1),42,temporal.resolve("uno.csv"));c.ejecutar(p(10,1,.3,.1,2,1),42,temporal.resolve("dos.csv"));
            exigir(new LectorCsv().leer(temporal.resolve("uno.csv")).size()==3&&new LectorCsv().leer(temporal.resolve("dos.csv")).size()==3);
        });
        caso("CSV exportador rechaza lista vacia",()->rechaza(()->new ExportadorCsv().exportar(List.of(),temporal.resolve("vacio.csv"))));
        caso("CSV exportador rechaza transicion imposible",()->rechaza(()->new ExportadorCsv().exportar(List.of(new ResultadoPaso(0,95,5,0),new ResultadoPaso(1,0,0,100)),temporal.resolve("imposible.csv"))));
        caso("Texto para NetLogo escapa comillas y barras",()->exigir(PuenteNetLogo.texto("a\"b\\c").equals("\"a\\\"b\\\\c\"")));
        caso("UTF-8 corrupto se rechaza sin bloquear el lector",()->{
            Path f=temporal.resolve("utf8.csv");Files.write(f,new byte[]{(byte)0xc3,(byte)0x28});rechaza(()->new LectorCsv().leer(f));
            exigir(new LectorCsv().leer(temporal.resolve("uno.csv")).size()==3);
        });
        caso("Dos ejecuciones simultaneas con igual destino: una sola gana",()->{
            Path f=temporal.resolve("concurrente.csv");var inicio=new java.util.concurrent.CountDownLatch(1);
            var pool=java.util.concurrent.Executors.newFixedThreadPool(2);List<java.util.concurrent.Future<Boolean>> futuros=new ArrayList<>();
            try{
                for(int i=0;i<2;i++){final long semilla=i;futuros.add(pool.submit(()->{inicio.await();try{new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),semilla,f);return true;}catch(IOException e){return false;}}));}
                inicio.countDown();int ganadores=0;for(var futuro:futuros)if(futuro.get(10,java.util.concurrent.TimeUnit.SECONDS))ganadores++;
                exigir(ganadores==1&&new LectorCsv().leer(f).size()==101&&Files.exists(temporal.resolve("concurrente.png"))&&!Files.exists(temporal.resolve("concurrente.csv.lock")));
            }finally{pool.shutdownNow();}
        });
        caso("Reserva de otra ejecucion no se borra ni sobrescribe",()->{
            Path f=temporal.resolve("reservado.csv"),lock=temporal.resolve("reservado.csv.lock");Files.writeString(lock,"otra ejecucion");
            rechaza(()->new ControladorSIR(new ExportadorCsv()).ejecutar(new ParametrosSIR(),42,f));exigir(Files.readString(lock).equals("otra ejecucion")&&!Files.exists(f));
        });
        caso("Archivo final sin salto de linea se importa",()->exigir(new LectorCsv().leer(escribir("sin_salto",H+"0,95,5,0")).size()==1));
    }
    static Object llamar(String metodo,String texto)throws Exception {
        try{return motor.getClass().getMethod(metodo,String.class).invoke(motor,texto);}
        catch(InvocationTargetException e){if(e.getCause() instanceof Exception)throw (Exception)e.getCause();throw e;}
    }
    static void cmd(String codigo)throws Exception{llamar("command",codigo);}
    static Object rep(String codigo)throws Exception{return llamar("report",codigo);}
    static void netlogo()throws Exception {
        motor=Class.forName("org.nlogo.headless.HeadlessWorkspace").getMethod("newInstance").invoke(null);
        try {
            motor.getClass().getMethod("open",String.class).invoke(motor,raiz.resolve("netlogo/modelo_sir_netlogo.nlogox").toString());cmd("startup");
            caso("NetLogo carga base en t=0",()->exigir(rep("indice").equals(0.0)));
            caso("NetLogo importa exactamente todas las filas Java",()->exigir(rep("datos-java = but-first csv:from-file \"datos/resultados_java.csv\"").equals(true)));
            caso("NetLogo avanzar dibuja el paso siguiente",()->{cmd("reiniciar avanzar");exigir(rep("indice").equals(1.0));});
            caso("NetLogo ver completo llega a 100",()->{cmd("mostrar-completo");exigir(rep("indice").equals(100.0));});
            caso("NetLogo 500 avances al final no exceden horizonte",()->{cmd("repeat 500 [avanzar]");exigir(rep("indice").equals(100.0));});
            caso("NetLogo reiniciar despues del final",()->{cmd("reiniciar");exigir(rep("indice").equals(0.0));});
            caso("NetLogo animar avanza desde inicio",()->{cmd("animar");exigir(rep("indice").equals(1.0));});
            caso("NetLogo ver completo repetido es estable",()->{cmd("repeat 20 [mostrar-completo]");exigir(rep("valor-java 1 = 4 and valor-java 2 = 0 and valor-java 3 = 96").equals(true));});
            for(var v:CSV_MALOS.entrySet())caso("NetLogo rechaza y conserva datos: "+v.getKey(),()->{
                Object antes=rep("datos-java");Path f=escribir("nl_"+v.getKey(),v.getValue());rechaza(()->cmd("cargar-java-desde "+PuenteNetLogo.texto(f.toString())));exigir(rep("datos-java").equals(antes));
            });
            caso("NetLogo acepta BOM",()->{cmd("cargar-java-desde "+PuenteNetLogo.texto(escribir("nl_bom","\uFEFF"+H+"0,95,5,0\n").toString()));exigir(rep("length datos-java").equals(1.0));});
            caso("NetLogo acepta CRLF",()->{cmd("cargar-java-desde "+PuenteNetLogo.texto(escribir("nl_crlf",(H+"0,95,5,0\n1,95,5,0\n").replace("\n","\r\n")).toString()));exigir(rep("length datos-java").equals(2.0));});
            caso("NetLogo CSV faltante conserva escenario",()->{Object antes=rep("datos-java");rechaza(()->cmd("cargar-java-desde \"ausente.csv\""));exigir(rep("datos-java").equals(antes));});
            caso("NetLogo carga N y horizonte diferentes a la guia",()->{cmd("cargar-java-desde "+PuenteNetLogo.texto(temporal.resolve("uno.csv").toString()));exigir(rep("length datos-java = 3 and valor-java 1 + valor-java 2 + valor-java 3 = 10").equals(true));});
            caso("NetLogo referencia con horizonte distinto no sale del arreglo",()->{cmd("cargar-referencia-desde \"datos/resultados_java.csv\" mostrar-completo");exigir(rep("indice = 100 and valor-java 0 = 2 and valor-referencia 0 = 100").equals(true));});
            caso("NetLogo quitar referencia limpia comparaciones",()->{cmd("quitar-referencia");exigir(rep("empty? datos-referencia and indice = 2").equals(true));});
            caso("NetLogo sin datos: controles no lanzan excepcion",()->{cmd("set datos-java [] quitar-referencia reiniciar avanzar animar mostrar-completo");exigir(rep("indice").equals(0.0));});
            caso("NetLogo archivo solo t0 no provoca indice negativo",()->{cmd("cargar-java-desde "+PuenteNetLogo.texto(escribir("nl_t0",H+"0,95,5,0\n").toString())+" reiniciar avanzar mostrar-completo");exigir(rep("indice").equals(0.0));});
            caso("NetLogo rutas Unicode con comillas se tratan como datos",()->{cmd("cargar-java-desde "+PuenteNetLogo.texto(temporal.resolve("niño \"ruta\".csv").toString()));exigir(rep("length datos-java").equals(1.0));});
            caso("NetLogo exportacion de graficas contiene todos los puntos",()->{
                cmd("cargar-java-desde \"datos/resultados_java.csv\" quitar-referencia mostrar-completo");Path f=temporal.resolve("graficas.csv");cmd("export-all-plots "+PuenteNetLogo.texto(f.toString()));
                String datos=Files.readString(f).replace("\"","");exigir(datos.contains("Escenario A")&&datos.contains("Susceptibles: A / B"));
                List<ResultadoPaso> base=new LectorCsv().leer(raiz.resolve("netlogo/datos/resultados_java.csv"));
                String[] lineas=datos.split("\\R");int cabecera=-1;
                for(int k=0;k<lineas.length;k++){if(lineas[k].equals("x,y,color,pen down?,x,y,color,pen down?,x,y,color,pen down?")){cabecera=k;break;}}
                exigir(cabecera>=0);
                for(int t=0;t<101;t++){String[] v=lineas[cabecera+1+t].split(",");ResultadoPaso paso=base.get(t);exigir(Integer.parseInt(v[0])==t&&Integer.parseInt(v[1])==paso.getSusceptibles()&&Integer.parseInt(v[5])==paso.getInfectados()&&Integer.parseInt(v[9])==paso.getRecuperados());}
            });
            caso("NetLogo 100 ciclos reiniciar/completo sin acumulacion",()->{cmd("repeat 100 [reiniciar mostrar-completo]");exigir(rep("indice = 100 and length datos-java = 101").equals(true));});
        } finally {motor.getClass().getMethod("dispose").invoke(motor);}
    }
}
