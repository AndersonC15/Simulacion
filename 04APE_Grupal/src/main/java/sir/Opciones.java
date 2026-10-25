package sir;

import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import sir.model.ParametrosSIR;

/** Traduce entradas de terminal; las reglas numericas pertenecen al modelo. */
public record Opciones(ParametrosSIR parametros, long semilla, Path csv, Path netlogo, boolean sinNetlogo) {
    public static Opciones leer(String[] args, Path raiz) {
        int n=100, i0=5, pasos=100, contactos=1;
        double beta=.30, gamma=.10;
        long semilla=42;
        Path csv=null, netlogo=null;
        boolean sin=false;
        Set<String> vistas=new HashSet<>();
        for (int i=0; i<args.length; i++) {
            String opcion=args[i];
            if (!vistas.add(opcion)) { throw new IllegalArgumentException("Opcion repetida: " + opcion); }
            if (opcion.equals("--sin-netlogo") || opcion.equals("--sin-grafica")) { sin=true; continue; }
            if (!Set.of("--poblacion","--infectados","--pasos","--contactos","--beta","--gamma","--semilla","--csv","--netlogo").contains(opcion)) {
                throw new IllegalArgumentException("Opcion desconocida: " + opcion);
            }
            if (++i >= args.length || args[i].isBlank()) { throw new IllegalArgumentException("Falta el valor de " + opcion); }
            String valor=args[i];
            try {
                switch (opcion) {
                    case "--poblacion" -> n=Integer.parseInt(valor);
                    case "--infectados" -> i0=Integer.parseInt(valor);
                    case "--pasos" -> pasos=Integer.parseInt(valor);
                    case "--contactos" -> contactos=Integer.parseInt(valor);
                    case "--beta" -> beta=decimal(valor);
                    case "--gamma" -> gamma=decimal(valor);
                    case "--semilla" -> semilla=Long.parseLong(valor);
                    case "--csv" -> csv=Path.of(valor);
                    case "--netlogo" -> netlogo=Path.of(valor);
                    default -> throw new IllegalArgumentException(opcion);
                }
            } catch (NumberFormatException e) { throw new IllegalArgumentException("Valor invalido en " + opcion + ": usa numeros y punto decimal."); }
        }
        return new Opciones(new ParametrosSIR(n,i0,beta,gamma,pasos,contactos),semilla,
                csv==null ? sir.controller.ControladorSIR.nuevaRuta(raiz) : csv.toAbsolutePath(),netlogo,sin);
    }
    private static double decimal(String valor) {
        if (!valor.matches("[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?")) {
            throw new NumberFormatException();
        }
        return Double.parseDouble(valor);
    }
}
