# APE 06 — Validación estadística de números pseudoaleatorios

Práctica de Simulación de quinto ciclo. Dos programas independientes, en **Python y Java**, implementan el LCG y las pruebas de Chi-cuadrado, Kolmogorov–Smirnov y rachas. Se comparan sus secuencias completas y se genera la tabla de estimación de π y tiempos solicitada en la guía.

## Preparar y ejecutar

Requisitos: **Python >= 3.12, JDK 25 y Maven**. El `pom.xml` está configurado con `release=25`. En este equipo Java 25 tenía solamente el entorno de ejecución, mientras el compilador predeterminado era 21. `preparar.sh` resuelve esto instalando un JDK Temurin local en `.tools/jdk-25` si no encuentra un compilador compatible. Verifica el SHA-256 de la descarga y no cambia el Java del sistema. Se requiere conexión durante la preparación; los experimentos posteriores se ejecutan localmente.

Desde esta carpeta (`02Unidad/06APE`):

```bash
./scripts/preparar.sh
./scripts/ejecutar_todo.sh
```

`preparar.sh` crea `python/.venv`, instala las versiones de `requirements.txt`, registra el paquete Python y compila/verifica Java con Maven. `ejecutar_todo.sh` ejecuta los dos programas, mide π para los cuatro tamaños de la guía, compara los resultados y crea el informe. Los scripts resuelven su ubicación y también pueden invocarse desde otra carpeta.

El resultado principal es **`resultados/comparacion/informe.pdf`**. También se genera `informe.md` para editar el contenido académico antes de una entrega institucional. No se inventan datos de portada del estudiante.

## Ejecutar Python por separado

```bash
source python/.venv/bin/activate
ape06 ejecutar
ape06 benchmark
deactivate
```

Sin activar el entorno:

```bash
python/.venv/bin/python -m ape06 ejecutar
python/.venv/bin/python -m ape06 benchmark
```

El proyecto usa estructura `src`, `pyproject.toml`, un punto de entrada instalable y pruebas con pytest. `requirements.txt` fija también las dependencias transitivas del entorno verificado.

## Ejecutar Java por separado

```bash
./scripts/preparar.sh
./scripts/java.sh ejecutar
./scripts/java.sh benchmark
```

El JAR incluye sus dependencias. **Java genera sus CSV, JSON y gráficas PNG con Java2D sin ejecutar Python ni necesitar una pantalla.** Maven conserva la estructura `src/main/java` y `src/test/java`. Con el JDK local también puedes usar `.tools/jdk-25/bin/java -jar java/target/ape06.jar ejecutar` o `JAVA_HOME="$PWD/.tools/jdk-25" mvn -f java/pom.xml verify`. Los scripts admiten `APE_JDK=/ruta/al/jdk` para otra instalación.

## Opciones compartidas

| Opción | Valor predeterminado | Uso |
|---|---|---|
| `--config` | `config/generadores.csv` | Parámetros de los experimentos |
| `--generadores` | `minstd,glibc,zx81` | Selección separada por comas |
| `--salida` | `resultados/python` o `resultados/java` | Carpeta de resultados |
| `--n` | `10000` | Valores de la muestra de validación; mínimo 50 |
| `--alfa` | `0.05` | Significancia de las pruebas |
| `--tamanos` | `1000,10000,100000,1000000` | **Puntos** para estimar π |
| `--repeticiones` | `5` | Mediciones de tiempo por tamaño |

Ejemplo equivalente en ambos lenguajes:

```bash
python/.venv/bin/python -m ape06 ejecutar --generadores minstd --n 10000 --alfa 0.05 --salida resultados/python_individual
./scripts/java.sh ejecutar --generadores minstd --n 10000 --alfa 0.05 --salida resultados/java_individual
```

Los comandos individuales usan rutas relativas al directorio actual. Usa rutas absolutas en `--config` y `--salida` si ejecutas desde otra ubicación.

Para probar otra semilla o combinación de parámetros, añade una fila con nombre distinto al CSV y selecciónala con `--generadores`. Los parámetros son enteros y deben cumplir `0 <= semilla,a,c < m`. Se admite `1 <= m <= 2^53`: es una restricción de representación en `double`, no un teorema sobre el LCG. Java cambia a `BigInteger` si el producto no cabe en `long`. La semilla cero en un LCG multiplicativo se permite y produce la degeneración correspondiente; no se oculta ese resultado.

## Comparación e informe

Después de ejecutar **validación y benchmark en ambos lenguajes**:

```bash
python/.venv/bin/python -m ape06.controlador.entrega
```

También se instala el comando `ape06-comparar`. Acepta `--python`, `--java` y `--salida` para indicar otras carpetas. La comparación rechaza diferencias en parámetros, longitud, recurrencia, estados, normalización, frecuencias, estadísticos, decisiones o resultados de π. Se comparan **todas las filas**, no solamente las primeras diez.

| Archivo | Contenido |
|---|---|
| `resultados/{python,java}/<generador>/secuencia.csv` | Posición, estado entero y valor normalizado de los 10 000 datos |
| `.../frecuencias.csv` | Diez intervalos, Oi, Ei y aportes a Chi-cuadrado |
| `.../ks_ordenados.csv` | Todos los datos ordenados, FDE izquierda/derecha y diferencias |
| `.../analisis.json` | Parámetros, estadística descriptiva, pruebas, críticos, valores p y decisiones |
| `.../histograma.png` | Observadas frente a esperadas |
| `.../acumulada.png` | FDE completa frente a F(u)=u, con distancia D |
| `.../pares.png` | Hasta 4 000 pares consecutivos, como en Semana 5 |
| `resultados/{python,java}/resumen.csv` | Comparación de las tres pruebas y configuraciones |
| `.../benchmark.csv` y `.../tiempos.csv` | π, error, medianas y todas las mediciones individuales |
| `.../entorno_*.json` | Versión del lenguaje, sistema y reloj usado |
| `resultados/comparacion/secuencia_*.csv` | Comparación fila por fila entre lenguajes |
| `.../tabla_guia.csv` | N, π estimado, error y tiempos Python/Java por configuración |
| `.../verificacion.json` | Cantidades comparadas y tolerancias numéricas |
| `.../informe.pdf` e `.../informe.md` | Metodología, resultados reales, gráficas, conclusiones y preguntas de control |
| `.../comparacion_rendimiento.png` | Error de π y comparación de los tiempos medidos |

Los resultados se sobrescriben al repetir un comando con la misma carpeta de salida. Para conservar una ejecución, utiliza otra carpeta. No mezcles ejecuciones con parámetros distintos; usa carpetas nuevas al cambiar los nombres seleccionados, porque los directorios de generadores anteriores se conservan.

## Arquitectura y diseño

```text
06APE/
├── config/generadores.csv
├── python/
│   ├── pyproject.toml, requirements.txt, .venv/
│   ├── src/ape06/
│   │   ├── modelo/          # LCG, Strategy, pruebas y experimentos
│   │   ├── vista/           # Consola, Matplotlib e informe
│   │   ├── controlador/     # Coordinación y entrega
│   │   └── infraestructura/ # CSV, JSON y comparación de archivos
│   └── tests/
├── java/
│   ├── pom.xml
│   └── src/{main,test}/java/ec/edu/simulacion/ape06/
├── scripts/
└── docs/
```

**MVC:** el modelo calcula y valida; las vistas presentan; el controlador coordina. La persistencia está separada. El modelo no importa vistas ni controladores. **Strategy** es el patrón principal: `PruebaEstadistica` define el contrato y Chi-cuadrado, KS y rachas lo implementan. `ServicioSimulacion` recibe la colección de estrategias desde el punto de entrada; no tiene un `if` para cada prueba.

La separación aplica responsabilidad única; el contrato permite añadir otra prueba sin modificar el servicio y evita una interfaz enorme. Las dependencias se proporcionan por constructor. Se usan clases pequeñas, nombres del dominio y objetos de resultados para compartir los datos entre capas. No se necesita Spring, una base de datos ni un servidor para esta práctica.

## Verificación

```bash
./scripts/verificar.sh
```

Ejecuta pytest, las verificaciones Maven/JUnit y la comparación de los resultados existentes. Si todavía no existen resultados, primero ejecuta `ejecutar_todo.sh`. Las pruebas de integración Python invocan el JAR real cuando ya está construido; si falta Java/JAR, pytest informa ese caso como omitido y **no** se debe interpretar como una verificación de equivalencia completa.

Las cinco revisiones solicitadas y sus evidencias se registran en [docs/REVISIONES.md](docs/REVISIONES.md). El alcance, fórmulas, preguntas de control y decisiones no especificadas por la guía están en [docs/BASE_ACADEMICA.md](docs/BASE_ACADEMICA.md).

## Interpretación y decisiones importantes

- Significancia predeterminada: **0.05**; diez intervalos y nueve grados de libertad.
- KS calcula D+ y D−. Su **valor p es asintótico**, con el mismo método en ambos lenguajes. Se distingue del método exacto para N finito; no se atribuyen cifras prefijadas a los experimentos.
- Rachas conserva el orden original, descarta e informa los empates con la mediana y requiere `n1,n2 > 10` para usar la aproximación normal. El umbral bilateral a 0.05 es aproximadamente **1.96**, que las diapositivas redondean a 2.
- La guía pide π sin indicar un algoritmo. Se adopta explícitamente Monte Carlo por cuarto de círculo: `pi = 4*dentro/N`, `error = abs(pi - math.pi)`. N son puntos, por lo que se consumen **2N valores consecutivos del LCG**. Es una decisión adicional para completar la tabla, no una fórmula proporcionada en las diapositivas.
- Cada medición reinicia la semilla. Hay tres calentamientos, cinco repeticiones y se informa la mediana; no se incluyen archivos, gráficas ni impresiones. Estas repeticiones miden rendimiento, no son muestras aleatorias independientes.
- ZX81 no se obliga a fallar. Las conclusiones se basan en lo calculado, aunque una configuración descrita como deficiente supere estas pruebas con una muestra particular.
- No rechazar H0 no prueba aleatoriedad, independencia completa ni idoneidad para cualquier simulación. No se ejecutan poker, serial formal, Diehard ni TestU01; la guía no define esas actividades.

La guía no contiene una rúbrica con puntajes. Este proyecto documenta el cumplimiento y sus evidencias; la calificación corresponde al docente.
