   PE 07 — Estimación de π mediante Monte Carlo

Práctica de **Simulación, quinto ciclo de Computación**. Implementé el mismo experimento en **Python y Java** para aproximar π mediante Monte Carlo: generar puntos en un cuadrado y contar los que caen dentro del círculo inscrito. Comparo las estimaciones, el error absoluto y los tiempos para 1 000, 10 000, 100 000 y 1 000 000 de puntos.

Organicé ambos programas con **MVC** y utilicé **Strategy** para separar la fuente de números pseudoaleatorios del estimador.


## Requisitos

- Linux y Bash para los scripts incluidos.
- **Python 3.11 o superior**, con `venv` y `pip`.
- **JDK 21 o superior**, con `java` y `javac`, y **Maven**. El proyecto compila con `release=21`.
- Conexión para descargar dependencias durante la preparación, si no están disponibles localmente.

El experimento Java utiliza clases del JDK; JUnit se usa solamente en las pruebas. Python utiliza NumPy y Pandas para verificar y analizar los archivos, y Matplotlib para las gráficas. No se necesita abrir una ventana gráfica.

## Preparar y ejecutar todo

Desde esta carpeta, `02Unidad/07APE`:

```bash
bash scripts/preparar.sh
bash scripts/ejecutar.sh
```

`preparar.sh` comprueba las herramientas, crea `.venv` en la raíz de `07APE`, instala las dependencias y el paquete Python en modo editable, y compila y prueba Java mediante `java/pom.xml`. `ejecutar.sh` recompila Java, ejecuta ambos programas con los valores predeterminados y genera las tablas comparativas y las gráficas.

Después de ejecutar los experimentos, compruebo las pruebas y los resultados:

```bash
bash scripts/verificar.sh
```

En una copia recién descargada debo seguir el orden **preparar → ejecutar → verificar**: los binarios `secuencia.bin` están excluidos de Git y se reconstruyen al ejecutar ambos programas. La verificación los necesita para comparar los resultados principales.

Los comandos reemplazan las salidas con los mismos nombres. Los scripts resuelven la raíz desde su propia ubicación y también pueden invocarse desde otra carpeta. `.venv` y `java/target` se recrean al preparar el proyecto en otra computadora.

## Ejecutar Python por separado

Para demostrar el programa sin reemplazar los datos principales del informe:

```bash
.venv/bin/python -m ape07 \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_python
```

También puedo activar el entorno como en las prácticas anteriores:

```bash
source .venv/bin/activate
python -m ape07 --salida resultados/demo_python
deactivate
```

Se instala además el comando `.venv/bin/ape07`. Para consultar las opciones:

```bash
.venv/bin/python -m ape07 --help
```

Instalación manual de Python, equivalente a la parte Python de la preparación:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r python/requirements.txt
.venv/bin/python -m pip install -e ./python
```

[python/requirements.txt](python/requirements.txt) declara NumPy, Pandas y Matplotlib. [python/requirements-lock.txt](python/requirements-lock.txt) registra las versiones exactas de esas bibliotecas y sus dependencias en el entorno verificado con Python 3.14.4. Para reproducir esas versiones, sustituyo el primer archivo por el segundo al instalar las dependencias. En otros intérpretes, `requirements.txt` permite resolver versiones compatibles.

## Ejecutar Java por separado

Después de la preparación:

```bash
java -jar java/target/ape07.jar \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_java
```

El JAR funciona sin Python. La ayuda está disponible con `java -jar java/target/ape07.jar --help`. Desde un IDE, abro `java/pom.xml` como proyecto Maven y ejecuto `ec.edu.simulacion.ape07.App` con un JDK compatible.

Para compilar y probar únicamente Java:

```bash
mvn -B -ntp -f java/pom.xml verify
```

## Opciones compartidas

| Opción | Valor predeterminado | Uso |
|---|---|---|
| `--semilla` | `123457` | Estado inicial del generador |
| `--tamanos` | `1000,10000,100000,1000000` | Cantidades de puntos, ordenadas y sin repetir |
| `--repeticiones` | `5` | Mediciones de tiempo por tamaño |
| `--salida` | `resultados/python` o `resultados/java` | Carpeta donde se guardan los archivos |

La semilla admite enteros de **1 a 2147483646**. Cada tamaño debe estar entre 1 y 1 000 000; las repeticiones, entre 1 y 30. Los límites de puntos y repeticiones son decisiones operativas del programa. Las rutas de los comandos individuales son relativas a la carpeta desde la que se ejecutan.

## Parámetros y decisiones del experimento

Utilicé el generador congruencial lineal multiplicativo **MINSTD**, con `a=16807`, `c=0`, `m=2147483647` y semilla inicial `123457`:

```text
S(k+1) = (a * S(k) + c) mod m
S(k+1) = (16807 * S(k)) mod 2147483647
U = S / 2147483647
```

Estos parámetros son la configuración elegida para el proyecto; la guía 07 no impone sus valores. Los ejecutables permiten cambiar la semilla, los tamaños, las repeticiones y la salida, y mantienen fijos `a`, `c` y `m`.

Cada punto consume dos valores consecutivos y los transforma en coordenadas del cuadrado `[-1,1)²`, de lado 2:

```text
x = 2*U1 - 1
y = 2*U2 - 1
Dentro del círculo si: x² + y² <= 1
```

El círculo tiene radio 1. Bajo muestreo uniforme, la proporción de puntos interiores aproxima la relación entre las áreas:

```text
Área del cuadrado = lado² = 2² = 4
Área del círculo = π * radio² = π * 1² = π
Proporción interior = Nc / N
Porcentaje interior = 100 * Nc / N
π estimado = 4 * Nc / N
Error absoluto = |π estimado - π de referencia|
```

`N` es el total de puntos y `Nc` la cantidad dentro del círculo. La referencia del error es `math.pi` en Python y `Math.PI` en Java. Un millón de puntos requiere dos millones de estados del generador.

Cada tamaño y cada repetición reinician la semilla. Por eso los conteos se repiten y los tamaños utilizan prefijos de la misma secuencia. Antes de medir se realizan tres calentamientos de hasta 10 000 puntos. Se mide la generación y clasificación mediante `perf_counter` y `System.nanoTime`; compilación, calentamientos, consola, archivos y gráficas quedan fuera del intervalo medido. Se conserva cada duración y se presenta su mediana.

El cálculo tiene complejidad **O(N)** porque procesa una vez cada punto. Más puntos aumentan el trabajo y no garantizan que el error absoluto disminuya en cada ejecución. La relación ideal `1/√N` describe la escala de la desviación estándar bajo muestreo uniforme e independiente; la curva del informe es una referencia visual y no una cota garantizada para el LCG.

## Resultados y comparación

| N | Interiores | π estimado | Error absoluto | Python (s) | Java (s) |
|---:|---:|---:|---:|---:|---:|
| 1 000 | 765 | 3.060000 | 0.08159265 | 0.00069456 | 0.00014955 |
| 10 000 | 7 850 | 3.140000 | 0.00159265 | 0.00699646 | 0.00130951 |
| 100 000 | 78 608 | 3.144320 | 0.00272735 | 0.07093225 | 0.00159038 |
| 1 000 000 | 785 969 | 3.143876 | 0.00228335 | 0.70752325 | 0.01375321 |

Fuente: `resultados/python/resumen.csv` y `resultados/java/resumen.csv`. Los tiempos son medianas de cinco mediciones por tamaño. Ambos lenguajes obtuvieron los mismos conteos y estimaciones. En estos resultados, la menor diferencia respecto a π ocurrió con 10 000 puntos y Java registró menores medianas; los tiempos dependen del equipo y de estas implementaciones.

| Archivo | Contenido |
|---|---|
| `resultados/{python,java}/resumen.csv` | Tamaño, interiores, π, error, mediana, mínimo y repeticiones |
| `.../tiempos.csv` | Duración de cada medición |
| `.../primeros20.csv` | Hasta veinte puntos iniciales, con estados, coordenadas y clasificación |
| `.../secuencia.bin` | Los 2N estados del mayor tamaño, como enteros de cuatro bytes big-endian |
| `.../entorno.json` | Parámetros, versión, protocolo de medición y SHA-256 de la secuencia |
| `resultados/comparacion/tabla_guia.csv` | Tabla consolidada Python/Java |
| `.../primeros20_comparados.csv` | Comparación de las coordenadas iniciales |
| `.../convergencia.csv` | Estimaciones para prefijos intermedios |
| `.../puntos_convergencia.png` | Puntos dentro y fuera, y evolución del estimador |
| `.../error_tiempos.png` | Error absoluto y medianas por lenguaje |
| `.../verificacion.json` | Cantidades comparadas, parámetros y huella de la secuencia |
| `resultados/revision/*.log` | Salida de compilación, ejecución y pruebas para revisar lo ocurrido |

Los binarios están excluidos de Git y se recrean al ejecutar ambos programas. El comparador los necesita para verificar la secuencia completa.

La carpeta de resultados está organizada así:

```text
resultados/
├── python/             # Resultados principales de Python
├── java/               # Resultados principales de Java
├── comparacion/        # Tablas, verificación y gráficas principales
├── demo_python/        # Resultados de demostración en Python
├── demo_java/          # Resultados de demostración en Java
├── demo_comparacion/   # Comparación conservada de una demostración
└── revision/           # Registros .log de ejecución y pruebas
```

Los ejemplos con `--salida resultados/demo_python` y `--salida resultados/demo_java` guardan únicamente las salidas de cada lenguaje. `demo_comparacion` conserva una comparación anterior; esos dos comandos no la actualizan.

Después de generar los resultados principales en ambos lenguajes, puedo reconstruir solamente la comparación y las gráficas:

```bash
.venv/bin/python scripts/entrega.py
```

Este script lee exclusivamente `resultados/python` y `resultados/java`, y escribe en `resultados/comparacion`. Verifica todos los estados, su recurrencia, parámetros, coordenadas iniciales, conteos, estimaciones, errores y coherencia de los tiempos. Para la configuración principal compara dos millones de estados y reconstruye el millón de puntos. Los valores se contrastan numéricamente, aunque Python y Java puedan escribirlos con formatos decimales distintos.

## Arquitectura MVC, POO y patrón Strategy

| Capa | Python | Java | Responsabilidad |
|---|---|---|---|
| Modelo | `modelo.py` | paquete `modelo` | Parámetros, LCG, estimación de π y medición de tiempos |
| Vista | `vista.py` | paquete `vista` | Mostrar y guardar los resultados |
| Controlador | `controlador.py` | paquete `controlador` | Coordinar el modelo y la vista |
| Entrada | `__main__.py` | `App.java` | Leer argumentos y construir las dependencias |

En **Strategy**, `EstimadorPi` recibe el contrato `FuenteUniforme`. El experimento usa `GeneradorLCG` y las pruebas inyectan fuentes controladas para comprobar la geometría. Se puede sustituir la fuente que recibe el estimador sin cambiar su fórmula; la CLI actual utiliza siempre MINSTD. `comparacion.py` es la herramienta de verificación entre lenguajes y no forma parte del cálculo cronometrado.

La POO se aplica mediante clases con responsabilidades separadas, el estado del generador y objetos de parámetros y resultados. Python utiliza `dataclass` y `Protocol`; Java utiliza `record` e interfaces. El punto de entrada construye las dependencias y las entrega a las clases que las necesitan. El modelo realiza los cálculos sin escribir archivos ni importar vistas o controladores.

## Estructura del código

```text
07APE/
├── README.md
├── APE07-CoelloAnderson-U2-Simulacion.pdf
├── .gitignore
├── .venv/                         # Entorno local, excluido de Git
├── python/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-lock.txt
│   ├── src/ape07/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── modelo.py
│   │   ├── vista.py
│   │   ├── controlador.py
│   │   └── comparacion.py
│   └── tests/test_qa.py
├── java/
│   ├── pom.xml
│   ├── src/main/java/ec/edu/simulacion/ape07/
│   │   ├── App.java
│   │   ├── modelo/
│   │   ├── vista/
│   │   └── controlador/
│   ├── src/test/java/ec/edu/simulacion/ape07/ModeloTest.java
│   └── target/                    # Compilación local, excluida de Git
├── scripts/
│   ├── preparar.sh
│   ├── ejecutar.sh
│   ├── verificar.sh
│   └── entrega.py
└── resultados/
```

| Script o configuración | Para qué sirve |
|---|---|
| `scripts/preparar.sh` | Crear el entorno, instalar Python y compilar y probar Java |
| `scripts/ejecutar.sh` | Ejecutar los experimentos principales y generar tablas y PNG |
| `scripts/verificar.sh` | Ejecutar las pruebas y verificar los datos principales |
| `scripts/entrega.py` | Comparar archivos y generar tablas y PNG sin repetir los experimentos |
| `python/pyproject.toml` | Configurar la instalación del paquete y el comando `ape07` |
| `python/requirements.txt` | Declarar las dependencias directas |
| `python/requirements-lock.txt` | Registrar versiones exactas del entorno verificado |
| `java/pom.xml` | Configurar Java 21, JUnit, compilación y JAR ejecutable |

## Pruebas y errores frecuentes

La verificación completa, después de preparar y ejecutar los experimentos principales, es:

```bash
bash scripts/verificar.sh
```

Ejecuta Maven/JUnit, las campañas Python y la comparación de los resultados principales existentes. Los registros de las pruebas se guardan en `resultados/revision/java.log` y `resultados/revision/qa.log`.

Para ejecutar solamente las pruebas, después de preparar el entorno:

```bash
mvn -B -ntp -f java/pom.xml verify
.venv/bin/python -m unittest discover -s python/tests -v
```

Java incluye diez pruebas JUnit. Python incluye diez campañas con subcasos e integración real con Java; necesita el JAR construido. Se comprueban estados conocidos, geometría, reproducibilidad, límites, entradas inválidas, rutas con espacios, secuencias manipuladas, tiempos incoherentes y carga de un millón de puntos.

- `No module named ape07`: ejecuto la preparación y uso `.venv/bin/python`, o activo el entorno.
- Error al crear `.venv`: reviso que el componente `venv` esté instalado para mi versión de Python.
- `release version 21 not supported`: configuro Maven con un JDK 21 o superior y compruebo su versión con `mvn -version`.
- Falta `secuencia.bin`: ejecuto ambos experimentos principales antes de comparar.
- Parámetros incompatibles o secuencias distintas: reviso que ambos programas se hayan ejecutado con la misma semilla, tamaños y repeticiones.
- Semilla, tamaños o repeticiones fuera de los límites: la CLI termina con código 2 y muestra el error.

## Enlaces de la práctica

- [Repositorio en GitHub](https://github.com/AndersonC15/Simulacion/tree/main/02Unidad/07APE).
- [Video de demostración en Google Drive](https://drive.google.com/file/d/1Q0uEeraq0bAYnZmH4SY4CKrbCAZI32bb/view?usp=sharing).
