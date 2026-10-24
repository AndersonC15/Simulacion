# Vista

`VistaConsola` recibe texto y presenta mensajes, tablas y resultados. Delega
la validación al modelo; no calcula índices ni decide sus categorías. El
formato conserva el valor decimal y ajusta el ancho de las columnas.

`VistaGraficas` dibuja resultados ya calculados y devuelve una `EntregaGraficas`
con rutas y situación de visualización. Convierte a float solo al dibujar.
Guarda `variables_modelo.png` y `comparacion_modelos.png` dentro de
`01APE/graficas_generadas`, con independencia del directorio de ejecución.

La detección usa el framework del registro de backends de Matplotlib: Agg
no abre ventanas; TkAgg y QtAgg sí cuando sus toolkits y el escritorio están
disponibles. Se intenta Agg si falla el inicio del backend. Los PNG pueden
consultarse sin ventanas. Los errores de archivos llegan al controlador y
las figuras propias se cierran en finally. Las pruebas simuladas de show
no equivalen a comprobar ventanas reales.
