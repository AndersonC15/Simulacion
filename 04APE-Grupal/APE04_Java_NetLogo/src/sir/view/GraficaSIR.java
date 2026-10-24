package sir.view;

import sir.model.ResultadoPaso;

import javax.imageio.ImageIO;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GraphicsEnvironment;
import java.awt.RenderingHints;
import java.awt.geom.Path2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.List;

public class GraficaSIR {

    private static final Color COLOR_FONDO = Color.WHITE;
    private static final Color COLOR_REJILLA = new Color(225, 225, 225);
    private static final Color COLOR_EJES = new Color(50, 50, 50);
    private static final Color COLOR_TEXTO = new Color(40, 40, 40);
    private static final Color COLOR_SUSCEPTIBLES = new Color(30, 100, 210);
    private static final Color COLOR_INFECTADOS = new Color(200, 40, 40);
    private static final Color COLOR_RECUPERADOS = new Color(30, 150, 70);

    private static final int MARGEN_IZQUIERDO = 75;
    private static final int MARGEN_DERECHO = 35;
    private static final int MARGEN_SUPERIOR = 85;
    private static final int MARGEN_INFERIOR = 65;

    private static final int SERIE_SUSCEPTIBLES = 0;
    private static final int SERIE_INFECTADOS = 1;
    private static final int SERIE_RECUPERADOS = 2;

    private final List<ResultadoPaso> historial;
    private final int ancho;
    private final int alto;

    public GraficaSIR(List<ResultadoPaso> historial) {
        this(historial, 960, 600);
    }

    public GraficaSIR(List<ResultadoPaso> historial, int ancho, int alto) {
        this.historial = historial;
        this.ancho = ancho;
        this.alto = alto;
    }

    public BufferedImage crearImagen() {
        BufferedImage imagen = new BufferedImage(ancho, alto, BufferedImage.TYPE_INT_RGB);
        Graphics2D graphics = imagen.createGraphics();
        try {
            dibujar(graphics);
        } finally {
            graphics.dispose();
        }
        return imagen;
    }

    public File guardarImagen(String ruta) throws IOException {
        File archivo = new File(ruta);
        ImageIO.write(crearImagen(), "png", archivo);
        return archivo;
    }

    public void mostrarVentana(String titulo) {
        if (GraphicsEnvironment.isHeadless()) {
            return;
        }
        final BufferedImage imagen = crearImagen();
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                JFrame marco = new JFrame(titulo);
                marco.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
                JPanel panel = new JPanel() {
                    @Override
                    protected void paintComponent(Graphics g) {
                        super.paintComponent(g);
                        g.drawImage(imagen, 0, 0, null);
                    }

                    @Override
                    public Dimension getPreferredSize() {
                        return new Dimension(imagen.getWidth(), imagen.getHeight());
                    }
                };
                marco.add(panel);
                marco.pack();
                marco.setLocationRelativeTo(null);
                marco.setVisible(true);
            }
        });
    }

    private void dibujar(Graphics2D g) {
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(COLOR_FONDO);
        g.fillRect(0, 0, ancho, alto);

        if (historial.isEmpty()) {
            return;
        }

        int tiempoMaximo = historial.get(historial.size() - 1).getTiempo();
        if (tiempoMaximo <= 0) {
            tiempoMaximo = 1;
        }

        int valorMaximo = 1;
        for (ResultadoPaso resultado : historial) {
            valorMaximo = Math.max(valorMaximo, Math.max(resultado.getSusceptibles(),
                    Math.max(resultado.getInfectados(), resultado.getRecuperados())));
        }
        valorMaximo = redondearArriba(valorMaximo);

        int x0 = MARGEN_IZQUIERDO;
        int y0 = MARGEN_SUPERIOR;
        int anchoArea = ancho - MARGEN_IZQUIERDO - MARGEN_DERECHO;
        int altoArea = alto - MARGEN_SUPERIOR - MARGEN_INFERIOR;

        dibujarTitulo(g);
        dibujarRejilla(g, x0, y0, anchoArea, altoArea, tiempoMaximo, valorMaximo);
        dibujarCurva(g, x0, y0, anchoArea, altoArea, tiempoMaximo, valorMaximo, COLOR_SUSCEPTIBLES, SERIE_SUSCEPTIBLES);
        dibujarCurva(g, x0, y0, anchoArea, altoArea, tiempoMaximo, valorMaximo, COLOR_INFECTADOS, SERIE_INFECTADOS);
        dibujarCurva(g, x0, y0, anchoArea, altoArea, tiempoMaximo, valorMaximo, COLOR_RECUPERADOS, SERIE_RECUPERADOS);
        dibujarLeyenda(g);
        dibujarRotulos(g, x0, y0, anchoArea, altoArea);
    }

    private void dibujarTitulo(Graphics2D g) {
        g.setColor(COLOR_TEXTO);
        g.setFont(new Font("SansSerif", Font.BOLD, 20));
        String titulo = "Modelo SIR - Evolucion de la poblacion (Java)";
        int anchoTitulo = g.getFontMetrics().stringWidth(titulo);
        g.drawString(titulo, (ancho - anchoTitulo) / 2, 35);
    }

    private void dibujarRejilla(Graphics2D g, int x0, int y0, int anchoArea, int altoArea,
                                int tiempoMaximo, int valorMaximo) {
        g.setFont(new Font("SansSerif", Font.PLAIN, 13));

        for (int paso = 0; paso <= 4; paso++) {
            int valor = valorMaximo * paso / 4;
            int y = y0 + altoArea - (int) (altoArea * (paso / 4.0));

            g.setColor(COLOR_REJILLA);
            g.drawLine(x0, y, x0 + anchoArea, y);

            g.setColor(COLOR_EJES);
            String etiqueta = String.valueOf(valor);
            int anchoEtiqueta = g.getFontMetrics().stringWidth(etiqueta);
            g.drawString(etiqueta, x0 - 12 - anchoEtiqueta, y + 5);
        }

        int intervalo = Math.max(1, tiempoMaximo / 10);
        for (int t = 0; t <= tiempoMaximo; t += intervalo) {
            int x = x0 + (int) (anchoArea * (t / (double) tiempoMaximo));

            g.setColor(COLOR_REJILLA);
            g.drawLine(x, y0, x, y0 + altoArea);

            g.setColor(COLOR_EJES);
            String etiqueta = String.valueOf(t);
            int anchoEtiqueta = g.getFontMetrics().stringWidth(etiqueta);
            g.drawString(etiqueta, x - anchoEtiqueta / 2, y0 + altoArea + 22);
        }

        g.setColor(COLOR_EJES);
        g.setStroke(new BasicStroke(2f));
        g.drawLine(x0, y0, x0, y0 + altoArea);
        g.drawLine(x0, y0 + altoArea, x0 + anchoArea, y0 + altoArea);
        g.setStroke(new BasicStroke(1f));
    }

    private void dibujarCurva(Graphics2D g, int x0, int y0, int anchoArea, int altoArea,
                              int tiempoMaximo, int valorMaximo, Color color, int serie) {
        Path2D.Double ruta = new Path2D.Double();
        boolean primero = true;
        for (ResultadoPaso resultado : historial) {
            double x = x0 + anchoArea * (resultado.getTiempo() / (double) tiempoMaximo);
            double y = y0 + altoArea - altoArea * (valorDe(resultado, serie) / (double) valorMaximo);
            if (primero) {
                ruta.moveTo(x, y);
                primero = false;
            } else {
                ruta.lineTo(x, y);
            }
        }
        g.setColor(color);
        g.setStroke(new BasicStroke(2.6f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.draw(ruta);
        g.setStroke(new BasicStroke(1f));
    }

    private void dibujarLeyenda(Graphics2D g) {
        String[] textos = {
                "Susceptibles (S)",
                "Infectados (I)",
                "Recuperados (R)"
        };
        Color[] colores = {COLOR_SUSCEPTIBLES, COLOR_INFECTADOS, COLOR_RECUPERADOS};

        g.setFont(new Font("SansSerif", Font.BOLD, 14));
        int posicionX = MARGEN_IZQUIERDO;
        int posicionY = 65;

        for (int i = 0; i < textos.length; i++) {
            g.setColor(colores[i]);
            g.fillRect(posicionX, posicionY - 11, 26, 12);
            g.setColor(COLOR_TEXTO);
            g.drawString(textos[i], posicionX + 33, posicionY);
            posicionX += 33 + g.getFontMetrics().stringWidth(textos[i]) + 35;
        }
    }

    private void dibujarRotulos(Graphics2D g, int x0, int y0, int anchoArea, int altoArea) {
        g.setColor(COLOR_TEXTO);
        g.setFont(new Font("SansSerif", Font.PLAIN, 15));

        String ejeX = "Tiempo (pasos)";
        int anchoEjeX = g.getFontMetrics().stringWidth(ejeX);
        g.drawString(ejeX, x0 + (anchoArea - anchoEjeX) / 2, y0 + altoArea + 50);

        Graphics2D copia = (Graphics2D) g.create();
        copia.rotate(-Math.PI / 2, 22, y0 + altoArea / 2.0);
        String ejeY = "Numero de individuos";
        int anchoEjeY = copia.getFontMetrics().stringWidth(ejeY);
        copia.drawString(ejeY, 22 - anchoEjeY / 2, y0 + altoArea / 2);
        copia.dispose();
    }

    private int valorDe(ResultadoPaso resultado, int serie) {
        if (serie == SERIE_SUSCEPTIBLES) {
            return resultado.getSusceptibles();
        }
        if (serie == SERIE_INFECTADOS) {
            return resultado.getInfectados();
        }
        return resultado.getRecuperados();
    }

    private int redondearArriba(int valor) {
        int paso = 20;
        return ((valor + paso - 1) / paso) * paso;
    }
}
