# Validación de la revisión Maven

Ejecución del 25 de octubre de 2026 en Ubuntu 26.04.1 LTS, OpenJDK 21.0.12.1 y Maven 3.9.12. NetLogo instalado: `~/Aplicaciones/NetLogo 7.0.4`. Las pruebas gráficas se ejecutaron en la sesión gráfica local; no se utilizó Xvfb ni se incorporó Python.

## Resultados comprobados

| Grupo | Casos distintos | Fallos | Errores | Omitidos |
|---|---:|---:|---:|---:|
| Modelo, parámetros, opciones, archivos e individuos | 187 | 0 | 0 | 0 |
| JAR y terminal, en JVM separada | 7 | 0 | 0 | 0 |
| Motor NetLogo sin pantalla | 72 | 0 | 0 | 0 |
| Ventana Swing y componente NetLogo real | 34 | 0 | 0 | 0 |
| Total distinto | **300** | **0** | **0** | **0** |

Cada invocación de `verify` repite las 187 pruebas unitarias y las siete del JAR; esos casos repetidos no se suman de nuevo al total. Los perfiles externos se ejecutaron por separado. Las 42 pruebas individuales forman parte de las 187, no se suman otra vez.

Surefire y Failsafe generaron XML/TXT en `target/surefire-reports/` y `target/failsafe-reports/`. Las capturas de esta revisión están en `target/test-artifacts/visor.png` y `target/test-artifacts/personas.png`; esta última permite inspeccionar las cinco gráficas y la única vista A/B completa. Se conservaron allí los informes XML externos y los registros de ejecución al realizar la última construcción limpia; no se reutilizaron los informes históricos del proyecto.

## Comandos ejecutados

El repositorio de dependencias y la caché del Wrapper se ubicaron temporalmente bajo `/tmp` por las restricciones de escritura del entorno de ejecución. Esto no está fijado en el POM ni es necesario en el equipo del usuario.

```bash
mvn -Dmaven.repo.local=/tmp/ape04-m2 org.apache.maven.plugins:maven-wrapper-plugin:3.3.4:wrapper -Dmaven=3.9.12 -Dtype=only-script
MAVEN_USER_HOME=/tmp/ape04-wrapper MAVEN_OPTS=-Dmaven.repo.local=/tmp/ape04-m2 ./mvnw clean verify
MAVEN_OPTS=-Dmaven.repo.local=/tmp/ape04-m2 mvn clean verify
MAVEN_USER_HOME=/tmp/ape04-wrapper MAVEN_OPTS=-Dmaven.repo.local=/tmp/ape04-m2 ./mvnw -Pnetlogo '-Dnetlogo.home=/home/anderson-coello/Aplicaciones/NetLogo 7.0.4' verify
MAVEN_USER_HOME=/tmp/ape04-wrapper MAVEN_OPTS=-Dmaven.repo.local=/tmp/ape04-m2 ./mvnw -Pgui '-Dnetlogo.home=/home/anderson-coello/Aplicaciones/NetLogo 7.0.4' verify
java -jar target/sir.jar --sin-netlogo
java -jar target/sir.jar --ayuda
bash -n pruebas/verificar.sh
sh -n mvnw
git diff --check -- .
```

También se ejecutaron `mvn test` y pruebas focalizadas de individuos durante el desarrollo. Las descargas iniciales fallaron dentro del entorno sin red; se completaron con la autorización automática para descargar los artefactos oficiales de Maven Central. No hubo rechazo de aprobación pendiente.

Se abrió el JAR real desde otra carpeta mediante la ruta `/tmp/APE04 con espacios/target/sir.jar`, en una copia temporal del proyecto sin `sir.jar` en la raíz. Se comprobó el modo con `--netlogo` explícito y el modo de detección automática. Una instrumentación Java temporal, externa al proyecto, comprobó 100 personas, registró que el subproceso cargaba `target/sir.jar`, guardó la propia ventana y envió su evento normal de cierre. El proceso terminó con código 0. La instrumentación no forma parte del producto ni utiliza capturas del escritorio.

La terminal y el modelo confirmaron semilla 42: `100,4,0,96`, pico de 49 infectados en t=20; semilla 7: `100,9,0,91`. La ejecución base exportó 10100 registros individuales más encabezado; las pruebas verificaron todos sus conteos e identidades, no únicamente la última fila.

## Defectos encontrados y correcciones

- Las rutas antiguas buscaban clases y `sir.jar` desde la raíz. Se resuelven desde la ubicación real del artefacto; el subproceso usa el mismo origen. Los datos predeterminados se guardan junto al proyecto.
- El agregado no contenía identidades. Se añadió escritura progresiva del estado real y validación completa, con huellas opcionales y protección de las cuatro salidas.
- A y B con el mismo archivo compartían el cursor NetLogo. Se detecta la lectura compartida y se reutiliza la instantánea correcta, preservando las identidades de ambas zonas.
- Una serie vacía con una ruta de detalle conservada provocaba `first []`. La disponibilidad individual exige una serie cargada.
- Un ejemplo histórico corrupto durante `startup` impedía cargar otro archivo válido. La carga automática inicial informa el problema sin impedir la carga solicitada.
- La apertura del componente integrado desde el trabajador produjo `not event thread`. Se verificó la API local: creación de widgets/compilación requieren EDT, mientras que órdenes/reportes se ejecutan fuera de EDT. El adaptador respeta ambas restricciones.
- Las acciones de botones se descartaban mientras el trabajador estaba ocupado. Ahora se serializan; el reloj omite pulsos y una revisión cancela inicios pendientes después de pausar o cerrar.
- `--sin-netlogo` podía intentar usar una pantalla declarada pero inaccesible al crear el PNG. Activa el modo gráfico en memoria antes de dibujar. Las pruebas del JAR ahora se ejecutan con un DISPLAY deliberadamente inválido, sin forzar ese modo desde el test.
- Dos pruebas de captura fallaron por el permiso de escritorio del sistema. Se sustituyeron por `printAll` de la propia ventana en EDT. La suite gráfica completa posterior pasó sus 34 casos.

Los intentos fallidos anteriores no se presentan como aprobados; la tabla corresponde a las ejecuciones corregidas. No se desactivaron validaciones para obtener esos resultados.

## Límites pendientes

La inicialización de widgets/compilación de `InterfaceComponent` debe usar EDT por exigencia de NetLogo y puede producir una espera inicial. Simulación, exportación, validación y reproducción utilizan el trabajador. Los archivos deben mantenerse estables durante la reproducción; no hay vigilancia continua de modificaciones externas ni transacción atómica de cuatro archivos frente a un cierre forzado.

Los CSV históricos sin detalle conservan sus curvas y muestran que las personas no están disponibles. Sin huellas no se puede demostrar el origen de dos historias individuales compatibles con los mismos conteos. No se promete legibilidad individual de 10000 figuras, inmunidad a fallos del sistema ni portabilidad del visor a sistemas no probados. Windows/macOS no se ejecutaron en esta revisión.
