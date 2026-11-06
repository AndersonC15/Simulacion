package ec.edu.simulacion.ape06.vista;

import ec.edu.simulacion.ape06.modelo.Analisis;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.Path2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Locale;
import javax.imageio.ImageIO;

/** Vista nativa Java2D; exporta PNG sin servidor grafico ni Python. */
public final class VistaGraficas {
    private static final int ANCHO = 1200, ALTO = 820, IZQUIERDA = 100, ARRIBA = 110, W = 1000, H = 590;
    private static final Color AZUL = new Color(36, 118, 138);
    private static final Color NARANJA = new Color(196, 93, 53);

    public void guardar(Analisis analisis, Path directorio) throws IOException {
        histograma(analisis, directorio.resolve("histograma.png"));
        acumulada(analisis, directorio.resolve("acumulada.png"));
        pares(analisis, directorio.resolve("pares.png"));
    }

    private record Lienzo(BufferedImage imagen, Graphics2D g) implements AutoCloseable {
        @Override public void close() { g.dispose(); }
    }

    private Lienzo lienzo(String titulo, String subtitulo, String etiquetaX, String etiquetaY, double maxY) {
        var imagen = new BufferedImage(ANCHO, ALTO, BufferedImage.TYPE_INT_RGB);
        var g = imagen.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, ANCHO, ALTO);
        g.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 25));
        g.setColor(new Color(30, 45, 55));
        g.drawString(titulo, IZQUIERDA, 44);
        g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 18));
        g.drawString(subtitulo, IZQUIERDA, 78);
        g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 17));
        for (int i = 0; i <= 10; i++) {
            int x = x(i / 10.0), y = y(i / 10.0);
            g.setColor(new Color(228, 233, 236));
            g.drawLine(x, ARRIBA, x, ARRIBA + H);
            g.drawLine(IZQUIERDA, y, IZQUIERDA + W, y);
            g.setColor(Color.DARK_GRAY);
            g.drawString(String.format(Locale.ROOT, "%.1f", i / 10.0), x - 12, ARRIBA + H + 27);
            g.drawString(String.format(Locale.ROOT, maxY == 1 ? "%.1f" : "%.0f", i * maxY / 10), 30, y + 6);
        }
        g.setColor(Color.DARK_GRAY);
        g.drawRect(IZQUIERDA, ARRIBA, W, H);
        g.drawString(etiquetaX, IZQUIERDA + 320, ALTO - 40);
        g.drawString(etiquetaY, 20, 98);
        return new Lienzo(imagen, g);
    }

    private int x(double valor) { return IZQUIERDA + (int) Math.round(valor * W); }
    private int y(double valor) { return ARRIBA + H - (int) Math.round(valor * H); }

    private void histograma(Analisis a, Path ruta) throws IOException {
        var chi = a.pruebas().stream().filter(p -> p.nombre().equals("chi_cuadrado")).findFirst().orElseThrow();
        double maxY = chi.intervalos().stream().mapToDouble(b -> Math.max(b.observada(), b.esperada())).max().orElseThrow() * 1.15;
        try (var l = lienzo(a.muestra().parametros().nombre().toUpperCase(Locale.ROOT) + " - Chi-cuadrado",
                String.format(Locale.ROOT, "T=%.5f, p=%.7g | Azul: observada; naranja: esperada N/10", chi.estadistico(), chi.valorP()),
                "Intervalo de U", "Frecuencia", maxY)) {
            var g = l.g();
            for (var b : chi.intervalos()) {
                g.setColor(AZUL);
                int superior = y(b.observada() / maxY);
                g.fillRect(x(b.inferior() + .008), superior, (int) (.084 * W), y(0) - superior);
            }
            g.setColor(NARANJA);
            g.setStroke(new BasicStroke(3));
            int linea = y(a.muestra().valores().length / 10.0 / maxY);
            g.drawLine(x(0), linea, x(1), linea);
            ImageIO.write(l.imagen(), "png", ruta.toFile());
        }
    }

    private void acumulada(Analisis a, Path ruta) throws IOException {
        double[] ordenados = a.muestra().valores().clone();
        Arrays.sort(ordenados);
        int n = ordenados.length;
        var ks = a.pruebas().stream().filter(p -> p.nombre().equals("ks")).findFirst().orElseThrow();
        try (var l = lienzo(a.muestra().parametros().nombre().toUpperCase(Locale.ROOT) + " - Kolmogorov-Smirnov",
                String.format(Locale.ROOT, "D=%.7f, p aprox.=%.7g | Azul: FDE; naranja: F(u)=u; rojo: D", ks.estadistico(), ks.valorP()),
                "u", "Acumulada", 1)) {
            var camino = new Path2D.Double();
            camino.moveTo(x(0), y(0));
            double mayor = -1, punto = 0, inferior = 0, superior = 0;
            for (int i = 0; i < n; i++) {
                camino.lineTo(x(ordenados[i]), y((double) i / n));
                camino.lineTo(x(ordenados[i]), y((i + 1.0) / n));
                double mas = (i + 1.0) / n - ordenados[i];
                double menos = ordenados[i] - (double) i / n;
                if (mas > mayor) { mayor = mas; punto = ordenados[i]; inferior = punto; superior = (i + 1.0) / n; }
                if (menos > mayor) { mayor = menos; punto = ordenados[i]; inferior = (double) i / n; superior = punto; }
            }
            camino.lineTo(x(1), y(1));
            var g = l.g();
            g.setColor(AZUL);
            g.setStroke(new BasicStroke(2));
            g.draw(camino);
            g.setColor(NARANJA);
            g.setStroke(new BasicStroke(2, BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 10, new float[]{9, 7}, 0));
            g.drawLine(x(0), y(0), x(1), y(1));
            g.setColor(new Color(197, 46, 69));
            g.setStroke(new BasicStroke(4));
            g.drawLine(x(punto), y(inferior), x(punto), y(superior));
            ImageIO.write(l.imagen(), "png", ruta.toFile());
        }
    }

    private void pares(Analisis a, Path ruta) throws IOException {
        double[] valores = a.muestra().valores();
        int limite = Math.min(4000, valores.length - 1);
        try (var l = lienzo(a.muestra().parametros().nombre().toUpperCase(Locale.ROOT) + " - Pares consecutivos",
                limite + " pares | Inspeccion visual: no es una prueba formal de independencia", "U(n)", "U(n+1)", 1)) {
            l.g().setColor(new Color(36, 118, 138, 140));
            for (int i = 0; i < limite; i++) l.g().fillOval(x(valores[i]) - 2, y(valores[i + 1]) - 2, 4, 4);
            ImageIO.write(l.imagen(), "png", ruta.toFile());
        }
    }
}
