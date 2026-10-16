# APE03 — Simulación de líneas de espera M/M/1

**Asignatura:** Simulación · **Carrera:** Computación · **Ciclo:** Quinto · **Universidad:** Universidad Nacional de Loja (UNL)

**Tecnologías:** Python 3 · SimPy · NumPy · Matplotlib · Arquitectura MVC

> **Alcance de este README:** documentación del contenido real de `Practica 3.zip`. Este proyecto muestra tablas en la terminal y gráficas en ventanas de Matplotlib. **No incluye una interfaz de escritorio con Tkinter, clientes individuales moviéndose entre cajas, exportación CSV ni una carpeta de pruebas automatizadas.**

## Contenido

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Tecnologías utilizadas](#2-tecnologías-utilizadas)
3. [Instalación en Linux, Windows y macOS](#3-instalación-en-linux-windows-y-macos)
4. [Uso del programa](#4-uso-del-programa)
5. [Estructura del proyecto](#5-estructura-del-proyecto)
6. [Funcionamiento y resultados](#6-funcionamiento-y-resultados)
7. [Información adicional](#7-información-adicional)

---

## 1. Descripción del proyecto

Este programa desarrolla la **Práctica APE03: simulación de un sistema de líneas de espera M/M/1 mediante SimPy**. Representa un sistema en el que llegan clientes aleatoriamente, esperan si el servidor está ocupado y reciben atención de **un único servidor** bajo la disciplina **FIFO** (*First In, First Out*: primero en llegar, primero en ser atendido).

El propósito es **comparar las métricas del modelo matemático M/M/1 con las estimaciones de una simulación computacional** y observar cómo aumenta la congestión cuando la tasa de llegadas se aproxima a la capacidad de atención.

### Qué hace el programa

- Ejecuta automáticamente los **tres escenarios** especificados en la práctica.
- Genera tiempos entre llegadas y tiempos de servicio con distribuciones **exponenciales** mediante `random.expovariate`.
- Utiliza `simpy.Environment` y `simpy.Resource(capacity=1)` para modelar la atención.
- Calcula las métricas teóricas **ρ, L, Lq, W y Wq**.
- Muestra en la terminal una **tabla de comparación teórico/simulado**, con el error porcentual para cada métrica.
- Abre una **animación de la evolución de la cola** para los tres escenarios, usando Matplotlib.
- Presenta seis gráficas: evolución de la cola y distribución de tiempos de espera para cada escenario.
- Guarda el conjunto de gráficas estáticas en **`graficas_mm1.png`**.

### Escenarios utilizados

| Escenario | Tasa de llegadas (λ) | Tasa de servicio (μ) | Condición |
|:--|--:|--:|:--|
| 1 | 2.0 | 3.0 | Sistema estable |
| 2 | 2.5 | 3.0 | Mayor utilización |
| 3 | 2.9 | 3.0 | Cerca de saturación |

**Parámetros programados:** tiempo de simulación `20000` unidades y semilla aleatoria `42`. Son valores definidos en el código, **no campos editables de una interfaz gráfica**.

---

## 2. Tecnologías utilizadas

| Herramienta | ¿Para qué se utiliza? |
|:--|:--|
| **Python 3** | Lenguaje principal de la aplicación. |
| **SimPy ≥ 4.0** | Motor de simulación de eventos discretos: procesos, tiempos y recurso de atención. |
| **NumPy ≥ 1.24** | Preparación de arreglos e índices para las animaciones y gráficas. |
| **Matplotlib ≥ 3.7** | Animación de cola, histogramas, gráficas y exportación PNG. |
| **`random` (Python)** | Generación pseudoaleatoria de tiempos exponenciales mediante `expovariate`. |
| **`dataclasses` (Python)** | Agrupación sencilla de escenarios, métricas y resultados. |

Las versiones indicadas son los **mínimos declarados por `requirements.txt`**; no son versiones fijas ni una certificación de compatibilidad en todos los sistemas.

Este proyecto **no requiere** Docker, una base de datos, un servidor web, credenciales ni variables `.env`.

---

## 3. Instalación en Linux, Windows y macOS

### Requisitos previos

- Tener instalado **Python 3** y acceso a una terminal.
- Contar con `pip` y soporte para crear entornos virtuales con `venv`.
- Tener un entorno de escritorio disponible para abrir las ventanas de Matplotlib.
- Conexión a Internet durante la primera instalación de bibliotecas.

**Importante:** todos los comandos de instalación y ejecución se realizan desde la carpeta que contiene `requirements.txt` y `src/`, **no desde la carpeta `src`**.

### 3.1. Linux (Ubuntu / Debian)

Descomprime `Practica 3.zip`, abre una terminal y entra a la carpeta:

```bash
cd "Practica 3"
```

Si no tienes instalados los componentes de Python o el soporte gráfico de Tk:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
```

Crea y activa el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias y ejecuta el programa:

```bash
python -m pip install -r requirements.txt
python -m src.main
```

> `python3-tk` puede ser necesario para que Matplotlib abra ventanas cuando utiliza el backend TkAgg. **El proyecto no implementa su interfaz con Tkinter.**

### 3.2. Windows (PowerShell)

Instala Python 3 desde [python.org](https://www.python.org/downloads/) si aún no lo tienes. Abre PowerShell dentro de la carpeta extraída `Practica 3`, donde se encuentra `requirements.txt`.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

Estos comandos **no requieren activar** el entorno virtual. Si prefieres activarlo, utiliza `\.venv\Scripts\Activate.ps1` cuando la configuración de PowerShell lo permita.

Si el comando `py` no existe, comprueba la instalación de Python e intenta `python` en su lugar.

### 3.3. macOS (Terminal)

Instala una versión actual de Python 3 si aún no está disponible; puedes obtenerla desde [python.org](https://www.python.org/downloads/macos/). Algunas instalaciones de Python requieren componentes gráficos adicionales para mostrar ventanas; comprueba que tu instalación soporte Matplotlib con un backend interactivo.

Desde la carpeta extraída:

```bash
cd "Practica 3"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

### Ejecutarlo otra vez

No tienes que reinstalar las bibliotecas cada vez. Desde la carpeta principal del proyecto:

**Linux/macOS:**

```bash
source .venv/bin/activate
python -m src.main
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Para salir del entorno virtual activado, escribe `deactivate`.

---

## 4. Uso del programa

Al iniciar `python -m src.main` ocurre lo siguiente:

1. El programa obtiene los tres escenarios definidos en `ModeloMM1.construir_escenarios()`.
2. Para cada escenario estable, ejecuta una simulación de **20000 unidades de tiempo** con SimPy.
3. Muestra por consola un **resumen** y una **tabla teórico/simulado**, que incluye el error porcentual.
4. Abre una ventana de Matplotlib con **tres paneles animados**, uno por escenario. La animación representa **la evolución del número de clientes en cola**, no clientes individuales caminando entre cajas.
5. Al cerrar esa ventana, abre otra con **seis gráficas** (tamaño de cola e histogramas de espera para los tres escenarios).
6. Genera o reemplaza `graficas_mm1.png` en el directorio desde el que se ejecutó el programa.

### Interpretación de las gráficas

- **Animación de cola (3 paneles):** línea azul = tamaño registrado de la cola; punto rojo = muestra actual de la animación. Usa fotogramas seleccionados del historial, no cada evento como movimiento individual.
- **Gráfica superior de cada escenario:** evolución del tamaño de cola; el código muestra hasta las primeras 800 observaciones registradas.
- **Gráfica inferior de cada escenario:** histograma de tiempos de espera en cola; las líneas verticales representan el promedio simulado y el valor teórico de **Wq**.

La barra de herramientas de Matplotlib, según el backend disponible, permite acciones habituales como **zoom, desplazamiento, restablecer vista y guardar la imagen**.

### Cambiar los parámetros

El programa **no tiene formulario de configuración**. Para cambiar los valores, edita las constantes de `src/controllers/m_controller.py`:

```python
TIEMPO_SIMULACION = 20000
SEMILLA = 42
```

Para cambiar los escenarios, modifica `construir_escenarios()` en `src/models/m_model.py`, pero conserva los tres escenarios oficiales para entregar la práctica.

---

## 5. Estructura del proyecto

```text
Practica 3/
├── requirements.txt               # SimPy, NumPy y Matplotlib
├── graficas_mm1.png               # Imagen presente en el ZIP original
└── src/
    ├── __init__.py
    ├── main.py                    # Punto de entrada del programa
    ├── models/
    │   ├── __init__.py
    │   └── m_model.py             # Escenarios, fórmulas y tipos de resultados
    ├── controllers/
    │   ├── __init__.py
    │   └── m_controller.py        # Ejecución SimPy y cálculos simulados
    └── views/
        ├── __init__.py
        └── m_view.py              # Tablas, gráficas y animación
```

El archivo ZIP de origen también contiene carpetas `__pycache__/` generadas por Python, que **no son necesarias para ejecutar el proyecto y no conviene subir a GitHub**.

### Arquitectura MVC

| Componente | Archivo | Responsabilidad en esta implementación |
|:--|:--|:--|
| **Modelo** | `src/models/m_model.py` | Representa escenarios y resultados; calcula métricas teóricas. |
| **Controlador** | `src/controllers/m_controller.py` | Crea y ejecuta los procesos de SimPy, registra datos y calcula métricas simuladas. |
| **Vista** | `src/views/m_view.py` | Imprime las tablas y construye gráficas y animaciones con Matplotlib. |
| **Inicio** | `src/main.py` | Coordina la ejecución de los tres escenarios y la presentación final. |

**Flujo general:** `main.py` → escenarios del modelo → simulaciones del controlador → resultados → vista.

El proyecto utiliza **clases de datos, funciones separadas y organización MVC**. Esto facilita su lectura; no significa que implemente formalmente todos los principios SOLID.

---

## 6. Funcionamiento y resultados

### Fundamento del modelo M/M/1

- Primera **M**: llegadas Poisson (intervalos entre llegadas exponenciales).
- Segunda **M**: tiempos de servicio exponenciales.
- **1**: un solo servidor.
- Disciplina de cola utilizada: **FIFO**.

Las tasas se miden por la misma unidad de tiempo. El régimen estacionario teórico exige **0 < λ < μ**.

| Métrica | Significado | Fórmula teórica |
|:--|:--|:--|
| **ρ** | Fracción esperada de tiempo ocupado el servidor | `λ / μ` |
| **L** | Número promedio de clientes en el sistema | `λ / (μ − λ)` |
| **Lq** | Número promedio de clientes esperando en cola | `λ² / [μ(μ − λ)]` |
| **W** | Tiempo promedio en el sistema | `1 / (μ − λ)` |
| **Wq** | Tiempo promedio de espera antes de la atención | `λ / [μ(μ − λ)]` |

> La fórmula correcta para la utilización es **ρ = λ / μ**. No debe invertirse.

### Datos generados y presentación

El controlador guarda durante cada corrida listas de tiempos de espera, tiempos de servicio, llegadas, salidas y observaciones de tamaño de cola. La vista usa esos registros para construir tablas, una animación y las figuras.

La tabla de la terminal incluye las cinco métricas teóricas y sus estimaciones simuladas; el error mostrado se calcula como `|simulado − teórico| / teórico × 100`.

La imagen `graficas_mm1.png` se crea con `plt.savefig()` durante la ejecución. **No se genera ningún archivo CSV** en esta versión.

### Limitaciones conocidas de la implementación actual

Conviene revisar estas consideraciones antes de usar los resultados en un informe:

- Las **estimaciones simuladas no aplican período de calentamiento**; el modelo empieza con el sistema vacío.
- Para **L simulado**, el código utiliza `Lq simulado + ρ teórico`; **no realiza una integración temporal independiente de L**.
- La **utilización simulada** se aproxima sumando duraciones de servicio generadas y dividiendo entre `20000` (con límite superior de 1); no se calcula con una integral exacta de ocupación truncada en el horizonte.
- El cálculo de **W simulado** empareja registros mediante `zip()`; esto puede producir sesgos si hay clientes cuyo servicio no termina antes de T.
- Los cambios de tamaño de cola se registran en algunos instantes de ejecución del proceso y deben revisarse si se requiere medir el promedio temporal exacto de la cola.
- La semilla se reinicia con el mismo valor **42** en cada escenario, de acuerdo con el código actual.

Por estas razones, **no debe asumirse que las estimaciones experimentales de este ZIP ya están completamente validadas matemáticamente**. Las fórmulas teóricas sí están explícitas en el modelo. La animación representa los registros existentes, no un seguimiento individual completo y sincronizado de todos los clientes.

---

## 7. Información adicional

### Comprobación básica de instalación

Con el entorno virtual disponible, verifica las bibliotecas:

```bash
python -c "import simpy, numpy, matplotlib; print('Dependencias instaladas correctamente')"
```

Para comprobar la sintaxis de los módulos:

```bash
python -m compileall -q src
```

**Nota:** el ZIP proporcionado **no contiene una carpeta `tests/` ni pruebas automatizadas**, por lo que no corresponde afirmar que pasó un conjunto de pruebas unitarias. Esta comprobación de sintaxis no sustituye una validación de la simulación.

### Solución de problemas frecuentes

| Problema | Qué revisar |
|:--|:--|
| `ModuleNotFoundError: No module named 'src'` | Ejecuta `python -m src.main` desde la carpeta **Practica 3**, no desde `src/`. |
| `ModuleNotFoundError: No module named 'simpy'` | Activa el entorno correcto e instala `python -m pip install -r requirements.txt`. |
| No aparecen las ventanas | Comprueba que estés en una sesión gráfica y que Matplotlib tenga un backend interactivo; en Ubuntu puede hacer falta `python3-tk`. |
| El programa parece detenido | Revisa si la ventana de animación está abierta. Al cerrarla, continúa la visualización de las gráficas estáticas. |
| No encuentro `graficas_mm1.png` | Se guarda en el **directorio actual de ejecución**; si ya existía, se reemplaza. |
| El resultado simulado difiere del teórico | La simulación es aleatoria y finita; revisa también las limitaciones de cálculo indicadas arriba. |

### Equipo de trabajo

**Integrantes:** Daniel, Jimmy, María y Anderson.

Las responsabilidades y contribuciones concretas deben documentarse según los cambios realizados realmente por cada integrante; este archivo no sustituye el historial de Git.

### Control de versiones

Se recomienda incluir un `.gitignore` con, como mínimo:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.idea/
.DS_Store
Thumbs.db
```

Al subir el trabajo, conserva `src/`, `requirements.txt` y este `README.md`. No subas el entorno virtual. El archivo PNG puede conservarse como ejemplo de salida si así lo requiere la entrega.

### Declaración de uso de IA

Este README se preparó con asistencia de ChatGPT a partir de la inspección del código fuente de `Practica 3.zip` y de los requisitos de documentación suministrados. **No constituye una declaración sobre la autoría ni el porcentaje de IA del resto del proyecto.** El equipo debe registrar de manera veraz las herramientas, prompts, archivos afectados y revisiones humanas efectuadas, conforme a las instrucciones del docente.

### Licencia

El ZIP proporcionado **no incluye un archivo de licencia**. Por tanto, no se declara aquí una licencia de software que sus integrantes no hayan elegido.

---

**Proyecto académico de simulación de líneas de espera M/M/1 — Computación, UNL.**
