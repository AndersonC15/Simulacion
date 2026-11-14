# APE 07 — Estimación de π con Monte Carlo en Python y Java

En esta práctica de **Simulación, quinto ciclo de Computación**, implementé el mismo experimento Monte Carlo en Python y Java. Genero puntos en un cuadrado, cuento los que pertenecen a un círculo inscrito y comparo la estimación de π, el error absoluto y el tiempo para cuatro tamaños de muestra.

Organicé ambos programas con **MVC** y utilicé **Strategy** para separar la fuente de números del estimador. La explicación del modelo, los componentes y la demostración está en [GUIA_EXPOSICION.md](GUIA_EXPOSICION.md).

## Informe para entregar

El informe académico conservado está en [APE07-CoelloAnderson-U2-Simulacion.pdf](APE07-CoelloAnderson-U2-Simulacion.pdf). Incluye el modelo matemático, la metodología, los resultados, las gráficas, ocho preguntas de análisis, cinco preguntas de control y las conclusiones de la ejecución original.

La carpeta actual conserva el código, las pruebas, los resultados y el PDF. Retiré la guía original, los documentos de análisis, la versión Markdown del informe, el video y los scripts que generaban el informe y el video. El PDF todavía contiene referencias a ese material. Los scripts `entregar.sh` y `auditar_entrega.py` también dependen de archivos retirados; su situación se detalla más adelante.

## Requisitos

- Linux y Bash para los scripts incluidos.
- **Python 3.11 o superior**, con `venv` y `pip`. El entorno local utiliza Python 3.14.4.
- **JDK 21 o superior**, con `java` y `javac`, y **Maven**. El proyecto Java compila con `release=21`.
- Conexión para descargar dependencias durante la preparación cuando no estén disponibles localmente.

Java ejecuta el experimento con clases del JDK; JUnit es una dependencia de pruebas. Python utiliza NumPy y Pandas para la comparación y el análisis, y Matplotlib para las gráficas. Los programas de consola y las gráficas no necesitan abrir una ventana.

## Preparar y ejecutar

Desde esta carpeta, `02Unidad/07APE`:

```bash
bash scripts/preparar.sh
bash scripts/ejecutar.sh
bash scripts/verificar.sh
```

`preparar.sh` comprueba las herramientas, crea `.venv`, instala las dependencias y el paquete Python en modo editable, y compila y prueba Java con Maven. No descarga ni configura un JDK.

`ejecutar.sh` empaqueta Java, ejecuta los dos programas con la configuración predeterminada y reconstruye la comparación y las gráficas. `verificar.sh` ejecuta las pruebas de ambos lenguajes y vuelve a comparar los resultados principales existentes.

Estos comandos **reemplazan archivos con los mismos nombres**. Al volver a ejecutar el experimento cambian las mediciones de tiempo y el PDF conservado no se actualiza automáticamente. Para exponer manteniendo los datos originales, utiliza las carpetas de demostración de la siguiente sección.

Los scripts Bash resuelven la raíz desde su propia ubicación. Desde `02Unidad` también se pueden invocar con `bash 07APE/scripts/preparar.sh`, por ejemplo. Los comandos individuales siguientes utilizan rutas relativas y deben ejecutarse desde `07APE`.

## Ejecutar Python por separado

```bash
.venv/bin/python -m ape07 \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_python
```

No es necesario activar el entorno. También se instala el comando `.venv/bin/ape07`. La ayuda está disponible con `.venv/bin/python -m ape07 --help`.

El paquete se configura en [python/pyproject.toml](python/pyproject.toml). [python/requirements.txt](python/requirements.txt) declara rangos de dependencias y [python/requirements-lock.txt](python/requirements-lock.txt) conserva las versiones exactas del entorno original; la preparación utiliza el primero. ReportLab permanece de la generación anterior del PDF e imageio-ffmpeg se utiliza en la auditoría antigua del video; no participan en el estimador.

## Ejecutar Java por separado

Si todavía no está construido el JAR:

```bash
mvn -B -ntp -f java/pom.xml verify
```

Para ejecutar el mismo experimento:

```bash
java -jar java/target/ape07.jar \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_java
```

El JAR funciona sin Python. En un IDE, abre `java/pom.xml` como proyecto Maven, selecciona un JDK compatible con release 21 y ejecuta `ec.edu.simulacion.ape07.App`. La ayuda se obtiene con `java -jar java/target/ape07.jar --help`.

## Opciones compartidas

| Opción | Valor predeterminado | Uso |
|---|---|---|
| `--semilla` | `123457` | Estado inicial del LCG |
| `--tamanos` | `1000,10000,100000,1000000` | Cantidades de puntos, separadas por comas |
| `--repeticiones` | `5` | Mediciones de tiempo por tamaño |
| `--salida` | `resultados/python` o `resultados/java` | Carpeta de salida |

La semilla debe ser un entero entre 1 y 2147483646. Los tamaños deben estar ordenados, no repetirse y pertenecer al intervalo de 1 a 1 000 000. Se permiten entre 1 y 30 repeticiones. Los límites de tamaño y repeticiones son decisiones operativas de esta implementación.

Para comprobar una entrada inválida:

```bash
.venv/bin/python -m ape07 --tamanos 0
```

El programa explica el error y termina con código 2. Ambos ejecutables mantienen fijos los parámetros del LCG; la CLI permite cambiar su semilla.

## Modelo matemático y parámetros

El cuadrado tiene lado 2 y área 4. El círculo inscrito tiene radio 1 y área π. Bajo muestreo uniforme, la proporción de puntos interiores aproxima la razón de áreas π/4:

```text
S(k+1) = 16807 * S(k) mod 2147483647
U = S / 2147483647
x = 2*U1 - 1
y = 2*U2 - 1
interior si x*x + y*y <= 1
pi_estimado = 4 * interiores / N
error_absoluto = abs(pi_estimado - pi_referencia)
```

Utilicé el LCG MINSTD con `a=16807`, `c=0`, `m=2147483647` y semilla `123457`. La elección del generador y la semilla está documentada en el informe como una decisión del experimento.

Cada punto utiliza dos valores consecutivos: un millón de puntos requiere dos millones de estados. La fuente admite valores en `[0,1)` y las coordenadas corresponden al cuadrado `[-1,1)²`; el LCG con semilla válida produce valores estrictamente entre cero y uno. La frontera del círculo se incluye mediante `<=`.

Cada tamaño y cada repetición reinician la semilla. Por eso se evalúan prefijos de la misma secuencia y se repite el mismo problema para medir rendimiento. Hay tres calentamientos de hasta 10 000 puntos y cinco mediciones por tamaño de forma predeterminada.

El intervalo medido comprende la construcción inmediata del generador y el estimador que genera y clasifica los puntos. Se utilizan `perf_counter` y `System.nanoTime`. Se excluyen compilación, calentamientos, consola, archivos y gráficas; se informa la mediana y se conservan todas las duraciones.

## Comparación y gráficas

Después de ejecutar ambos programas en sus carpetas principales:

```bash
.venv/bin/python scripts/entrega.py
```

Este script utiliza rutas fijas: lee `resultados/python` y `resultados/java`, y escribe en `resultados/comparacion`. Verifica los resultados, construye las tablas y genera dos gráficas. No genera el informe PDF ni un video.

Para comparar las carpetas de demostración anteriores sin reemplazar la comparación principal:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from ape07.comparacion import comparar

tabla = comparar(
    Path("resultados/demo_python"),
    Path("resultados/demo_java"),
    Path("resultados/demo_comparacion"),
)
print(tabla.to_string(index=False))
PY
```

La función `comparar` audita las secuencias completas y escribe `tabla_guia.csv` y `verificacion.json`. Comprueba parámetros, longitud, SHA-256, recurrencia de cada estado, coordenadas iniciales, conteos reconstruidos, estimaciones, errores y coherencia de los tiempos. Rechaza una secuencia alterada incluso si se actualiza su hash.

## Resultados conservados

| N | Interiores | π estimado | Error absoluto | Python (s) | Java (s) |
|---:|---:|---:|---:|---:|---:|
| 1 000 | 765 | 3.060000 | 0.08159265 | 0.00036424 | 0.00007351 |
| 10 000 | 7 850 | 3.140000 | 0.00159265 | 0.00402105 | 0.00063327 |
| 100 000 | 78 608 | 3.144320 | 0.00272735 | 0.03984748 | 0.00088667 |
| 1 000 000 | 785 969 | 3.143876 | 0.00228335 | 0.39313000 | 0.00649209 |

Fuente: [tabla_guia.csv](resultados/comparacion/tabla_guia.csv). Los tiempos son medianas de las cinco mediciones originales por tamaño. La verificación de los datos conservados confirma **dos millones de estados y un millón de puntos coincidentes** entre lenguajes.

La mejor aproximación ocurrió con **10 000 puntos**. Más puntos no garantizan menor error en cada prefijo. Bajo muestreo uniforme e independiente, la desviación estándar ideal escala como `1/√N`; la referencia de la gráfica ilustra esa forma, sin ser una cota ni demostrar independencia del LCG.

Java registró menores medianas en estos datos. La conclusión corresponde a estas implementaciones y su entorno; los tiempos pueden cambiar al repetirlas. El estimador Python utiliza un bucle ordinario; el procesamiento con NumPy se realiza después, en el análisis de los archivos.

## Archivos de salida

| Archivo | Contenido |
|---|---|
| `resultados/{python,java}/resumen.csv` | N, interiores, π, error, mediana, mínimo y repeticiones |
| `.../tiempos.csv` | Una duración por tamaño y repetición |
| `.../primeros20.csv` | Hasta veinte puntos iniciales: estados, coordenadas y clasificación |
| `.../secuencia.bin` | Los 2N estados del mayor tamaño, en enteros de cuatro bytes big-endian |
| `.../entorno.json` | Parámetros, versión, protocolo de medición y huella de la secuencia |
| `resultados/comparacion/tabla_guia.csv` | Tabla consolidada de ambos lenguajes |
| `.../primeros20_comparados.csv` | Comparación legible de las coordenadas iniciales |
| `.../convergencia.csv` | Estimaciones para prefijos intermedios |
| `.../puntos_convergencia.png` | Hasta 5 000 puntos y evolución del estimador |
| `.../error_tiempos.png` | Error absoluto y medianas Python/Java |
| `.../verificacion.json` | Cantidades comparadas, parámetros y huella |
| `resultados/revision/` | Registros de compilación, ejecución y verificaciones anteriores |

Cada binario principal ocupa 8 000 000 de bytes. Los binarios se conservan localmente y están excluidos de Git; se recrean al ejecutar los programas. El comparador los necesita para verificar los datos completos.

Las carpetas `resultados/demo_python`, `demo_java` y `demo_comparacion` contienen ejecuciones de demostración. Cambiar parámetros requiere utilizar carpetas coherentes en ambos lenguajes. Repetir un comando con la misma carpeta reemplaza sus archivos.

## Arquitectura y diseño

```text
07APE/
├── APE07-CoelloAnderson-U2-Simulacion.pdf
├── README.md
├── GUIA_EXPOSICION.md
├── python/
│   ├── pyproject.toml, requirements.txt, requirements-lock.txt
│   ├── src/ape07/
│   │   ├── modelo.py          # LCG, Strategy, estimador y mediciones
│   │   ├── vista.py           # Consola y exportación
│   │   ├── controlador.py     # Coordinación del experimento
│   │   ├── comparacion.py     # Verificación cruzada de archivos
│   │   ├── __main__.py        # Argumentos y composición
│   │   └── __init__.py
│   └── tests/test_qa.py
├── java/
│   ├── pom.xml
│   └── src/
│       ├── main/java/ec/edu/simulacion/ape07/
│       │   ├── modelo/, vista/, controlador/
│       │   └── App.java
│       └── test/java/ec/edu/simulacion/ape07/ModeloTest.java
├── scripts/
└── resultados/
```

**MVC:** el modelo calcula y valida; la vista presenta y exporta; el controlador coordina. Los puntos de entrada construyen las dependencias. La comparación entre lenguajes y las gráficas se ejecutan como herramientas adicionales.

**Strategy:** `EstimadorPi` recibe el contrato `FuenteUniforme`. En el experimento se utiliza `GeneradorLCG` y en las pruebas se suministran fuentes controladas. Esto permite comprobar o sustituir la generación que consume el estimador sin cambiar la geometría. El medidor construye actualmente el LCG; seleccionar otra estrategia desde la CLI requeriría modificar esa construcción.

POO se aplica mediante clases, encapsulación del estado y objetos inmutables para parámetros y resultados: `dataclass(frozen=True)` en Python y `record` en Java. La separación de tareas y el contrato pequeño de generación permiten justificar responsabilidad única e inversión de dependencias en el estimador.

## Scripts incluidos

| Script | Función y estado actual |
|---|---|
| `preparar.sh` | Prepara Python y compila y prueba Java. |
| `ejecutar.sh` | Ejecuta ambos experimentos y reconstruye comparación y gráficas. Su mensaje final conserva una referencia a generadores documentales retirados. |
| `verificar.sh` | Ejecuta JUnit y unittest, guarda registros y compara los resultados principales existentes. |
| `entrega.py` | Verifica datos principales y genera tablas y PNG. |
| `entregar.sh` | Conserva el flujo completo antiguo. Ejecuta etapas que reemplazan resultados y luego falla al llamar a los generadores del informe y video retirados. No lo utilizo como comando completo en esta versión. |
| `auditar_entrega.py` | Conserva la auditoría documental antigua. Necesita la guía, los análisis y el video retirados; no puede completarse con la carpeta actual. |

## Verificación y errores frecuentes

Para ejecutar las pruebas sin reconstruir tablas ni gráficas:

```bash
mvn -B -ntp -f java/pom.xml verify
.venv/bin/python -m unittest discover -s python/tests -v
```

La suite Python contiene **diez campañas** con subcasos e integración real con Java. Comprueba geometría, estados conocidos, reproducibilidad, entradas inválidas, rutas con espacios, secuencias manipuladas, tiempos incoherentes y carga de un millón de puntos. El JAR es obligatorio: su ausencia hace fallar la suite.

Java añade **diez pruebas JUnit** del modelo. En la revisión actual ambas suites aprobaron, y la comparación de los resultados principales confirmó la igualdad completa de los estados y los conteos.

- `No module named ape07`: ejecuta la preparación y utiliza `.venv/bin/python`.
- Falta el JAR: ejecuta `mvn -B -ntp -f java/pom.xml verify`.
- `release version 21 not supported`: configura Maven con un JDK compatible y revisa `mvn -version`.
- Falta `secuencia.bin` o no coinciden parámetros: ejecuta ambos programas con configuraciones equivalentes en las carpetas correspondientes.
- Error de archivo ausente al usar `entregar.sh` o `auditar_entrega.py`: esos scripts dependen de material retirado; utiliza el flujo de ejecución y pruebas documentado arriba.

Los registros antiguos de auditoría describen el estado anterior de la entrega. No certifican que sigan presentes los archivos retirados ni sustituyen una verificación actual.
