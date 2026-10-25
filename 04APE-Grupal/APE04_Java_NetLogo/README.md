# APE04 — SIR en Java y visualización con NetLogo

Java simula contagios y recuperaciones por pasos con individuos S/I/R y
exporta una tabla, CSV y PNG. NetLogo importa esas series y las reproduce;
no ejecuta un segundo motor de contagios. No es un simulador M/M/c.

La [guía de uso existente](LEEME_PRIMERO.md) describe los botones, parámetros,
ejemplos y exportaciones. Se conservan sus instrucciones válidas y el método
de compilación original.

## Requisitos y scripts existentes

JDK 17 o posterior para compilar; Java 17 o posterior para ejecutar. El código
usa únicamente la biblioteca estándar, incluidos Swing, AWT e ImageIO. Bash
es necesario para los scripts. NetLogo 7.0.4 se instala por separado para
abrir `netlogo/modelo_sir_netlogo.nlogox` con sus tres archivos `.nls` y CSV.

Desde `04APE-Grupal/APE04_Java_NetLogo`:

```bash
bash compilar.sh
bash ejecutar.sh --semilla 42 --sin-grafica
bash abrir_netlogo.sh
```

`--sin-grafica` guarda el PNG sin abrir la ventana Java. El script de ejecución
guarda además `resultados/ultima_ejecucion_java.txt`. Sin esa opción, Java
intenta abrir su ventana si el entorno lo permite.

## Compilar y ejecutar con Maven

Maven 3.6.3 o posterior y JDK 17 o posterior. El POM conserva `src/sir`,
configura UTF-8, compila con `release 17` y establece `sir.Main` como entrada:

```bash
mvn clean package
java -jar target/ape04-sir-1.0.0.jar --semilla 42 --sin-grafica
java -jar target/ape04-sir-1.0.0.jar --ayuda
```

Ejecuta el JAR desde la raíz del proyecto para que las rutas relativas
apunten a `netlogo/` y `resultados/`. El artefacto contiene las clases Java;
el modelo, los archivos `.nls` y los CSV permanecen junto al proyecto y no se
instalan dentro del JAR. Maven descarga plugins de construcción; no se añaden
bibliotecas externas al programa.

Opciones de salida para conservar archivos anteriores:

```bash
java -jar target/ape04-sir-1.0.0.jar --semilla 7 --sin-grafica --csv /tmp/ape04-copia.csv --png /tmp/ape04-copia.png
```

Los valores por defecto son `netlogo/java_simulado.csv` y
`resultados/grafica_sir_java.png`. Otra ejecución los reemplaza.

## Pruebas reales

```bash
bash pruebas.sh
bash pruebas_netlogo.sh "/ruta/real/NetLogo 7.0.4"
```

Son programas Java independientes en `pruebas/`. `mvn test` no los compila ni
los ejecuta; la fase de pruebas Maven no tiene pruebas integradas. El segundo
script necesita la carpeta real de NetLogo 7.0.4 con `lib/app` y `extensions`,
no el lanzador. La validación de esta actualización está en
[VALIDACION_MAVEN.md](VALIDACION_MAVEN.md).

## Organización y explicación

- [src](src/README.md): paquetes `sir.model`, `sir.controller`, `sir.view` y `sir.io`.
- [netlogo](netlogo/README.md): importación y representación de los CSV Java.
- [pruebas](pruebas/README.md): comprobaciones del modelo y del importador.
- [resultados](resultados/README.md): PNG y registro de ejemplo.
- [GUIA_CODIGO.md](GUIA_CODIGO.md): MVC, POO, responsabilidades y algoritmo.
- [ALGORITMO_COMUN.md](ALGORITMO_COMUN.md) y [COMPARACION_HERRAMIENTAS.md](COMPARACION_HERRAMIENTAS.md): interpretación y herramientas.

En esta sesión se utilizó Codex para revisar las instrucciones, añadir el POM
y comprobar la construcción y las pruebas en una copia temporal. Esta
actualización conserva los algoritmos y no atribuye autoría histórica de IA.
