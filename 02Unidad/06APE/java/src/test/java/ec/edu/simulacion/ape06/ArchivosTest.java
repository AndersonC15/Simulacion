package ec.edu.simulacion.ape06;

import ec.edu.simulacion.ape06.infraestructura.Archivos;
import ec.edu.simulacion.ape06.infraestructura.RepositorioResultados;
import ec.edu.simulacion.ape06.modelo.*;
import ec.edu.simulacion.ape06.vista.VistaGraficas;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import javax.imageio.ImageIO;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

class ArchivosTest {
    @TempDir Path temporal;

    @Test void lectorCsvRespetaComillasYRechazaDuplicados() throws Exception {
        Path archivo = temporal.resolve("config.csv");
        Files.writeString(archivo, "nombre,semilla,a,c,m,fuente\nprueba,1,5,1,16,\"Semana 5, ejemplo\"\n");
        assertEquals("Semana 5, ejemplo", Archivos.leerParametros(archivo, List.of("prueba")).getFirst().fuente());
        assertThrows(IllegalArgumentException.class, () -> Archivos.leerParametros(archivo, List.of("desconocido")));
        Files.writeString(archivo, Files.readString(archivo) + "prueba,1,5,1,16,duplicado\n");
        assertThrows(IllegalArgumentException.class, () -> Archivos.leerParametros(archivo, List.of("prueba")));
    }

    @Test void exportaCsvJsonYGraficasNativasSinPantalla() throws Exception {
        var p = new ParametrosLCG("constante", 1, 1, 0, 16, "Comprobacion");
        var servicio = new ServicioSimulacion(List.of(new Rachas(), new KolmogorovSmirnov(), new ChiCuadrado()));
        var analisis = servicio.analizar(p, 50, .05);
        Path carpeta = new RepositorioResultados(temporal).guardarAnalisis(analisis);
        new VistaGraficas().guardar(analisis, carpeta);
        var json = new ObjectMapper().readTree(carpeta.resolve("analisis.json").toFile());
        assertEquals("No aplicable", json.get("pruebas").get(0).get("decision").asText());
        assertTrue(json.get("pruebas").get(0).get("valor_p").isNull());
        assertEquals(51, Files.readAllLines(carpeta.resolve("secuencia.csv")).size());
        for (String nombre : List.of("histograma.png", "acumulada.png", "pares.png")) {
            var imagen = ImageIO.read(carpeta.resolve(nombre).toFile());
            assertEquals(1200, imagen.getWidth());
            assertEquals(820, imagen.getHeight());
        }
    }

    @Test void interfazRechazaOpcionesInvalidas() {
        assertEquals(2, Main.ejecutar(new String[]{"ejecutar", "--desconocida", "1"}));
        assertEquals(2, Main.ejecutar(new String[]{"ejecutar", "--n"}));
        assertEquals(0, Main.ejecutar(new String[]{"--help"}));
    }
}
