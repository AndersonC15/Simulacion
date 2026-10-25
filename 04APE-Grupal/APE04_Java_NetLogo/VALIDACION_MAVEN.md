# Validación de Maven y ejecución — 24 de octubre de 2026

Estas comprobaciones pertenecen a la actualización de documentación y
manifiestos del portafolio. No reemplazan las declaraciones históricas de
`VALIDACION.md` ni atribuyen pruebas nuevas a sesiones anteriores.

## Entorno y aislamiento

Linux amd64, Maven 3.9.12, JDK OpenJDK 21.0.12.1. El código original y los CSV
se copiaron a una carpeta temporal; la construcción, las pruebas y las
exportaciones se ejecutaron allí. No se recompilaron ni reemplazaron los
`out/`, CSV, PNG o registros versionados del repositorio.

El POM conserva `src/sir`, UTF-8, `--release 17` y la entrada `sir.Main`.
`javap -verbose target/classes/sir/Main.class` confirmó major version 61
(Java 17), y el manifiesto del JAR contiene `Main-Class: sir.Main`.
El mínimo Maven 3.6.3 se contrastó con los metadatos de los plugins usados.
En esta actualización se ejecutó el programa con JDK 21, no con un runtime 17.

## Comandos y resultados

Desde la raíz de la copia temporal del proyecto:

```bash
mvn clean package
java -Djava.awt.headless=true -jar target/ape04-sir-1.0.0.jar --semilla 42 --sin-grafica
java -jar target/ape04-sir-1.0.0.jar --ayuda
bash ejecutar.sh --semilla 42 --sin-grafica
bash pruebas.sh
bash pruebas_netlogo.sh "/ruta/real/NetLogo 7.0.4"
```

- Maven: `BUILD SUCCESS`; compiló los 11 archivos Java y creó
  `target/ape04-sir-1.0.0.jar`.
- Maven informó `No tests to run`: sus fases no ejecutan los programas de
  `pruebas/`. No se considera `mvn test` una validación de esas pruebas.
- JAR y script original: pico de 49 infectados en t=20; final S=4, I=0, R=96.
  El CSV tiene 102 líneas, incluido el encabezado; inicio 0,95,5,0 y final
  100,4,0,96. Se comprobó la firma PNG de la imagen generada.
- El CSV regenerado con semilla 42 coincide byte por byte con el ejemplo
  versionado. Esta comparación lee el original sin reemplazarlo.
- `bash pruebas.sh`: `OK: 15167 comprobaciones Java. Conservacion, semillas,
  limites y CSV.` Es la cantidad de aserciones informada por la suite existente,
  no 15167 escenarios independientes.
- Prueba real con NetLogo 7.0.4 instalado: el script abrió el `.nlogox` mediante
  `HeadlessWorkspace`, cargó ambos CSV, comparó sus datos y reprodujo t=0..100.
  Resultado: `OK: NetLogo 7.0.4 importa exactamente ambos CSV Java y reproduce
  t=0..100.` No se utilizaron mocks para este resultado.

## Incidencias y límites

Los primeros intentos Maven en modo offline encontraron dependencias de
plugins que no estaban completas en la caché. Se seleccionaron versiones
explícitas de plugins disponibles y se repitió `mvn clean package` con éxito.
El POM final no contiene dependencias externas del programa. Una instalación
sin la caché necesita Internet para descargar los plugins Maven.

Las verificaciones descritas fueron sin ventanas. No acreditan una nueva
prueba visual de Swing o de la interfaz gráfica NetLogo ni una ejecución en
Windows/macOS. No se modifica el algoritmo SIR ni se reorganiza el proyecto.
