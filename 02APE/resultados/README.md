# Resultados regenerables de APE02

Desde `02APE`, con su entorno activado:

```bash
MPLBACKEND=Agg python main.py --comparar --graficas
MPLBACKEND=Agg python main.py --escenarios
```

El primer comando guarda `comparacion.png` y `comparacion.csv`. El segundo
genera pares PNG/CSV para `crecimiento`, `decrecimiento` y `constante`. Se
puede elegir otra carpeta con `--salida "/ruta/con espacios"`. La ubicación
por defecto se resuelve desde el proyecto, independientemente del directorio
de la terminal.

Los PNG tienen título, tiempo en períodos, población, leyenda y cuadrícula.
Las observaciones son cruces negras, el discreto se dibuja por escalones y
Euler se identifica como aproximación. En escenarios de decrecimiento las
observaciones siguen siendo el arreglo de referencia original creciente.

Los CSV contienen `modelo,tiempo_periodos,poblacion`, una fila por punto de
cada serie y las observaciones de referencia. Se escriben los valores Decimal
sin limitar decimales. No se leen estos archivos para continuar cálculos.

Una nueva generación reemplaza archivos del mismo nombre usando temporales.
PNG y CSV se reemplazan por separado: un fallo puede dejar actualizado uno y
conservar el otro anterior. Para conservar una ejecución elige otro directorio.
Las figuras se cierran al terminar. La exportación NetLogo tiene reglas
separadas y rechaza sus archivos de salida si ya existen.

Consulta [README](../README.md) para interpretar métodos y parámetros, y
[VALIDACION.md](../VALIDACION.md) para los comandos realmente comprobados.

El envío `python main.py --netlogo` exporta `netlogo-<identificador>.csv`;
`--netlogo-gui` añade el PNG de interfaz del mismo envío. El identificador
conserva ejecuciones anteriores y el puente rechaza destinos existentes. El
ejemplo de GUI comprobado se guardó como `netlogo_oficial.png` junto a su CSV.
El CSV exportado por NetLogo contiene los datos del plot y una cabecera propia,
incluida su fecha; no se promete igualdad binaria entre esas exportaciones.

Los ejemplos PNG y el CSV `netlogo_oficial.csv` se conservan en Git para
consultarlos al descargar el proyecto. `analisis_ruido.txt` registra la salida
reproducible de `python main.py --analizar-ruido`; se puede regenerar
redirigiendo esa salida.
