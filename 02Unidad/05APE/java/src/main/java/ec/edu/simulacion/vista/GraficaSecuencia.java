package ec.edu.simulacion.vista;

import ec.edu.simulacion.modelo.ResultadoExperimento;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Path;
import javax.imageio.ImageIO;

/** PNG generado por Java2D del JDK; no requiere Python ni sesión gráfica. */
public final class GraficaSecuencia {
    private static final int ANCHO = 1400;
    private static final int ALTO = 1200;
    private static final int IZQUIERDA = 95;
    private static final int GRAFICA_ANCHO = 1220;
    private static final int GRAFICA_ALTO = 240;

    public void guardar(ResultadoExperimento resultado, Path destino) throws IOException {
        var imagen = new BufferedImage(ANCHO, ALTO, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = imagen.createGraphics();
        try {
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g.setColor(Color.WHITE);
            g.fillRect(0, 0, ANCHO, ALTO);
            g.setColor(Color.DARK_GRAY);
            g.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 24));
            g.drawString("LCG — Java — semilla " + resultado.parametros().semilla(), 95, 45);
            dibujarPanel(g, resultado, 110, 0);
            dibujarPanel(g, resultado, 480, 1);
            dibujarPanel(g, resultado, 850, 2);
        } finally {
            g.dispose();
        }
        if (!ImageIO.write(imagen, "png", destino.toFile())) {
            throw new IOException("No se encontró un codificador PNG.");
        }
    }

    private void dibujarPanel(Graphics2D g, ResultadoExperimento r, int arriba, int tipo) {
        int total = r.estados().size();
        int cantidad = tipo == 1 ? Math.min(200, total) : tipo == 2 ? total - 1 : total;
        String titulo = switch (tipo) {
            case 0 -> "Secuencia completa: " + total + " valores";
            case 1 -> "Detalle de las primeras " + cantidad + " observaciones";
            default -> "Pares consecutivos: inspección visual, no prueba estadística";
        };
        g.setColor(Color.DARK_GRAY);
        g.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 19));
        g.drawString(titulo, IZQUIERDA, arriba - 20);
        g.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 15));
        for (int i = 0; i <= 4; i++) {
            int y = arriba + i * GRAFICA_ALTO / 4;
            g.setColor(new Color(225, 230, 235));
            g.drawLine(IZQUIERDA, y, IZQUIERDA + GRAFICA_ANCHO, y);
            g.setColor(Color.DARK_GRAY);
            g.drawString(Double.toString(1 - i / 4.0), 50, y + 5);
            double etiquetaX = tipo == 2 ? i / 4.0 : 1 + Math.max(0, cantidad - 1) * i / 4.0;
            String etiqueta = tipo == 2 ? Double.toString(etiquetaX) : Long.toString(Math.round(etiquetaX));
            g.drawString(etiqueta, IZQUIERDA + i * GRAFICA_ANCHO / 4 - 10,
                    arriba + GRAFICA_ALTO + 25);
        }
        g.drawRect(IZQUIERDA, arriba, GRAFICA_ANCHO, GRAFICA_ALTO);
        g.drawString(tipo == 2 ? "Un" : "n", ANCHO / 2, arriba + GRAFICA_ALTO + 53);
        var transformacion = g.getTransform();
        int centroY = arriba + GRAFICA_ALTO / 2;
        g.rotate(-Math.PI / 2, 20, centroY);
        g.drawString(tipo == 2 ? "Un+1" : "Un", 20, centroY);
        g.setTransform(transformacion);
        g.setColor(new Color(30, 100, 165, tipo == 1 ? 210 : 100));
        g.setStroke(new BasicStroke(1));
        int previoX = 0;
        int previoY = 0;
        for (int i = 0; i < cantidad; i++) {
            double x = tipo == 2 ? r.normalizado(i) : (double) i / Math.max(1, cantidad - 1);
            double y = r.normalizado(tipo == 2 ? i + 1 : i);
            int pixelX = IZQUIERDA + (int) Math.round(x * GRAFICA_ANCHO);
            int pixelY = arriba + (int) Math.round((1 - y) * GRAFICA_ALTO);
            if (tipo == 1 && i > 0) {
                g.drawLine(previoX, previoY, pixelX, pixelY);
            }
            g.fillOval(pixelX - 1, pixelY - 1, 3, 3);
            previoX = pixelX;
            previoY = pixelY;
        }
    }
}

