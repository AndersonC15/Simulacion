# APE02 — Comparación de modelos determinísticos, estocásticos, discretos y continuos

**Asignatura:** Simulación · **Carrera:** Computación · **Ciclo:** Quinto · **Universidad:** Universidad Nacional de Loja (UNL)

**Tecnologías:** Python · NumPy · Matplotlib · pytest para pruebas

## Contenido

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Tecnologías utilizadas](#2-tecnologías-utilizadas)
3. [Preparación del entorno](#3-preparación-del-entorno)
4. [Uso del programa](#4-uso-del-programa)
5. [Estructura del proyecto](#5-estructura-del-proyecto)
6. [Funcionamiento y resultados](#6-funcionamiento-y-resultados)
7. [Información adicional](#7-información-adicional)

---

## 1. Descripción del proyecto

Esta práctica compara cuatro formulaciones del crecimiento poblacional: una solución exponencial, una recurrencia por períodos, una recurrencia con ruido normal y una aproximación numérica mediante Euler. El objetivo es observar cómo cambian las trayectorias al modificar la tasa de crecimiento, el ruido y el paso de integración.

El programa parte de las observaciones `[1000, 1100, 1250, 1400, 1600, 1850, 2100]` de la [guía local de la semana 2](ape_guia%20simulacion%20semana%202-firmado-signed.pdf). Permite ejecutar cada modelo, compararlos, introducir otros datos, modificar parámetros y generar gráficas y tablas CSV.

La implementación actual realiza los cálculos en Python y la visualización en Matplotlib. La guía también describe una conexión con NetLogo mediante pyNetLogo; esa integración no está implementada en esta versión.

Los cuatro nombres no son categorías excluyentes: la recurrencia discreta es determinística y el modelo estocástico también avanza por períodos. La ecuación continua describe una derivada; Euler la aproxima con pasos discretos.

---

## 2. Tecnologías utilizadas

| Herramienta | Uso en esta práctica |
|:--|:--|
| **Python** | Menú de consola, control de experimentos y cálculos. |
| **NumPy 2.5.4** | Generador local de ruido normal mediante `default_rng(semilla)`. |
| **Matplotlib 3.11.2** | Comparación de trayectorias, observaciones de referencia y exportación PNG. |
| **`decimal` y `fractions`** | Aritmética decimal, control de precisión y construcción de mallas. |
| **`csv`, `dataclasses` y `typing.Protocol`** | Exportación, objetos de datos y contrato de las estrategias. |
| **pytest 9.1.1** | Ejecución opcional de las pruebas existentes. |

[requirements.txt](requirements.txt) fija las dependencias de ejecución y sus dependencias transitivas. [requirements-dev.txt](requirements-dev.txt) incorpora ese manifiesto y añade pytest. NumPy 2.5.4 requiere **Python 3.12 o posterior**, según los metadatos del paquete instalado.

Para abrir ventanas se necesita un escritorio y un backend interactivo de Matplotlib. Para generar archivos sin escritorio puede utilizarse el backend `Agg`.

---

## 3. Preparación del entorno

Ejecuta los comandos desde **`02APE/`**, donde están `main.py` y `requirements.txt`. Desde la raíz del repositorio entra primero con `cd 02APE`.

### Linux y macOS

Con Python compatible y soporte para `venv` instalados:

```bash
python3 -m venv .venv-ape02
source .venv-ape02/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Para ejecutarlo otra vez, activa el mismo entorno y utiliza `python main.py`. Sal del entorno con `deactivate`.

### Windows PowerShell

Estos comandos utilizan directamente el intérprete del entorno:

```powershell
py -3.12 -m venv .venv-ape02
.\.venv-ape02\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-ape02\Scripts\python.exe main.py
```

Sustituye `3.12` por una versión compatible instalada. Las instrucciones para Windows y macOS se basan en la estructura del proyecto; no se ejecutaron en esas plataformas durante esta revisión.

---

## 4. Uso del programa

### Menú interactivo

```bash
python main.py
```

| Opción | Acción |
|:--|:--|
| **1–4** | Ejecutar exponencial, discreto, estocástico o Euler, respectivamente. |
| **5** | Comparar los cuatro modelos con la misma configuración. |
| **6** | Consultar observaciones y parámetros actuales. |
| **7** | Modificar parámetros; Enter conserva un valor. |
| **8** | Elegir crecimiento, decrecimiento o población constante. |
| **9** | Introducir un nuevo arreglo y elegir estimación automática o parámetros manuales. |
| **10** | Guardar PNG y CSV del experimento actual y solicitar la ventana gráfica. |
| **a** | Analizar el ruido con 30 realizaciones por nivel. |
| **0** | Salir. |

La terminal muestra el número de puntos y los valores inicial y final de cada serie. La opción de gráficas reutiliza el experimento calculado, incluida su trayectoria aleatoria. Al cambiar datos o parámetros se invalida ese resultado y la siguiente ejecución calcula uno nuevo.

### Ejecución por argumentos

Desde `02APE/`, con el entorno disponible:

```bash
python main.py --help
python main.py --comparar
python main.py --comparar --graficas --mostrar
python main.py --escenario decrecimiento --comparar --graficas
python main.py --analizar-ruido
```

`--graficas` guarda los archivos; `--mostrar` solicita además una ventana si el backend es interactivo. Sin argumentos se abre el menú. Los parámetros numéricos se modifican desde la opción 7 del menú; los argumentos anteriores permiten seleccionar los escenarios predefinidos.

Para generar los tres escenarios sin ventanas y elegir otra carpeta de salida en Linux/macOS:

```bash
MPLBACKEND=Agg python main.py --escenarios --salida "/tmp/APE02 resultados"
```

En PowerShell, el equivalente para generar sin ventanas es:

```powershell
$env:MPLBACKEND = "Agg"
.\.venv-ape02\Scripts\python.exe main.py --escenarios --salida ".\resultados nuevos"
```

### Datos y parámetros

Las siete observaciones representan períodos consecutivos de 0 a 6. El primer dato determina `p0`; el horizonte inicial es seis períodos. No se asignan unidades como días o años.

| Parámetro | Función y configuración inicial del controlador |
|:--|:--|
| `p0` | Población inicial: `1000`. |
| `tasa` | Tasa `r`, estimada a partir de las seis variaciones relativas; aproximadamente `0.1317676524`. |
| `sigma` | Desviación estándar del ruido aditivo por período, estimada de los residuos; aproximadamente `22.3680456170`. |
| `dt` | Paso de Euler y de la malla exponencial: `0.1`. |
| `horizonte` | Tiempo final: `6`. Debe ser entero para comparar los cuatro modelos. |
| `semilla` | Semilla del generador local: `42`. |
| `precision` | Dígitos de precisión para las aproximaciones: `50`, configurable entre 32 y 80. |

La tabla abrevia los parámetros estimados para facilitar su lectura; la consola muestra sus cifras completas. `dt`, semilla y precisión son decisiones de implementación. La configuración manual `Parametros()` tiene tasa `0.1` y sigma `0`; el arranque habitual utiliza la estimación del arreglo.

Para introducir observaciones utiliza punto y coma entre elementos:

```text
[1000;1100,25;1250.5]
```

Los corchetes son opcionales. El punto o la coma sirven como separador decimal; la coma no separa observaciones ni miles. No se utiliza `eval()`.

El modo automático necesita al menos dos datos y ningún divisor cero al calcular tasas relativas. El modo manual conserva tasa, sigma, paso, semilla y precisión; actualiza `p0` con el primer dato y el horizonte con `n−1`. Permite un único dato, con horizonte cero.

---

## 5. Estructura del proyecto

```text
02APE/
├── main.py                 # Arranque, argumentos y vista de consola
├── Modelo/
│   ├── datos.py            # Observaciones y lectura de arreglos
│   ├── parametros.py       # Configuración validada
│   ├── estimacion.py       # Estimación de tasa y ruido
│   ├── numeros.py          # Validación y operaciones decimales
│   ├── tiempo.py           # Mallas temporales
│   ├── estrategias.py      # Los cuatro modelos
│   ├── resultados.py       # Serie y experimento
│   └── analisis.py         # Comparación del ruido con varias semillas
├── Controlador/
│   └── simulacion.py       # Coordina estrategias y conserva el experimento
├── Vista/
│   └── graficas.py         # Gráficas y exportación PNG/CSV
├── tests/                  # Pruebas existentes
├── resultados/             # Ejemplos y directorio de salida por defecto
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── PROMPT.md               # Registro del encargo previo
```

### Organización del código

La separación MVC está respaldada por la implementación: `Modelo/` contiene ecuaciones y datos, `Controlador/` coordina los experimentos y las vistas presentan la información. La vista de consola está en `main.py`; la vista gráfica y la exportación están en `Vista/graficas.py`.

Las cuatro clases de simulación comparten la operación `simular(parametros)`, definida mediante `EstrategiaSimulacion`, un `Protocol`. El controlador permite seleccionar o inyectar estrategias; esto corresponde al patrón Strategy. `Parametros`, `Serie` y `Experimento` son clases de datos inmutables. Esta organización describe responsabilidades concretas sin afirmar cumplimiento formal de todos los principios SOLID.

---

## 6. Funcionamiento y resultados

### Ecuaciones implementadas

| Modelo | Regla |
|:--|:--|
| **Determinístico exponencial** | `P(t) = P0 × exp(r × t)`. Calcula cada punto desde P0. |
| **Discreto** | `P[k+1] = P[k] + r × P[k]`. Avanza un período por paso. |
| **Estocástico** | `P[k+1] = max(0, P[k] + r × P[k] + epsilon[k])`, con `epsilon ~ Normal(0, sigma²)`. |
| **Continuo mediante Euler** | Aproxima `dP/dt = rP` con `P(t+h) = P(t) + h × r × P(t)`. |

El mismo valor de `r` tiene interpretaciones distintas: es una tasa instantánea en la exponencial y una variación relativa por período en la recurrencia. Por eso `exp(r)` y `1+r` producen resultados diferentes.

La estimación inicial promedia las variaciones `(dato siguiente − dato actual) / dato actual`. Después calcula los residuos respecto a la recurrencia y utiliza su desviación estándar poblacional centrada, con divisor `n`, como sigma. Es una estimación descriptiva; no valida una hipótesis de ruido normal ni una calibración científica.

### Escenarios e interpretación

| Escenario | Tasa | Sigma | Comportamiento que permite comparar |
|:--|--:|--:|:--|
| crecimiento | `0.1` | `0` | Aumento de población y diferencia entre métodos. |
| decrecimiento | `−0.1` | `0` | Descenso con un paso Euler compatible. |
| constante | `0` | `0` | Conservación de la población inicial. |

Los escenarios conservan el resto de los parámetros. Con sigma cero, el estocástico coincide con el discreto en condiciones válidas. Las cruces negras de las gráficas son observaciones de referencia; las líneas y marcadores representan las series calculadas. Las observaciones originales permanecen visibles aunque se elija decrecimiento.

El análisis de ruido compara sigma cero, sigma base y el doble de sigma base con las mismas 30 semillas por nivel. Si la sigma configurada es cero, toma base uno. Muestra la media y la desviación poblacional de los valores finales en la terminal. Una trayectoria aislada no demuestra el efecto general del ruido; la restricción a cero también puede modificar la media. Con ruido aditivo, llegar a cero no impide que la población vuelva a aumentar.

### Archivos de salida

Por defecto se guardan en `02APE/resultados/`, independientemente del directorio de lanzamiento. `--salida` permite cambiarlo.

| Ejecución | Archivos generados |
|:--|:--|
| `--graficas` o menú 10 | `comparacion.png` y `comparacion.csv`. |
| `--escenarios` | Pares `.png` y `.csv` para `crecimiento`, `decrecimiento` y `constante`. |
| `--analizar-ruido` o menú `a` | Resumen por terminal; no guarda automáticamente un TXT. |

Los CSV contienen las columnas `modelo`, `tiempo_periodos` y `poblacion`, con todos los puntos y las observaciones de referencia. Conservan los valores decimales como texto; la vista convierte a `float` únicamente para dibujar.

Actualmente están versionados los ejemplos PNG de [comparación](resultados/comparacion.png), [crecimiento](resultados/crecimiento.png), [decrecimiento](resultados/decrecimiento.png) y [población constante](resultados/constante.png), junto con [analisis_ruido.txt](resultados/analisis_ruido.txt). Los CSV son salidas generadas y no están versionados.

Al repetir un nombre se reemplazan sus salidas. Cada archivo se escribe mediante un temporal, pero PNG y CSV no forman una transacción conjunta: un error al exportar el CSV puede dejar la imagen nueva y la tabla anterior.

### Precisión y límites

Las entradas se convierten desde texto a `Decimal`; la API del dominio rechaza `float` y booleanos. Las sumas y productos usan precisión adaptativa y rechazan operaciones que perderían cifras dentro de los límites establecidos. La exponencial, las divisiones y las raíces son aproximaciones; el ruido de NumPy también tiene precisión finita.

La malla incluye cero y el horizonte, con un máximo de 10001 puntos. Euler reduce el último paso cuando es necesario. Para varios períodos, el discreto exige `r ≥ −1`; Euler exige `1+h×r ≥ 0` en cada paso. Estas condiciones evitan poblaciones negativas por esas reglas de actualización.

También se limitan las entradas a 80 dígitos, las operaciones exactas a 10000 dígitos y el almacenamiento a 2000000 dígitos de población por serie. El análisis de ruido admite horizontes de hasta 100 períodos. Una combinación puede alcanzar los límites de recursos aunque sus parámetros individuales sean válidos.

---

## 7. Información adicional

### Pruebas existentes y comprobación de esta revisión

Desde `02APE/`, con su entorno activado:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip check
```

Las pruebas de `tests/` cubren ecuaciones con referencias racionales y exponenciales, reproducibilidad, estimación, entradas inválidas, límites de recursos, comportamiento del controlador, menú, procesos de consola y exportación gráfica con Agg.

Durante esta revisión se ejecutaron **353 casos, todos aprobados**, en una copia temporal de código y pruebas, con Python 3.14.4 y las versiones indicadas arriba. También se comprobaron `--help`, `--comparar`, `--graficas`, `--escenarios` y `--analizar-ruido`. La generación PNG/CSV se realizó en `/tmp` con `Agg` para conservar los resultados del proyecto. El entorno existente también pasó `python -m pip check` sin dependencias incompatibles. No se verificaron ventanas interactivas ni una instalación nueva de dependencias.

### Problemas frecuentes

| Problema | Qué revisar |
|:--|:--|
| Falta NumPy o Matplotlib | Utiliza el intérprete del entorno e instala su `requirements.txt`. |
| No se abre una ventana | Comprueba el escritorio, el backend y `--mostrar`; Agg solo genera archivos. |
| Falla la comparación con horizonte fraccionario | Discreto y estocástico necesitan un número entero de períodos. |
| Euler rechaza el decrecimiento | Reduce `dt` para que cada factor `1+h×r` sea no negativo. |
| No se pueden estimar parámetros | Revisa que haya dos observaciones y divisores distintos de cero, o utiliza modo manual. |
| No se pueden guardar resultados | Revisa permisos y ruta de salida; repetir un nombre reemplaza el archivo anterior. |

### Declaración de uso de IA

El README previo declara asistencia de Codex en la implementación, las pruebas y la documentación de esta práctica. [PROMPT.md](PROMPT.md) conserva el encargo previo; algunas de sus solicitudes, como NetLogo, no corresponden a la implementación actual. En esta revisión se utilizó Codex para inspeccionar los archivos actuales, comprobar comandos y pruebas y reorganizar la documentación. Esta asistencia no determina la autoría ni el porcentaje de código generado con IA. Corresponde al estudiante revisar y poder explicar el trabajo antes de entregarlo.
