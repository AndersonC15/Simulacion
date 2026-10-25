# APE 04 — SIR con Java y NetLogo

Java calcula toda la simulación SIR y exporta sus resultados. NetLogo importa esos datos y reproduce las curvas y los estados reales de las personas. La comparación A/B corresponde a dos ejecuciones Java y es una función adicional del proyecto.

## Ejecutar

Requisitos: JDK 21, una terminal y, para el visor, NetLogo 7.0.4 instalado y una sesión gráfica. La construcción necesita acceso a Maven Central la primera vez. Maven Wrapper descarga Maven 3.9.12; si ya tienes Maven, también puedes utilizarlo directamente.

Desde `04APE_Grupal`:

```bash
./mvnw clean verify
java -jar target/sir.jar
java -jar target/sir.jar --sin-netlogo
java -jar target/sir.jar --netlogo "/ruta/real/de/NetLogo-7.0.4"
```

La ruta de NetLogo es un ejemplo: reemplázala por la carpeta real que contiene `lib` y `extensions`. También se admite `NETLOGO_HOME`, la detección por el ejecutable `netlogo` en `PATH` y las carpetas habituales, incluida `~/Aplicaciones`.

Con Maven instalado:

```bash
mvn clean verify
mvn test
```

El único artefacto canónico es **`target/sir.jar`**, con `sir.Main` como clase principal. El antiguo `sir.jar` de la raíz, si está presente en una copia anterior, se conserva localmente e ignora en Git: los scripts y el visor utilizan las clases o el JAR que se están ejecutando, y no lo actualizan ni lo cargan. Recompila con Maven cuando modifiques el código.

La raíz se busca desde la ubicación real de las clases o del JAR. Se puede ejecutar el JAR por ruta absoluta desde otra carpeta, también con espacios:

```bash
cd /tmp
java -jar "/ruta/con espacios/04APE_Grupal/target/sir.jar" --sin-netlogo
```

Conserva `target/sir.jar` dentro del proyecto, junto a `pom.xml` y la carpeta fuente `netlogo/`. El JAR no contiene una distribución de NetLogo ni es un paquete portátil independiente del proyecto.

## Modelo y escenarios

| Parámetro | Valor base |
|---|---:|
| Población N | 100 |
| Susceptibles iniciales S0 | 95 |
| Infectados iniciales I0 | 5 |
| Recuperados iniciales | 0 |
| Beta por contacto y paso | 0.30 |
| Gamma por paso | 0.10 |
| Pasos | 100 |
| Contactos por infectado y paso | 1 |
| Semilla de ejemplo | 42 |

Cada paso toma una copia de los estados. Cada infectado de esa copia selecciona contactos de toda la población, con reemplazo y pudiendo elegirse a sí mismo. Si el contacto era susceptible se intenta contagiar con beta; después se intenta recuperar al infectado original con gamma. Los recién infectados actúan y pueden recuperarse desde el paso siguiente. La exportación consulta copias defensivas y no consume números aleatorios.

Se conserva `S + I + R = N`. Es una simulación discreta por individuos, no un solucionador de ecuaciones diferenciales. Las regresiones verificadas son: semilla 42, final `S=4, I=0, R=96`, con pico `I=49` en `t=20`; semilla 7, final `S=9, I=0, R=91`.

Beta y gamma se conservan como `double` de Java: precisión binaria finita, aproximadamente 15–17 cifras decimales significativas. No se redondean para decidir contagios, recuperaciones ni condiciones. El cociente nominal `contactos * beta / gamma` se presenta por separado usando `BigDecimal` con `DECIMAL128`; esa presentación no interviene en la simulación. Si gamma es cero se indica infinito o indefinido según el numerador.

```bash
java -jar target/sir.jar --beta 0.10 --semilla 42
java -jar target/sir.jar --gamma 0.30 --semilla 42
java -jar target/sir.jar --poblacion 200 --infectados 10 --pasos 150
java -jar target/sir.jar --beta 0.299999 --gamma 0.30 --sin-netlogo
java -jar target/sir.jar --csv "netlogo/datos/mi escenario.csv" --sin-netlogo
java -jar target/sir.jar --ayuda
```

Usa punto decimal. Los ejemplos existentes `resultados_java`, `otra_semilla`, `menor_contagio` y `mayor_recuperacion` se conservan con sus CSV, PNG y parámetros. Si no tienen archivo individual, se muestran sus curvas y se indica que el detalle no está disponible. No se reconstruyen identidades a partir de conteos. Una sola trayectoria no demuestra una tendencia estadística general.

## Archivos que produce

Sin `--csv`, cada ejecución genera un nombre nuevo en **`netlogo/datos/` del proyecto**, incluso al ejecutar desde otra carpeta. Un `--csv` relativo se resuelve desde el directorio actual de la terminal.

Para `ejemplo.csv` se escriben cuatro archivos:

| Archivo | Contenido |
|---|---|
| `ejemplo.csv` | Conteos agregados de cada instante |
| `ejemplo_individuos.csv` | Estado real de cada persona en cada instante |
| `ejemplo.png` | Gráfica Java completa |
| `ejemplo.properties` | Parámetros, semilla, tiempo de cálculo y huellas SHA-256 de los CSV |

Ambos CSV usan UTF-8 y comienzan en `t=0`. Contrato agregado:

```csv
tiempo,susceptibles,infectados,recuperados
0,95,5,0
1,93,7,0
```

Contrato individual (fragmento ilustrativo del formato):

```csv
tiempo,id,estado
0,0,SUSCEPTIBLE
0,1,INFECTADO
```

Los estados válidos son `SUSCEPTIBLE`, `INFECTADO` y `RECUPERADO`. Los identificadores son enteros estables de `0` a `N-1`, ordenados dentro de cada tiempo; los tiempos son consecutivos. Para 100 personas y 100 pasos hay **10100 registros individuales más el encabezado**. Los conteos de cada paso coinciden exactamente con el CSV agregado. El detalle se escribe progresivamente; no se conserva todo ese historial en memoria.

El controlador reserva los nombres de las cuatro salidas mediante archivos `.lock`, prepara temporales en el mismo directorio y publica el agregado al final. Rechaza cualquier salida existente, incluido el compañero individual. Ante un fallo ordinario retira solamente archivos que creó esa operación. No hay una transacción atómica de cuatro archivos frente a cortes de energía o procesos externos que ignoren las reservas. No borres los `.lock` mientras haya una exportación activa.

Las huellas permiten detectar modificaciones y mezclas de archivos en las nuevas ejecuciones. No certifican autoría. En parejas externas sin huellas se valida la coherencia completa de estados y conteos, pero dos historias compatibles con los mismos agregados no permiten demostrar su procedencia. Los resultados existentes no se borran ante un error.

## Usar la ventana

| Control | Función |
|---|---|
| GENERAR ESCENARIO | Ejecuta Java, guarda los cuatro archivos y comienza la reproducción |
| ABRIR CSV | Carga un CSV agregado como A y queda en t=0 |
| COMPARAR CON OTRO CSV | Carga una segunda ejecución como B y vuelve a t=0 |
| QUITAR COMPARACIÓN | Retira B conservando A |
| PAUSAR / CONTINUAR | Detiene o reanuda personas y curvas; desde el final reinicia |
| REINICIAR | Regresa a t=0 y queda pausado |
| UN PASO | Avanza una fila y queda pausado |
| VER COMPLETO | Muestra curvas y estados individuales finales reales |
| Pausa entre pasos | Regula la reproducción entre 20 y 500 ms |
| GUARDAR VISTA PNG | Guarda la interfaz NetLogo completa en `resultados/netlogo_....png` |
| Cierre de ventana / Ctrl+Q | Detiene el reloj, cierra las lecturas y libera el motor |

Se conservan cinco gráficas: S/I/R de A, S/I/R de B y las comparaciones de susceptibles, infectados y recuperados. Hay **una sola vista de personas**, dividida en zona A y zona B. Cada persona se identifica por ejecución e ID exportado; no se utiliza `who` como identidad del modelo.

Las posiciones forman una cuadrícula fija: Java no exporta distancias ni contactos físicos. No se simulan contagios en NetLogo, no hay movimientos epidemiológicos ni líneas de transmisión. La asignación S/I/R conserva los colores de las curvas: verde `#00AB4D`, infectados `#0B1220` y recuperados `#829A90`. El fondo de esa vista usa el tono claro existente `#E0F7EF` para que los infectados oscuros sean visibles. El marco Swing conserva fondo oscuro, verde neón y texto claro.

Si B no está cargada se indica explícitamente. Si falta el detalle se conservan las curvas y no se crean personas ficticias. Para horizontes distintos, cada ejecución mantiene su último estado real; sus curvas no añaden puntos fuera de sus datos. Las poblaciones distintas se comparan como conteos absolutos.

El visor incluye desplazamiento para las gráficas y las personas; los controles se organizan para pantallas de 1366×768. La ventana integrada no muestra las pestañas Información y Código. También se puede abrir `netlogo/modelo_sir_netlogo.nlogox` en el editor normal de NetLogo 7.0.4, que conserva sus propias pestañas.

## Estructura y código

| Ubicación | Responsabilidad |
|---|---|
| `pom.xml`, `mvnw`, `mvnw.cmd`, `.mvn/wrapper/` | Construcción y Wrapper oficial |
| `src/main/java/sir/model/` | Individuos, estados, parámetros y reglas SIR |
| `src/main/java/sir/controller/` | Coordinación del modelo y publicación de resultados |
| `src/main/java/sir/io/` | Estrategia agregada, exportación individual, lectores y huellas |
| `src/main/java/sir/view/` | PNG Java, Swing y adaptador por reflexión a NetLogo |
| `src/main/java/sir/` | Entrada, opciones y detección de la instalación |
| `netlogo/datos.nls`, `individuos.nls` | Validación y lectura de CSV |
| `netlogo/vista.nls`, `personas.nls` | Curvas y representación de personas |
| `netlogo/controlador.nls` | Carga y reproducción |
| `src/test/java/sir/pruebas/` | JUnit por responsabilidad, integración y GUI |
| `pruebas/` | Script, documentación de validación e informes históricos |
| `target/` | JAR, clases e informes generados; excluido de Git |

Se mantiene MVC, POO y `ExportadorResultados` inyectado al controlador. Swing, AWT, ImageIO, NIO, XML y SHA-256 son APIs del JDK. **No hay dependencias Maven de producción.** NetLogo se carga desde su instalación local mediante reflexión; no se declaran coordenadas inventadas ni se copia su distribución.

La única dependencia declarada es `org.junit.jupiter:junit-jupiter:5.12.2`, con alcance `test`. Plugins con versión explícita: Compiler 3.14.0, Surefire y Failsafe 3.5.3, JAR 3.4.2, Clean 3.4.1 y Resources 3.3.1. Los dos últimos pertenecen al ciclo normal de construcción. Failsafe comprueba el JAR después de empaquetarlo y ejecuta los perfiles externos.

`netlogo/` es la única ubicación fuente del modelo. El adaptador lee la lista `__includes` del modelo y reúne esos mismos archivos en una copia temporal para `InterfaceComponent`, que no aporta el editor de includes. La copia se elimina tras la carga. Maven no mantiene otra versión manual del modelo.

El Wrapper se generó mediante el [procedimiento oficial de Apache Maven](https://maven.apache.org/tools/wrapper/index.html):

```bash
mvn org.apache.maven.plugins:maven-wrapper-plugin:3.3.4:wrapper -Dmaven=3.9.12 -Dtype=only-script
```

El tipo oficial `only-script` incluye `mvnw`, `mvnw.cmd` y `maven-wrapper.properties`; no necesita `maven-wrapper.jar` ni un descargador Java inventado. La versión [Maven 3.9.12 está publicada por Apache](https://maven.apache.org/docs/3.9.12/release-notes.html).

## Límites y manejo de errores

- N entre 1 y 10000; I0 entre 0 y N.
- Beta y gamma finitas entre 0 y 1; pasos entre 0 y 2000; contactos entre 0 y 20.
- `N * max(1,pasos) * (contactos+1) <= 10000000`, calculado con `long`.
- Agregado: hasta 1 MiB y 2001 registros; líneas de hasta 256 caracteres.
- Individual: hasta 512 MiB, 20010000 registros como límite estructural y líneas de hasta 256 caracteres. Las ejecuciones nuevas también cumplen el límite de trabajo del modelo.

Son límites técnicos del proyecto. Se rechazan encabezados incorrectos, UTF-8 inválido, archivos vacíos o truncados, IDs duplicados o ausentes, tiempos con saltos, estados desconocidos, transiciones imposibles y diferencias de conteos. Selecciona el CSV agregado en el selector; elegir el individual produce un mensaje y conserva la ejecución anterior. La memoria del detalle es proporcional a N, no al historial completo.

Los archivos deben mantenerse estables durante la reproducción. No se implementa vigilancia continua de cambios externos en el disco. Un cierre forzado puede dejar reservas o salidas incompletas; revisa esa ejecución y usa otro nombre. Con poblaciones grandes las figuras se reducen y la lectura/representación puede tardar: el límite de datos no garantiza legibilidad individual para 10000 personas.

La API local de NetLogo exige crear los widgets y compilar `InterfaceComponent` en el hilo gráfico. Esa inicialización puede producir una espera al abrir la ventana. La preparación de archivos, la simulación Java, las validaciones y las órdenes de reproducción se realizan en el trabajador; el temporizador no acumula avances mientras está ocupado.

## Recompilar y probar

```bash
./mvnw clean verify
mvn clean verify
mvn test
```

`test` ejecuta las pruebas del modelo, opciones, validaciones y exportación. Surefire falla si no descubre pruebas. `verify` añade los casos del JAR, ejecutando la terminal en otras JVM para aislar los códigos de salida. Informes nuevos: `target/surefire-reports/` y `target/failsafe-reports/`. Los informes anteriores de `pruebas/RESULTADOS_*.md` se conservan como históricos y no prueban esta versión.

Integración real con NetLogo, sin pantalla:

```bash
./mvnw -Pnetlogo -Dnetlogo.home="/ruta/real/de/NetLogo-7.0.4" verify
```

Pruebas de la ventana Swing integrada, en una sesión gráfica:

```bash
./mvnw -Pgui -Dnetlogo.home="/ruta/real/de/NetLogo-7.0.4" verify
```

Ejecuta los perfiles `netlogo` y `gui` por separado: sus JVM tienen configuraciones gráficas distintas. Si no se solicita un perfil, sus pruebas externas no se ejecutan. Si falta su instalación o pantalla, las pruebas correspondientes se informan como omitidas, sin contarlas como aprobadas. Si usas una pantalla virtual, debes tener Xvfb instalado; no es dependencia de producción.

El script compatible utiliza Maven Wrapper y admite:

```bash
bash pruebas/verificar.sh
bash pruebas/verificar.sh "/ruta/real/de/NetLogo-7.0.4"
bash pruebas/verificar.sh "/ruta/real/de/NetLogo-7.0.4" --interfaz
```

Los resultados comprobados y el entorno de esta revisión se registran en `pruebas/VALIDACION_MAVEN.md`. No se reutilizan informes históricos para declarar que pasan las pruebas nuevas.

## Alcance de la entrega y uso de IA

Esta entrega comprende el código, la construcción, la visualización y las pruebas. El informe académico, el video y la exposición quedan fuera del trabajo actual. La guía disponible describe la práctica SIR y la importación de CSV; no se atribuye a ella la exigencia de dos escenarios Java ni siete gráficas. Comparar A/B no equivale a comparar implementaciones independientes en varios lenguajes.

Se utilizó ChatGPT/Codex para inspeccionar y modificar código, integrar Maven, diseñar y ejecutar pruebas y actualizar las instrucciones. La asistencia fue sustancial; no se inventa un porcentaje ni se presenta el código como elaborado sin ayuda. El grupo debe estudiar, adaptar, verificar y declarar la asistencia conforme a las reglas del docente.
