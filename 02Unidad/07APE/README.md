# APE 07 — Monte Carlo para estimar π

Práctica de **Simulación, quinto ciclo de Computación**, basada en
`ape_guia simulacion semana 7-signed.pdf`. Implementaciones independientes en
Python y Java, arquitectura **MVC** y patrón **Strategy**.

## Entregables

- [Informe académico PDF](APE07-CoelloAnderson-U2-Simulacion.pdf) y
  [versión editable Markdown](APE07-CoelloAnderson-U2-Simulacion.md).
- [Video de demostración](evidencias/APE07-demostracion.mp4), 76 segundos,
  sin audio, con animación de puntos reales, código, salidas y resultados.
- [Tabla solicitada](resultados/comparacion/tabla_guia.csv),
  [gráficas](resultados/comparacion/) y secuencias completas locales.
- [Diez campañas QA](docs/ANALISIS_03_QA.md), diez pruebas JUnit adicionales,
  [cuatro análisis](docs/ANALISIS_04_ENTREGA.md) y [guion de defensa](docs/DEFENSA.md).

**Aclaración del alcance:** los objetivos y el procedimiento tratan de Monte
Carlo, pero una línea de la rúbrica menciona «modelo M/M/1». El estudiante
comunicó que el docente confirmó que corresponde a **Monte Carlo**. La
implementación de π sigue ese alcance confirmado. La rúbrica asigna cuatro puntos a defensa/demostración, tres
a implementación y tres al documento/evidencias. El software no garantiza la
calificación de la defensa personal.

## Requisitos y ejecución

- Python **3.11 o superior**, `venv` y `pip`.
- **JDK 21 o superior**, con `javac`, y **Maven 3.9 o superior**.
- Internet durante la preparación de dependencias.
- Linux; Times New Roman o DejaVu Serif para el PDF, y DejaVu Sans/Mono para
  el video. La reproducción no necesita Internet ni una ventana gráfica.
- `pdftotext` de Poppler para la auditoría final del PDF.

Desde `07APE`, para preparar y reproducir toda la entrega:

```bash
bash scripts/entregar.sh
```

También se puede ejecutar cada etapa:

```bash
bash scripts/preparar.sh
bash scripts/ejecutar.sh
bash scripts/verificar.sh
.venv/bin/python scripts/generar_informe.py
.venv/bin/python scripts/generar_video.py
.venv/bin/python scripts/auditar_entrega.py
```

Desde `02Unidad`, utiliza `bash 07APE/scripts/entregar.sh`. Los scripts Bash
resuelven su propia ubicación. Los comandos individuales siguientes utilizan
rutas relativas y deben ejecutarse desde `07APE`:

```bash
.venv/bin/python -m ape07
java -jar java/target/ape07.jar
```

No es necesario activar `.venv`. El JAR usa solo el JDK y funciona sin Python.
Python consolida la comparación, el documento, las gráficas y el video después
de las dos ejecuciones independientes.
`python/requirements-lock.txt` registra las versiones exactas del entorno
verificado con Python 3.14.4; `requirements.txt` permite resolver versiones
compatibles en otros intérpretes admitidos.

## Modelo y parámetros

```text
X(n+1) = 16807 * X(n) mod 2147483647
U = X / 2147483647
x = 2*U1 - 1; y = 2*U2 - 1
interior si x*x + y*y <= 1
pi_estimado = 4 * interiores / N
error_absoluto = abs(pi_estimado - pi_referencia)
```

El cuadrado [-1,1)² tiene área 4 y el círculo inscrito de radio 1 tiene área π.
La semilla predeterminada es **123457**. El LCG y la semilla son decisiones
de implementación, no valores impuestos por la guía 07. Cada punto requiere
dos valores consecutivos: un millón de puntos consume dos millones de estados.

Se utilizan los cuatro tamaños solicitados: 1000, 10000, 100000 y 1000000.
Cada tamaño y repetición reinicia la misma semilla, por lo que se comparan
prefijos reproducibles; no son muestras independientes. Hay tres calentamientos
y cinco mediciones por tamaño. Se publica la mediana de generación más
clasificación, excluyendo compilación, calentamientos, archivos y gráficas.

Para probar otra semilla o un caso pequeño sin sustituir la entrega:

```bash
.venv/bin/python -m ape07 --semilla 1 --tamanos 1000,10000 --repeticiones 2 --salida resultados/prueba_python
java -jar java/target/ape07.jar --semilla 1 --tamanos 1000,10000 --repeticiones 2 --salida resultados/prueba_java
```

`--help` muestra la ayuda. Se exige semilla entre 1 y 2147483646, tamaños
ordenados y únicos entre 1 y 1000000 y entre 1 y 30 repeticiones. El máximo
de tamaño y de repeticiones son protecciones operativas documentadas.
La entrada inválida termina con código 2 y explica el error.

## Resultados conservados

| N | π estimado | Error absoluto |
|---:|---:|---:|
| 1000 | 3.060000 | 0.0815926536 |
| 10000 | 3.140000 | 0.0015926536 |
| 100000 | 3.144320 | 0.0027273464 |
| 1000000 | 3.143876 | 0.0022833464 |

Python y Java coincidieron en los **dos millones de estados**, en los puntos
y en los cuatro conteos/estimaciones. En esta ejecución la mejor aproximación
correspondió a **10000 puntos**. No se fuerza la disminución monótona del error.
La escala ideal 1/√N supone muestreo uniforme independiente y no garantiza
mejora en cada prefijo. Los tiempos originales figuran en `tabla_guia.csv`;
regenerarlos cambia las mediciones y puede cambiar sus relaciones.

## Archivos de salida

| Archivo | Contenido |
|---|---|
| `resultados/{python,java}/resumen.csv` | N, interiores, π, error, mediana, mínimo y repeticiones |
| `.../tiempos.csv` | Veinte tiempos individuales por lenguaje |
| `.../primeros20.csv` | Primeros veinte puntos, estados, coordenadas y pertenencia |
| `.../secuencia.bin` | Todos los estados: uint32 big-endian, ocho MB por lenguaje |
| `.../entorno.json` | Parámetros, versiones, reloj, tamaños y SHA-256 |
| `resultados/comparacion/tabla_guia.csv` | Tabla consolidada de cuatro filas |
| `.../primeros20_comparados.csv` | Comparación legible inicial |
| `.../convergencia.csv` | Estimaciones con prefijos intermedios |
| `.../puntos_convergencia.png` | Puntos originales y evolución del estimador |
| `.../error_tiempos.png` | Error absoluto y medianas Python/Java |
| `.../verificacion.json` | Cantidad completa comparada y huella de la secuencia |
| `resultados/revision/` | Salidas reales y registros de JUnit/unittest |

Los binarios completos se conservan localmente y se excluyen de Git por tamaño;
se recrean ejecutando el proyecto. No borres esos archivos si deseas volver a
auditar o regenerar el informe sin repetir los experimentos. El comparador
rechaza una secuencia ausente, truncada o alterada; comprueba la recurrencia
de cada estado incluso si alguien actualiza el SHA-256 de un archivo adulterado.

Repetir comandos con las mismas carpetas sobrescribe sus resultados. No mezcles
una ejecución parcial con archivos de otra configuración. El informe académico
exige los cuatro tamaños, semilla 123457 y cinco mediciones; un cambio de ese
experimento requiere revisar su análisis, no solo reemplazar cifras.

## Arquitectura

```text
07APE/
├── python/src/ape07/
│   ├── modelo.py           parámetros, Strategy, LCG, estimador y mediciones
│   ├── vista.py            consola y archivos
│   ├── controlador.py      coordinación del experimento
│   ├── comparacion.py      auditoría cruzada de resultados
│   └── __main__.py         argumentos y composición
├── python/tests/test_qa.py diez campañas con subcasos adversarios
├── java/src/main/java/ec/edu/simulacion/ape07/
│   ├── modelo/             contratos, clases y records del dominio
│   ├── vista/              presentación y exportación
│   ├── controlador/        coordinación
│   └── App.java            entrada y composición
├── java/src/test/          diez pruebas JUnit
├── scripts/                preparación, ejecución, QA y entrega
├── docs/                   cuatro análisis y defensa
├── resultados/             evidencia numérica reproducible
└── evidencias/             video y metadatos
```

Strategy se aplica mediante `FuenteUniforme`: el estimador recibe una estrategia
de generación. Los casos de prueba inyectan datos controlados, sin cambiar la
geometría. MVC separa cálculo y presentación; los parámetros y resultados usan
objetos inmutables. Se aplican responsabilidad única, contratos pequeños e
inyección por constructor, con nombres del dominio y validaciones explícitas.

## Fuentes, revisiones y límites

- [Análisis 1: requisitos y contradicciones](docs/ANALISIS_01_REQUISITOS.md).
- [Análisis 2: modelo, arquitectura y medición](docs/ANALISIS_02_MODELO.md).
- [Análisis 3: diez campañas adversarias](docs/ANALISIS_03_QA.md).
- [Análisis 4: auditoría final y resultados](docs/ANALISIS_04_ENTREGA.md).
- [Procedencia de recursos](docs/recursos/README.md).

La guía firmada es la fuente de requisitos. Las diapositivas de semana 6 son
la bibliografía indicada por la propia guía; se incluyen como contexto de las
limitaciones de los generadores, sin atribuirles un algoritmo Monte Carlo no
verificado. No se afirman ejecutadas pruebas de uniformidad, sistemas de colas
ni aplicaciones ajenas a esta práctica.
