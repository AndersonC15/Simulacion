# APE 04 — SIR con Java y NetLogo

Java calcula la evolucion de la poblacion y guarda los resultados. NetLogo importa esos resultados y los representa. La animacion reproduce filas del CSV: no vuelve a simular ni agrega numeros aleatorios en NetLogo.

## Ejecutar

Se necesita Java 21 y NetLogo 7.0.4 instalado. Para recompilar o ejecutar las pruebas se necesita el JDK, que incluye `javac` y `jar`. No se utiliza Python, Maven, Gradle ni librerias Java descargadas por el proyecto. La extension `csv` viene con NetLogo. La ventana utiliza bibliotecas de esa instalacion.

Desde esta carpeta:

```bash
java -jar sir.jar
```

Se genera una ejecucion nueva y se abre una ventana con graficas reales de NetLogo. Las curvas avanzan automaticamente, inicialmente con una pausa de 100 ms entre filas. La ventana integrada muestra el visualizador, sin las pestanas Informacion y Codigo del editor.

Si no se detecta NetLogo, indica la carpeta que contiene `lib` y `extensions`:

```bash
java -jar sir.jar --netlogo "/opt/NetLogo-7.0.4"
```

Esa ruta es un ejemplo; reemplazala por tu instalacion. Tambien se puede definir `NETLOGO_HOME`. Si NetLogo no se encuentra, los resultados Java ya generados se conservan y aparece un mensaje con la opcion necesaria.

Para generar resultados sin abrir ventanas:

```bash
java -jar sir.jar --sin-netlogo
```

Los botones y las graficas se comprobaron en Linux con Java 21.0.13 y NetLogo 7.0.4. No se ejecutaron en tu version exacta de OpenJDK 21.0.12.1 ni en Windows/macOS. El codigo usa funciones estandar disponibles en Java 21; no se necesita actualizar tu Java solo por este proyecto.

## Modelo y escenarios

El escenario base conserva los parametros de la guia:

| Parametro | Valor |
|---|---:|
| Poblacion N | 100 |
| Susceptibles iniciales S0 | 95 |
| Infectados iniciales I0 | 5 |
| Recuperados iniciales R0 | 0 |
| Probabilidad de contagio por contacto y paso, beta | 0.30 |
| Probabilidad de recuperacion por paso, gamma | 0.10 |
| Pasos | 100 |
| Contactos por infectado y paso | 1 |
| Semilla de ejemplo | 42 |

`R0` tambien suele nombrar el numero reproductivo basico. No hay que confundirlo con el conteo inicial de recuperados: el numero reproductivo nominal es beta/gamma = 3 para un contacto. Se muestra sin redondearlo a un entero. Si gamma=0 no se realiza una division que afecte la simulacion: se indica sin limite, o no definido si el numerador tambien es cero.

En cada paso se toma una copia de los estados. Cada infectado de esa copia elige un contacto al azar de toda la poblacion, con reemplazo; puede elegirse a si mismo. Si el contacto era susceptible, se intenta contagiar con probabilidad beta. Despues se intenta recuperar al infectado original con probabilidad gamma. Un recien contagiado actua desde el siguiente paso. Se registra t=0 y luego cada paso: 101 filas para 100 pasos.

Es una simulacion discreta por individuos, como permite la guia; no es un solucionador de las ecuaciones diferenciales. El algoritmo base y el resultado de la semilla 42 se conservaron. Siempre se verifica `S + I + R = N`.

Ejemplos incluidos en `netlogo/datos/`:

| Archivo | Cambio respecto a base | Proposito |
|---|---|---|
| `resultados_java.csv` | Ninguno | Escenario de la guia, semilla 42 |
| `otra_semilla.csv` | Semilla 7 | Mostrar variabilidad aleatoria con iguales parametros |
| `menor_contagio.csv` | beta=0.10; semilla 42 | Comparar el efecto de reducir contagios |
| `mayor_recuperacion.csv` | gamma=0.30; semilla 42 | Comparar el efecto de aumentar recuperaciones |

Cada ejemplo tiene su PNG y sus parametros reales en un archivo `.properties` del mismo nombre. Las diferencias de una sola trayectoria no prueban una regla estadistica general: para comparar tendencias hay que repetir con varias semillas.

Para cambiar valores desde la terminal:

```bash
java -jar sir.jar --beta 0.10 --gamma 0.10 --semilla 42
java -jar sir.jar --beta 0.30 --gamma 0.30 --semilla 42
java -jar sir.jar --poblacion 200 --infectados 10 --pasos 150
java -jar sir.jar --beta 0.299999 --gamma 0.30 --sin-netlogo
java -jar sir.jar --csv netlogo/datos/mi_escenario.csv --sin-netlogo
java -jar sir.jar --ayuda
```

Usa punto decimal. Aqui no existen lambda, mu o rho: pertenecen al modelo de colas de la practica anterior. Beta y gamma son probabilidades en esta implementacion, por eso 2.9999 y 3 se rechazan; 0.299999 y 0.30 se aceptan conservando su precision.

## Archivos que produce

Sin `--csv`, cada ejecucion utiliza un nombre nuevo `netlogo/datos/ejecucion_....csv`. Junto al CSV se guardan un PNG y un `.properties`, con el mismo nombre base. Un nombre ya existente se rechaza para conservar resultados anteriores. No es necesario indicar un PNG por separado.

El CSV tiene cuatro columnas:

El ejemplo principal se llama `netlogo/datos/resultados_java.csv`, siguiendo el nombre de la guia. En la entrega anterior se llamaba `java_simulado.csv`.

```text
tiempo,susceptibles,infectados,recuperados
0,95,5,0
1,93,7,0
```

El PNG contiene la evolucion completa de esa ejecucion. La ventana NetLogo permite verla progresivamente y guardar otra imagen de su estado visible. El archivo de parametros conserva N, I0, beta, gamma, pasos, contactos, semilla y el tiempo medido del modelo. No se deducen beta, gamma ni la semilla a partir de las curvas.

## Usar la ventana

| Control | Funcion |
|---|---|
| GENERAR ESCENARIO | Valida los campos, ejecuta Java, guarda un nuevo CSV/PNG/parametros y comienza a representarlo |
| ABRIR CSV | Importa otro CSV Java como escenario A; queda pausado en t=0 |
| COMPARAR CON OTRO CSV | Carga otra ejecucion Java como escenario B, sin generar datos en NetLogo |
| QUITAR COMPARACION | Retira B y conserva A |
| PAUSAR / CONTINUAR | Detiene o reanuda la reproduccion; al continuar desde el final vuelve a empezar |
| REINICIAR | Vuelve a t=0 y queda pausado |
| UN PASO | Muestra una fila mas y queda pausado |
| VER COMPLETO | Muestra todas las filas y queda pausado |
| Pausa entre pasos | Ajusta la velocidad de reproduccion, de 20 a 500 ms |
| GUARDAR VISTA PNG | Guarda una imagen nueva de la interfaz NetLogo en `resultados/` |

En la parte superior hay una grafica S/I/R para cada CSV cargado. Debajo hay tres comparaciones: susceptibles, infectados y recuperados. B queda vacio mientras no se cargue una comparacion; no representa una ejecucion con cero personas. Todas las cantidades son personas, no porcentajes.

Si los horizontes son diferentes, cada escenario termina en su ultima fila y no se inventan puntos despues de ella. Los monitores conservan su ultimo valor. Si las poblaciones son diferentes, las curvas comparan conteos absolutos; para comparar el efecto de beta o gamma conviene mantener N, I0, pasos y semilla iguales.

Tambien se puede abrir `netlogo/modelo_sir_netlogo.nlogox` directamente en NetLogo 7.0.4. En ese caso se utiliza el editor normal, que conserva sus pestanas propias, y los botones del modelo: ABRIR CSV, COMPARAR CSV, REINICIAR, ANIMAR/PAUSAR y VER COMPLETO. Para repetir desde el final se pulsa REINICIAR y despues ANIMAR. El formato `.nlogox` corresponde a NetLogo 7.

## Estructura y codigo

| Ubicacion | Responsabilidad |
|---|---|
| `src/sir/model/` | Individuos, estados, parametros y reglas SIR |
| `src/sir/controller/` | Ejecutar cada escenario y coordinar sus archivos de salida |
| `src/sir/view/` | Grafica Java, ventana y adaptador al motor grafico NetLogo |
| `src/sir/io/` | Validacion del CSV y estrategia de exportacion |
| `src/sir/Main.java`, `Opciones.java`, `LanzadorNetLogo.java` | Entrada, opciones y localizacion de NetLogo |
| `netlogo/datos.nls` | Lectura y validacion, sin modelo epidemiologico |
| `netlogo/vista.nls` | Dibuja los puntos importados |
| `netlogo/controlador.nls` | Carga de escenarios y estado de reproduccion |
| `pruebas/` | Casos ejecutables, resultados y hallazgos de QA |

Se conserva MVC, POO y la interfaz `ExportadorResultados` inyectada al controlador. Esta interfaz permite cambiar la estrategia de exportacion sin cambiar las reglas del modelo. Las clases tienen responsabilidades pequenas; no se agregaron patrones solo para aumentar la cantidad de archivos. El adaptador usa la API de NetLogo para integrar sus graficas; reune temporalmente los `.nls` porque el componente integrado no utiliza los editores de archivos incluidos. La copia temporal se retira al terminar la carga.

## Limites y manejo de errores

- N entre 1 y 10000; I0 entre 0 y N.
- Beta y gamma finitas, entre 0 y 1.
- De 0 a 2000 pasos y de 0 a 20 contactos por infectado.
- `N * max(1,pasos) * (contactos+1) <= 10000000`, para mantener razonable el trabajo de esta demostracion.
- CSV de hasta 2001 registros, lineas de hasta 256 caracteres y poblacion constante. El lector Java limita el archivo a 1 MiB.

Los limites son decisiones tecnicas de esta version, no requisitos nuevos atribuidos al docente. Los archivos invalidos se rechazan antes de reemplazar los datos visibles. Se rechazan tiempos con saltos, conteos negativos, poblacion variable, S creciente, R decreciente, mas recuperaciones que infectados previos y contagios cuando ya no hay infectados. Estos controles detectan incompatibilidades con SIR, pero no certifican el origen o la veracidad de cualquier archivo externo.

Un archivo `.lock` reserva el nombre durante una exportacion; no debe borrarse mientras otra ejecucion lo usa. Si se mata el proceso desde el sistema, puede quedar esa reserva o una salida incompleta: usa otro nombre y revisa la ejecucion interrumpida. El programa no puede impedir cortes de energia, cierre forzado, errores del sistema operativo ni fallos fisicos del disco.

## Recompilar y probar

No es necesario recompilar para usar `sir.jar`. Si modificas el codigo:

```bash
mkdir -p build
javac --release 17 -encoding UTF-8 -d build $(find src -name '*.java')
jar --create --file sir.jar --main-class sir.Main -C build .
```

El bytecode se compila con nivel 17 y se ejecuta con Java 21 para NetLogo 7.0.4.

```bash
bash pruebas/verificar.sh "/opt/NetLogo-7.0.4"
bash pruebas/verificar.sh "/opt/NetLogo-7.0.4" --interfaz
```

La segunda opcion abre una ventana y acciona sus controles de forma automatica; requiere una sesion grafica. Las pruebas generan resultados de demostracion con nombres nuevos y actualizan sus informes. El unico script incluido compila y prueba; no se necesita para la ejecucion normal.

Para cerrar el visor se puede usar el cierre normal de la ventana o `Ctrl+Q`. Se detiene el reloj y se libera el motor NetLogo; los archivos de cada ejecucion ya estan guardados.

## Alcance de la entrega y uso de IA

Esta entrega incluye el proyecto ejecutable y sus pruebas. El documento academico, las respuestas de control, el video y la exposicion quedan pendientes por indicacion del grupo. En el documento se deberan seguir las siete etapas de simulacion y el formato indicado en clase, sin indice ni caratula; en anexos iran el prompt, el enlace del video, Git y la declaracion de IA. El video debera durar al menos cinco minutos segun los apuntes proporcionados.

La guia describe SIR, aunque la fila de implementacion de la rubrica menciona M/M/1. Tambien incluye Python y un modelo autonomo en NetLogo en otras secciones. Esta version sigue la asignacion comunicada por el grupo: Java genera los datos y NetLogo los importa. Comparar dos CSV Java no equivale a comparar dos implementaciones independientes en lenguajes distintos.

Se utilizo ChatGPT para apoyar la revision, generar y modificar codigo, disenar pruebas y redactar instrucciones. La ayuda fue sustancial; no se declara un porcentaje menor sin evidencia ni se presenta este codigo como elaborado completamente sin asistencia. El grupo debe estudiar, adaptar y validar lo que entrega, y declarar su uso segun las reglas del docente. Los prompts completos corresponden a los anexos del documento, no a este README.
