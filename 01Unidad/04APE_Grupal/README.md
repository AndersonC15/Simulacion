# APE04 — Simulación SIR con Java y visualización en NetLogo

**Asignatura:** Simulación · **Carrera:** Computación · **Ciclo:** Quinto · **Universidad:** Universidad Nacional de Loja (UNL)

**Tecnologías:** Java 21 · Maven · Swing · NetLogo 7.0.4 · JUnit Jupiter

> **Alcance de este README:** documentación del código actual en `04APE_Grupal/`. **Java calcula la simulación SIR y exporta los datos; NetLogo los importa, valida y representa.** La comparación A/B utiliza dos ejecuciones de Java, no dos implementaciones independientes del modelo.

## Contenido

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Tecnologías utilizadas](#2-tecnologías-utilizadas)
3. [Requisitos y preparación](#3-requisitos-y-preparación)
4. [Uso del programa](#4-uso-del-programa)
5. [Estructura del proyecto](#5-estructura-del-proyecto)
6. [Funcionamiento y resultados](#6-funcionamiento-y-resultados)
7. [Información adicional](#7-información-adicional)

---

## 1. Descripción del proyecto

Esta práctica representa la evolución de una población cerrada mediante los estados **susceptible (S), infectado (I) y recuperado (R)**. Su objetivo es observar cómo cambian esos grupos según la probabilidad de contagio, la probabilidad de recuperación y las condiciones iniciales.

La implementación utiliza individuos con identificadores estables y pasos discretos de tiempo. No resuelve numéricamente las ecuaciones diferenciales del SIR. En cada paso conserva la población total: **S + I + R = N**.

### Qué hace el programa

- Ejecuta el modelo en Java con parámetros y semilla configurables desde la terminal.
- Exporta los conteos S/I/R y el estado de cada individuo, además de una gráfica PNG y un archivo de parámetros.
- Muestra en la terminal el estado final, el pico de infectados y un cociente nominal de reproducción.
- Abre una ventana Swing que integra NetLogo para reproducir las curvas y los estados individuales exportados.
- Permite cargar una segunda ejecución como escenario B y compararla con A mediante cinco gráficas: una por escenario y tres comparaciones de S, I y R.
- Ofrece pausa, avance de un paso, reinicio, vista completa y exportación de la vista NetLogo.

Las personas de NetLogo ocupan una cuadrícula fija. Sus colores reproducen los estados calculados por Java; sus posiciones no representan contactos ni distancias epidemiológicas.

---

## 2. Tecnologías utilizadas

| Herramienta | Uso en esta práctica |
|:--|:--|
| **JDK 21** | Compilación y ejecución del modelo, terminal, archivos y gráficos. El `pom.xml` fija `release=21`. |
| **Maven** | Compilación, pruebas y creación del JAR ejecutable. |
| **Maven Wrapper** | Los scripts incluidos descargan Maven **3.9.12**, según `.mvn/wrapper/maven-wrapper.properties`. |
| **Swing, AWT e ImageIO** | Ventana de escritorio y generación de imágenes; pertenecen al JDK. |
| **NetLogo 7.0.4** | Importación de los CSV, reproducción, gráficas y representación de personas. El modelo utiliza la extensión `csv`. |
| **JUnit Jupiter 5.12.2** | Pruebas Java; es la única dependencia declarada y tiene alcance `test`. |

**No hay dependencias Maven de producción.** El adaptador carga las bibliotecas de una instalación local de NetLogo mediante reflexión; Maven no descarga ni empaqueta NetLogo dentro del JAR.

El `pom.xml` también fija las versiones de los plugins: Compiler 3.14.0, Surefire y Failsafe 3.5.3, JAR 3.4.2, Clean 3.4.1 y Resources 3.3.1.

---

## 3. Requisitos y preparación

### Requisitos previos

- **JDK 21**, con `java` disponible en la terminal y `JAVA_HOME` correctamente configurado si se utiliza.
- Una terminal y acceso a Internet en la primera construcción para descargar Maven y sus dependencias.
- **NetLogo 7.0.4 instalado y una sesión gráfica** para utilizar el visor integrado. La generación con `--sin-netlogo` funciona sin pantalla.
- Permiso de escritura en el proyecto y en la carpeta elegida para los resultados. El visor prepara un archivo temporal junto al modelo NetLogo.

Todos los comandos siguientes se ejecutan desde **`04APE_Grupal/`**, donde están `pom.xml`, `mvnw` y `netlogo/`, salvo que se indique otra carpeta.

### 3.1. Construir en Linux o macOS

Desde la raíz del repositorio:

```bash
cd 04APE_Grupal
java -version
./mvnw clean verify
```

Si la copia del repositorio perdió el permiso de ejecución del Wrapper, puede invocarse con `sh mvnw clean verify`.

### 3.2. Construir en Windows (PowerShell)

Desde la raíz del repositorio:

```powershell
cd 04APE_Grupal
java -version
.\mvnw.cmd clean verify
```

### 3.3. Usar Maven instalado

El Wrapper evita instalar Maven por separado. Si ya tienes Maven disponible, desde la carpeta de esta práctica puedes utilizar:

```bash
mvn clean verify
```

Los comandos corresponden a los scripts y al `pom.xml` actuales. No se comprobó aquí la ejecución en Windows o macOS. El lanzador del visor espera `lib/app/netlogo-7.0.4.jar` y configura `natives/linux-amd64`, por lo que su integración gráfica en otros sistemas requiere revisión y no se presenta como verificada.

---

## 4. Uso del programa

### 4.1. Generar resultados sin abrir NetLogo

Después de construir, desde `04APE_Grupal/`:

```bash
java -jar target/sir.jar --sin-netlogo
```

Este modo genera los cuatro archivos de resultados y el resumen de la terminal. También produce la gráfica PNG; `--sin-netlogo` evita abrir el visor. El alias anterior `--sin-grafica` tiene el mismo comportamiento.

### 4.2. Generar resultados y abrir el visor

```bash
java -jar target/sir.jar
```

Si NetLogo no se detecta automáticamente, indica su carpeta real:

```bash
java -jar target/sir.jar --netlogo "/ruta/real/NetLogo 7.0.4"
```

La ruta es un ejemplo: reemplázala por el directorio que contiene `lib/app/netlogo-7.0.4.jar` y `extensions/`. El lanzador también consulta `NETLOGO_HOME`, busca el ejecutable `netlogo` en `PATH` y revisa carpetas habituales como `~/Aplicaciones`.

La simulación y la exportación ocurren **antes de abrir el visor**. Si falta NetLogo o no hay pantalla, el programa informa del error y conserva las salidas que ya generó.

El artefacto definido en Maven es **`target/sir.jar`**, con `sir.Main` como entrada. Debe conservarse dentro del proyecto, junto a `pom.xml` y la carpeta `netlogo/`; no es un paquete independiente de esas fuentes ni incluye la distribución de NetLogo. Después de cambiar código, vuelve a construirlo.

### 4.3. Parámetros de la terminal

| Opción | Valor inicial | Significado y límites |
|:--|--:|:--|
| `--poblacion` | `100` | Población total, entre 1 y 10000. |
| `--infectados` | `5` | Infectados iniciales, entre 0 y N; inicialmente R=0 y S=N−I. |
| `--beta` | `0.30` | Probabilidad de contagio por contacto y paso, entre 0 y 1. |
| `--gamma` | `0.10` | Probabilidad de recuperación por paso, entre 0 y 1. |
| `--pasos` | `100` | Horizonte, entre 0 y 2000; siempre se exporta también t=0. |
| `--contactos` | `1` | Contactos por infectado y paso, entre 0 y 20. |
| `--semilla` | `42` | Entero de tipo `long` para reproducir la secuencia pseudoaleatoria. |
| `--csv` | Nombre automático | Ruta nueva para el CSV agregado; no sobrescribe salidas existentes. |
| `--netlogo` | Detección automática | Directorio de la instalación de NetLogo 7.0.4. |
| `--sin-netlogo` | Desactivado | Genera resultados sin abrir el visor. |
| `--ayuda` o `-h` | — | Muestra la ayuda y termina. |

Usa **punto decimal**. Beta y gamma deben ser finitas. Además de los límites individuales, el modelo exige `N * max(1,pasos) * (contactos+1) <= 10000000` para acotar el trabajo.

Ejemplos desde la carpeta de esta práctica:

```bash
java -jar target/sir.jar --beta 0.10 --semilla 42 --sin-netlogo
java -jar target/sir.jar --gamma 0.30 --semilla 42 --sin-netlogo
java -jar target/sir.jar --poblacion 200 --infectados 10 --pasos 150 --sin-netlogo
java -jar target/sir.jar --csv "netlogo/datos/mi escenario.csv" --sin-netlogo
java -jar target/sir.jar --ayuda
```

Sin `--csv`, las salidas se guardan con un nombre nuevo en `netlogo/datos/` **del proyecto**. Una ruta relativa indicada mediante `--csv` se resuelve desde el directorio actual de la terminal. Si repites el ejemplo con el mismo nombre, debes elegir otro para conservar los resultados anteriores.

La raíz del proyecto se localiza desde el JAR. Por eso puede ejecutarse por ruta absoluta desde otra carpeta:

```bash
java -jar "/ruta/real/04APE_Grupal/target/sir.jar" --sin-netlogo
```

### 4.4. Controles de la ventana integrada

La cabecera permite editar población, infectados iniciales, beta, gamma, pasos y semilla. **Los contactos se configuran en la terminal; el formulario utiliza el valor inicial 1 al generar una ejecución.**

| Control | Comportamiento |
|:--|:--|
| **GENERAR ESCENARIO** | Ejecuta Java con el formulario, guarda las salidas y comienza su reproducción. |
| **ABRIR CSV** | Carga un CSV agregado como A y vuelve a t=0. |
| **COMPARAR CON OTRO CSV** | Carga otra ejecución como B y vuelve a t=0. |
| **QUITAR COMPARACION** | Retira B y conserva A. |
| **PAUSAR / CONTINUAR** | Detiene o reanuda la reproducción; continuar desde el final la reinicia. |
| **REINICIAR** | Regresa a t=0 y queda pausado. |
| **UN PASO** | Avanza un instante y queda pausado. |
| **VER COMPLETO** | Muestra todas las curvas y los últimos estados individuales disponibles. |
| **Pausa entre pasos** | Ajusta la reproducción entre 20 y 500 ms. |
| **GUARDAR VISTA PNG** | Guarda el componente NetLogo completo en un archivo nuevo `resultados/netlogo_….png`. |
| **Cerrar / Ctrl+Q** | Detiene la reproducción, cierra las lecturas y libera el motor. |

Selecciona el **CSV agregado**, no `*_individuos.csv`. Los datos se validan antes de sustituir la ejecución visible. La ventana incluye desplazamiento para acceder a las gráficas y a la vista de personas.

También puede abrirse [el modelo fuente](netlogo/modelo_sir_netlogo.nlogox) en el editor normal de NetLogo 7.0.4. Ese editor conserva sus pestañas de Información y Código; la ventana Swing integrada presenta el visor y sus propios controles.

---

## 5. Estructura del proyecto

```text
04APE_Grupal/
├── pom.xml                         # Construcción, JAR y perfiles de pruebas
├── mvnw / mvnw.cmd                 # Maven Wrapper para Unix y Windows
├── .mvn/wrapper/                   # Configuración de la distribución Maven
├── src/
│   ├── main/java/sir/
│   │   ├── Main.java               # Entrada de terminal y búsqueda de la raíz
│   │   ├── Opciones.java           # Interpretación de opciones
│   │   ├── LanzadorNetLogo.java    # Detección y apertura del visor
│   │   ├── model/                 # Parámetros, individuos, estados y reglas SIR
│   │   ├── controller/            # Ejecución y coordinación de salidas
│   │   ├── io/                    # CSV, validaciones y huellas de archivos
│   │   └── view/                  # Gráfica Java, ventana y puente NetLogo
│   └── test/java/sir/pruebas/      # Pruebas JUnit y de integración
├── netlogo/
│   ├── modelo_sir_netlogo.nlogox   # Modelo y widgets
│   ├── datos.nls / individuos.nls # Lectura y validación de los CSV
│   ├── personas.nls / vista.nls   # Representación y gráficas
│   ├── controlador.nls            # Carga y reproducción
│   └── datos/                     # Ejemplos incluidos y salidas nuevas
├── pruebas/verificar.sh           # Acceso a los comandos Maven de validación
├── resultados/                    # Imagen incluida y capturas del visor
└── target/                        # JAR, clases e informes generados por Maven
```

`target/` es una salida de construcción excluida de Git. La carpeta `pruebas/` contiene actualmente el script indicado.

### Arquitectura y flujo

| Componente | Responsabilidad respaldada por el código |
|:--|:--|
| **Modelo Java** | `SimulacionSIR`, `ParametrosSIR`, `Individuo`, `Estado` y `ResultadoPaso` mantienen los estados y ejecutan las transiciones. |
| **Controlador Java** | `ControladorSIR` coordina la simulación y la publicación de las cuatro salidas. Recibe un `ExportadorResultados` para el agregado. |
| **Entrada/salida** | Los exportadores escriben resultados; los lectores comprueban contratos y coherencia; `HuellasArchivos` calcula SHA-256. |
| **Vistas** | `GraficaSIR` genera el PNG; `VentanaSimulacion` aporta controles; `PuenteNetLogo` adapta las llamadas a NetLogo. |
| **Módulos NetLogo** | Separan lectura, control de reproducción, personas y curvas; no ejecutan las reglas de contagio o recuperación. |

**Flujo general:** opciones → modelo Java → CSV, PNG y parámetros → validación → reproducción en NetLogo.

La separación de modelo, controlador y vistas permite describir la organización como **MVC**. El código también utiliza clases de objetos e interfaces; eso no demuestra por sí solo la aplicación completa de SOLID.

`netlogo/` es la fuente del modelo. El adaptador reúne sus `__includes` en una copia temporal para cargar `InterfaceComponent` y la elimina después; no mantiene una segunda versión manual del modelo.

---

## 6. Funcionamiento y resultados

### Reglas de cada paso

El modelo guarda una copia de los estados al iniciar el paso. Cada individuo que estaba infectado selecciona el número configurado de contactos de toda la población, con reemplazo y pudiendo elegirse a sí mismo. Si el contacto era susceptible, intenta contagiarlo con probabilidad beta. Después, el infectado original intenta recuperarse con probabilidad gamma.

Un recién infectado empieza a actuar y puede recuperarse desde el paso siguiente. Las transiciones son **S → I → R** y los recuperados no vuelven a ser susceptibles. La semilla controla la selección inicial y los sorteos posteriores.

La terminal presenta `contactos * beta / gamma` como **R0 nominal**. Es un cociente orientativo de los parámetros, no una estimación calculada a partir de la trayectoria. Si gamma es cero, se informa de un valor sin límite o indefinido, según el numerador. Las decisiones del modelo usan `double` sin redondeo previo; la presentación del cociente utiliza `BigDecimal` y no altera la simulación.

### Archivos generados

Para una ruta nueva `ejemplo.csv`, Java produce:

| Archivo generado | Contenido |
|:--|:--|
| `ejemplo.csv` | Conteos agregados por instante. |
| `ejemplo_individuos.csv` | Estado real de cada persona en cada instante. |
| `ejemplo.png` | Gráfica Java de la serie completa. |
| `ejemplo.properties` | Parámetros, semilla, tiempo medido del modelo y huellas SHA-256 de ambos CSV. |

Estos nombres ilustran salidas; no son enlaces a archivos incluidos. Los CSV usan UTF-8 y comienzan en t=0. El agregado utiliza este formato:

```csv
tiempo,susceptibles,infectados,recuperados
0,95,5,0
1,93,7,0
```

El detalle individual tiene el encabezado `tiempo,id,estado`. Sus estados válidos son `SUSCEPTIBLE`, `INFECTADO` y `RECUPERADO`; sus IDs van de 0 a N−1, ordenados dentro de cada instante. Los conteos individuales deben coincidir con el agregado. Con N=100 y 100 pasos se escriben **10100 registros individuales más el encabezado**.

El detalle se escribe progresivamente y se lee con memoria proporcional a N, sin conservar todo el historial individual en memoria. El controlador reserva los nombres con archivos `.lock`, prepara temporales y publica el CSV agregado al final. Rechaza salidas existentes y retira sus propios archivos ante un fallo ordinario. Esa secuencia no constituye una transacción atómica de cuatro archivos frente a cortes de energía.

Las huellas permiten detectar modificaciones o mezclas de las nuevas salidas; no certifican autoría. En archivos antiguos sin huellas, la coherencia entre estados y conteos tampoco demuestra la procedencia de los datos.

### Ejemplos incluidos

Actualmente se incluyen cuatro ejemplos con CSV agregado, PNG y parámetros. **No incluyen su compañero individual**, por lo que el visor puede mostrar sus curvas pero no representar personas a partir de ellos.

| CSV incluido | Cambio respecto al escenario base | S/I/R en t=100 | Pico de I |
|:--|:--|:--|:--|
| [resultados_java.csv](netlogo/datos/resultados_java.csv) | Base: N=100, I0=5, beta=0.30, gamma=0.10, contactos=1, semilla=42. | 4 / 0 / 96 | 49 en t=20 |
| [otra_semilla.csv](netlogo/datos/otra_semilla.csv) | Semilla=7. | 9 / 0 / 91 | 35 en t=13 |
| [menor_contagio.csv](netlogo/datos/menor_contagio.csv) | Beta=0.10. | 80 / 0 / 20 | 8 en t=11 |
| [mayor_recuperacion.csv](netlogo/datos/mayor_recuperacion.csv) | Gamma=0.30. | 85 / 0 / 15 | 6 en t=1 |

Estos valores se obtuvieron **leyendo los CSV presentes durante la revisión documental**, sin volver a ejecutar la simulación. Las pruebas del código también contienen regresiones esperadas para las semillas 42 y 7; su presencia no equivale a haberlas ejecutado en esta revisión.

### Interpretar las gráficas

En las curvas de cada escenario y en las personas, **verde representa S**, el tono oscuro representa I y el gris verdoso representa R. El eje horizontal mide pasos y el vertical cuenta personas. El pico de I indica el máximo de infectados simultáneos; R final incluye a quienes ya pasaron por la infección.

Las tres gráficas de comparación muestran A y B para una misma variable. Si las poblaciones difieren, se comparan **conteos absolutos**, no porcentajes. Si los horizontes difieren, cada escenario conserva su último estado individual real y sus curvas no añaden puntos más allá de sus datos. Un CSV sin detalle mantiene sus curvas y muestra que los estados individuales no están disponibles.

Una trayectoria permite describir ese escenario y esa semilla. **Una sola corrida no demuestra una tendencia estadística general** ni valida un modelo epidemiológico real.

---

## 7. Información adicional

### Pruebas existentes

Desde `04APE_Grupal/`, estos comandos corresponden a la configuración actual:

```bash
./mvnw test
./mvnw clean verify
```

`test` ejecuta con Surefire las pruebas del modelo, parámetros, opciones, archivos y detalle individual. `verify` añade las pruebas del JAR mediante Failsafe, incluidas ejecuciones de terminal en otras JVM. Los informes se generan en `target/surefire-reports/` y `target/failsafe-reports/`.

Los perfiles opcionales añaden integración real con una instalación externa de NetLogo:

```bash
# Integración NetLogo sin pantalla
./mvnw -Pnetlogo -Dnetlogo.home="/ruta/real/NetLogo 7.0.4" verify

# Ventana Swing integrada: necesita una sesión gráfica
./mvnw -Pgui -Dnetlogo.home="/ruta/real/NetLogo 7.0.4" verify
```

Reemplaza las rutas de ejemplo. Ejecuta los perfiles **por separado**, porque utilizan configuraciones gráficas distintas. Sin un perfil, sus pruebas externas no se ejecutan. Si falta la instalación o la pantalla requerida, las pruebas correspondientes utilizan condiciones de omisión; una prueba omitida no cuenta como aprobada.

El script incluido ofrece los mismos accesos desde una terminal Bash:

```bash
bash pruebas/verificar.sh
bash pruebas/verificar.sh "/ruta/real/NetLogo 7.0.4"
bash pruebas/verificar.sh "/ruta/real/NetLogo 7.0.4" --interfaz
```

En PowerShell, sustituye `./mvnw` por `.\mvnw.cmd` en los comandos Maven. **En esta revisión solo se inspeccionaron fuentes, configuración y datos, y se comprobaron las referencias documentales. No se ejecutaron Maven, el JAR ni el visor**, por lo que no se declara un total de pruebas aprobadas ni se certifica aquí su funcionamiento.

### Límites y solución de problemas

| Situación | Qué revisar |
|:--|:--|
| No aparece `target/sir.jar` | Construye desde la carpeta de esta práctica con `clean verify` y revisa si Maven informa errores. |
| NetLogo no se encuentra | Indica `--netlogo` con la carpeta que contiene `lib/app/netlogo-7.0.4.jar`; revisa la versión instalada. |
| No hay pantalla gráfica | Usa `--sin-netlogo` para generar los archivos y el PNG. |
| Ya existe alguna salida | Escoge otro nombre; el controlador protege el CSV, el detalle, el PNG y los parámetros existentes. |
| Se seleccionó el CSV individual | Abre el agregado del mismo nombre base. |
| Las curvas aparecen sin personas | Comprueba si existe el compañero `*_individuos.csv`; no se reconstruyen identidades desde conteos. |
| Un CSV se rechaza | Revisa encabezado, codificación, tiempos consecutivos, población, estados, transiciones y coincidencia de huellas. |
| La ventana tarda en abrirse | La creación de widgets y compilación de NetLogo se realizan en el hilo gráfico y pueden producir una espera. |

El lector agregado admite archivos de hasta **1 MiB y 2001 registros**. El individual admite hasta **512 MiB y 20010000 registros** como límite estructural; ambos limitan las líneas a 256 caracteres. Estos límites no garantizan una vista legible de 10000 personas ni eliminan el coste de validar y representar poblaciones grandes.

Mantén los archivos estables durante la reproducción: no existe vigilancia continua de cambios externos. Un cierre forzado puede dejar reservas o salidas incompletas. No borres archivos `.lock` de una exportación activa; ante una ejecución interrumpida, revisa sus salidas y utiliza otro nombre.

### Alcance frente a la guía local

El PDF de la semana 4 plantea implementar un modelo común en NetLogo, Python/SimPy y Java, además de importar resultados de Python y Java en NetLogo. **Esta carpeta contiene el generador Java y el visor NetLogo; no incluye una implementación Python ni un generador SIR independiente en NetLogo.** La comparación A/B de dos ejecuciones Java no sustituye la comparación entre herramientas solicitada en esa guía. Este README documenta lo existente, sin afirmar que cubra toda la entrega académica.

### Declaración de uso de IA

El README anterior declaraba asistencia de ChatGPT/Codex en el desarrollo del código, Maven, pruebas e instrucciones. Se conserva esa declaración como antecedente del proyecto, sin deducir de ella autoría, porcentajes ni responsabilidades individuales.

En esta revisión, **Codex asistió en la inspección del repositorio y la reorganización y redacción de la documentación**. La revisión documental no modifica los algoritmos ni demuestra por sí misma qué partes del código fueron generadas con IA. Corresponde al equipo revisar el contenido y declarar su asistencia de forma veraz según las indicaciones del docente.

---

**Proyecto académico de simulación SIR — Computación, UNL.**
