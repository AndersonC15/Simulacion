# APE 04 - Java + NetLogo 7.0.4

Java genera los datos del SIR. NetLogo solamente los importa y los representa. No existe un motor de contagios en NetLogo.

## Ejecutar ahora en Ubuntu

Descomprime TODO el ZIP. Abre una terminal dentro de APE04_Java_NetLogo y ejecuta:

```bash
bash ejecutar.sh --semilla 42 --sin-grafica
bash abrir_netlogo.sh
```

Si tu lanzador `netlogo` no se reconoce, abre NetLogo 7.0.4 y selecciona Archivo > Abrir > `netlogo/modelo_sir_netlogo.nlogox`.

Los CSV ya estan incluidos y el modelo los carga automaticamente al abrir. Puedes abrir NetLogo sin ejecutar Java otra vez para ver el ejemplo.

## Funcionamiento

1. Java crea 100 individuos: S=95, I=5, R=0. Ejecuta 100 pasos con beta=0.30 y gamma=0.10.
2. Escribe `netlogo/java_simulado.csv`: tiempo,susceptibles,infectados,recuperados; 101 registros mas encabezado.
3. NetLogo abre ese archivo y dibuja sus datos exactamente como estan.
4. REINICIAR + ANIMAR reproduce las filas existentes. No se recalculan contagios.

## Cinco graficas

- Evolucion S/I/R del CSV principal.
- Evolucion S/I/R de una referencia opcional, tambien generada por Java.
- Comparacion de susceptibles entre ambas ejecuciones Java.
- Comparacion de infectados.
- Comparacion de recuperados.

El archivo opcional `java_referencia.csv` se genero realmente con Java y semilla 7. Solo sirve para tener una segunda ejecucion que comparar; no es obligatorio para visualizar el CSV principal. Principal: azul. Referencia: naranja. En las graficas S/I/R: S azul, I rojo, R verde.

## Botones

| Boton | Accion |
|---|---|
| CARGAR JAVA | Recarga java_simulado.csv |
| OTRO PRINCIPAL | Selecciona otro CSV Java con el mismo formato |
| CARGAR REFERENCIA | Carga java_referencia.csv |
| OTRA REFERENCIA | Selecciona una segunda ejecucion Java |
| REINICIAR | Vuelve a t=0 |
| ANIMAR | Boton continuo: avanza por las filas hasta t=100 |
| VER COMPLETO | Muestra todas las filas |
| EXPORTAR INTERFAZ PNG | Guarda resultados/interfaz_netlogo.png desde la aplicacion grafica |

Deten ANIMAR antes de cargar archivos. Puedes ajustar la velocidad desde el control de NetLogo. Maximiza la ventana si no ves todas las graficas.

## Tecnologias

Tu Java 21 es compatible. Para recompilar se necesita JDK (`javac --version`). El codigo usa solo la biblioteca estandar de Java; no hay librerias externas, Maven ni Gradle. NetLogo usa su extension csv incorporada. No se necesita Python.

Se incluyen clases compiladas para Java 17 compatibles con Java 21. Si solo tienes un JRE y no un compilador, ejecuta directamente desde la raiz:

```bash
java -cp out sir.Main --semilla 42 --sin-grafica
```

## Otras ejecuciones

```bash
bash ejecutar.sh --semilla 7 --sin-grafica
bash ejecutar.sh --semilla 42
bash ejecutar.sh --ayuda
```

Sin `--sin-grafica`, Java tambien abre su ventana. El PNG se guarda en ambos casos.

Para regenerar solo la referencia sin reemplazar el principal:

```bash
java -cp out sir.Main --semilla 7 --sin-grafica --csv netlogo/java_referencia.csv --png resultados/grafica_java_referencia.png
```

Puedes usar `--csv ruta` y `--png ruta`. Si eliges otro nombre de CSV, abre ese archivo con OTRO PRINCIPAL.

## Archivos y resultados

- src/sir: Java con modelo, vista, controlador y exportacion.
- netlogo: modelo .nlogox, tres archivos .nls y los CSV.
- resultados: PNG Java, registro de ejecucion y ejemplo de referencia.
- pruebas: pruebas del modelo y del importador.
- GUIA_CODIGO.md: responsabilidades MVC, POO y SOLID.
- COMPARACION_HERRAMIENTAS.md: tabla tecnica de Java y NetLogo.

El ejemplo principal usa semilla 42: pico de 49 infectados en t=20; final S=4, I=0, R=96. La referencia Java con semilla 7: pico de 35 en t=13; final S=9, I=0, R=91.

## Pruebas opcionales

```bash
bash pruebas.sh
bash pruebas_netlogo.sh "/ruta/real/a/NetLogo 7.0.4"
```

La segunda necesita la carpeta de instalacion que contiene lib/app, no el comando lanzador. No es necesario ejecutarlas para usar el proyecto.

Conserva juntos el .nlogox, los tres .nls y el CSV. Si NetLogo rechaza un archivo, revisa sus cuatro columnas, t=0..100, inicio 95/5/0 y S+I+R=100. El CSV no tiene que terminar obligatoriamente con todos recuperados.

No se incluyen informe academico, conclusiones ni video. El paquete cubre la implementacion tecnica; no representa una nota ni un porcentaje oficial de la rubrica.
