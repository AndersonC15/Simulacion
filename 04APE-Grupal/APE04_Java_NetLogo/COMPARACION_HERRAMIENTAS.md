# Comparacion de herramientas segun el reparto Java -> NetLogo

| Caracteristica | Java en el proyecto | NetLogo en el proyecto |
|---|---|---|
| Facilidad de implementacion | Clases y responsabilidades explicitas; requiere compilar | Procedimientos y widgets para importar y representar |
| Manejo de agentes | Objetos Individuo y estados S/I/R | No genera agentes: representa conteos importados |
| Generacion de datos | Ejecuta el SIR y produce los CSV | No genera los datos de la simulacion |
| Visualizacion | PNG, ventana Swing y tabla en consola | Cinco graficas, monitores y reproduccion del CSV |
| Flexibilidad | Parametros centralizados, semillas y rutas de salida | Permite seleccionar dos archivos y compararlos |
| Tiempo de ejecucion | System.nanoTime mide modelo y registro sin dibujo/CSV/consola | No hay tiempo de simulacion que comparar: realiza carga y representacion |
| Integracion | Escribe tiempo,S,I,R | Lee exactamente esas cuatro columnas mediante csv |

Ejemplos reales: semilla 42 -> pico I=49 en t=20, final 4/0/96. Semilla 7 -> pico I=35 en t=13, final 9/0/91. Ambas ejecuciones son Java; NetLogo conserva los valores. Repetir una semilla en Java reproduce su serie.

No se afirma que NetLogo sea mas rapido simulando: en este reparto no ejecuta el modelo. Para comparar tiempos deben distinguirse calculo Java, escritura CSV, lectura y dibujo NetLogo.
