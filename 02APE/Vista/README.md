# Adaptadores de visualización

La vista de consola está en `../main.py`. Esta carpeta adapta un `Experimento`
ya calculado a Matplotlib y CSV; no recalcula las ecuaciones ni genera otra
realización estocástica.

`graficas.py` contiene `VistaGraficas.guardar`: convierte a float únicamente
para dibujar, distingue observaciones, escalones discretos, ruido y Euler,
genera PNG y exporta CSV con los valores Decimal como texto. Usa un directorio
de resultados explícito o `../resultados`, reemplaza archivos mediante
temporales y cierra las figuras incluso ante errores.

La gráfica rechaza tiempos distintos que se fusionan al convertir a float.
Los valores convertidos no regresan al dominio para continuar cálculos.

Configuración y ejemplos en el [README principal](../README.md). La evidencia
de ejecución y el alcance de las comprobaciones de ventanas están en
[VALIDACION.md](../VALIDACION.md).
