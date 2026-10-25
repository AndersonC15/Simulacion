# Practica4 — copia SIR Java conservada

Esta carpeta contiene otra implementación SIR Java con `src/sir` y clases
compiladas en `out/`. Se conserva en su ubicación original. La versión del
portafolio con scripts, pruebas, POM e importador NetLogo se encuentra en
[04APE-Grupal/APE04_Java_NetLogo](../04APE-Grupal/APE04_Java_NetLogo/README.md).

El código de esta carpeta utiliza solo la biblioteca estándar. Para compilar
con un JDK 17 o posterior, desde `Practica4`:

```bash
javac -encoding UTF-8 --release 17 -d out src/sir/Main.java src/sir/model/*.java src/sir/view/*.java src/sir/controller/*.java
java -cp out sir.Main --semilla 42 --sin-grafica
```

`--sin-grafica` evita la ventana, pero guarda `grafica_sir_java.png` y
`resultados_java.csv` respecto al directorio de ejecución. `--csv ruta` cambia
el destino CSV; `--ayuda` muestra las opciones. Las salidas se reemplazan al
repetir la ejecución. Para conservar ejemplos y clases versionadas, compila y
prueba en una copia temporal. Aquí no hay pruebas automatizadas ni archivos
del modelo NetLogo. Esta documentación no modifica el algoritmo.
