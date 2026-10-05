# Vista

`graficas.py` recibe del controlador los resultados ya calculados y dibuja:

1. Humedad, nubosidad y factor de temperatura normalizados por hora.
2. Comparación del índice original y ajustado con los tres umbrales.

`main.py`, situado en la raíz por indicación de la práctica, es la vista de
consola y el punto de entrada. Esta carpeta solo complementa esa vista con las
gráficas de Matplotlib.

La opción 3 siempre guarda `variables_modelo.png` y
`comparacion_modelos.png` en `graficas_generadas`. Así se pueden consultar los
resultados aunque Matplotlib no disponga de un backend para abrir ventanas.
