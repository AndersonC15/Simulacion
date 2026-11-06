# APE01 — Modelo de índice de lluvia

**Asignatura:** Simulación · **Ciclo:** Quinto · **Tecnologías:** Python · Decimal · Matplotlib · Organización MVC

Esta práctica calcula un índice de lluvia a partir de humedad, nubosidad y temperatura. Compara dos configuraciones de pesos usando las nueve mediciones incluidas en la guía y permite evaluar un caso manual. El índice es una regla matemática del ejercicio; no es una predicción meteorológica validada.

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

El objetivo es identificar variables y parámetros de un modelo matemático, calcular su resultado y observar cómo cambia al modificar sus pesos.

La implementación permite:

- Consultar una tabla con el modelo original y otra con el ajustado.
- Clasificar cada índice en cuatro estados de lluvia.
- Evaluar humedad, nubosidad y temperatura ingresadas por consola con los pesos originales.
- Generar dos gráficas: variables normalizadas y comparación de índices.
- Trabajar con decimales sin redondeos silenciosos en el cálculo y la clasificación, dentro de los límites admitidos.

Los datos de entrada están en [`Modelo/datos.py`](Modelo/datos.py). Son nueve mediciones entre las 06:00 y las 22:00; el programa no completa las horas restantes con valores inventados.

---

## 2. Tecnologías utilizadas

| Herramienta | Uso en esta implementación |
|:--|:--|
| **Python 3** | Lenguaje de la aplicación y ejecución del menú. |
| **`decimal.Decimal`** | Conversión de entradas, cálculo de índices y comparación exacta con los umbrales. Forma parte de Python. |
| **Matplotlib 3.11.2** | Construcción, visualización y guardado de las gráficas. |
| **NumPy 2.5.3** | Dependencia declarada, también requerida por Matplotlib; el modelo de lluvia no la utiliza en sus cálculos. |
| **Pillow 13.0.0** | Inspección del formato PNG en las pruebas de gráficas. |
| **`unittest`, `unittest.mock` y `fractions.Fraction`** | Pruebas, simulación de interacciones y referencias racionales para los cálculos. Forman parte de Python. |

Las versiones se encuentran fijadas en [`requirements.txt`](requirements.txt), que también conserva las dependencias transitivas del entorno registrado. No se necesita Java, Maven, una base de datos ni un servidor para ejecutar esta carpeta.

---

## 3. Instalación en Linux, Windows y macOS

### Requisitos previos

Se necesita **Python 3** compatible con las versiones de `requirements.txt`, con `pip` y soporte para `venv`. Se necesita conexión a Internet al instalar las dependencias y un entorno gráfico para abrir ventanas de Matplotlib. También es posible generar los PNG sin ventanas.

Todos los comandos siguientes se ejecutan dentro de **`01APE`**, donde están `main.py` y `requirements.txt`. Desde la raíz del repositorio:

```bash
cd 01APE
```

### 3.1. Linux y macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Si ya existe `.venv`, actívalo y comprueba sus dependencias antes de ejecutarlo. No es necesario recrearlo en cada uso. Para abandonar el entorno activado, utiliza `deactivate`.

### 3.2. Windows (PowerShell)

Desde `01APE`, utiliza un Python compatible instalado en el equipo:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Estos comandos usan el intérprete del entorno sin exigir su activación. Si no está disponible el lanzador `py`, revisa la instalación de Python.

### 3.3. Ejecución sin ventanas

En Linux/macOS, con el entorno preparado y desde `01APE`:

```bash
printf '3\n0\n' | MPLBACKEND=Agg python main.py
```

La opción 3 genera las dos imágenes y la opción 0 termina el programa. Este comando reemplaza los PNG existentes en `graficas_generadas/`.

Las recetas se revisaron contra el punto de entrada y los archivos actuales. La instalación completa y la ejecución gráfica en Windows/macOS no se comprobaron en esta revisión documental; las comprobaciones ejecutadas se detallan en la sección 7.

---

## 4. Uso del programa

Al ejecutar `python main.py`, aparece el menú:

```text
1. Tabla con modelo original
2. Tabla con modelo ajustado
3. Generar gráficas
4. Ingresar un caso manual
0. Salir
```

Las opciones 1 y 2 muestran las nueve mediciones, H, N, Tf, índice y clasificación; también enumeran las horas con lluvia probable o lluvia. La opción 4 solicita humedad, nubosidad y temperatura y evalúa ese caso con el modelo original. El caso manual no se agrega a los datos de la guía ni a sus gráficas.

### Entradas y validación

| Campo | Intervalo admitido |
|:--|:--|
| Humedad | De 0 a 100 %, incluidos los extremos. |
| Nubosidad | De 0 a 100 %, incluidos los extremos. |
| Temperatura | De −50 a 60 °C, incluidos los extremos. |

El intervalo térmico es una decisión de la aplicación, no una exigencia de la guía. Se admite punto o coma decimal, signo, espacios externos y notación científica, por ejemplo `35,25` o `3.5e1`. La coma siempre se interpreta como decimal: `1,000` significa uno. No se admiten separadores de miles ni espacios internos.

La entrada está limitada a 256 caracteres, 120 dígitos en el coeficiente decimal y exponentes entre −120 y 120, tanto escritos como en la representación interna de `Decimal`. Por ejemplo, `1.23e-120` se rechaza porque su exponente interno es −122. Se rechazan texto vacío, NaN e infinitos. Las API del modelo admiten texto, enteros y `Decimal`; rechazan `float` y booleanos.

Ante una entrada incorrecta, la consola informa el error y permite volver a intentarlo. EOF y Ctrl+C finalizan el menú de forma controlada, incluso durante un caso manual.

### Gráficas

La opción 3 genera o reemplaza estos archivos dentro de `01APE/graficas_generadas/`, independientemente de la carpeta de la terminal:

| Archivo | Contenido |
|:--|:--|
| `variables_modelo.png` | H, N y Tf de los nueve registros, en una escala de 0 a 1. |
| `comparacion_modelos.png` | Índices original y ajustado, con líneas en los umbrales 0.40, 0.60 y 0.75. |

Ambos PNG ya están incluidos en la carpeta actual y se pueden regenerar. Con un backend interactivo se muestran ventanas; hay que cerrarlas para regresar al menú. Con Agg se guardan los archivos sin ventanas. Si falla el inicio del backend gráfico, la vista intenta utilizar Agg.

Si no se completan ambos guardados, el programa informa el error y continúa; puede quedar una imagen anterior o parcial. Un fallo al mostrar las ventanas después de guardar se informa por separado.

---

## 5. Estructura del proyecto

```text
01APE/
├── Modelo/
│   ├── datos.py                # Nueve mediciones de la guía
│   ├── modelo.py               # Datos, validaciones, fórmula y clasificación
│   └── precision.py            # Conversión y operaciones decimales
├── Vista/
│   ├── consola.py              # Captura, mensajes y tablas
│   └── graficas.py             # Dibujo, guardado y visualización
├── Controlador/
│   └── controlador.py          # Coordinación del menú
├── tests/
│   ├── test_modelo.py
│   ├── test_entradas.py
│   ├── test_mvc.py
│   └── test_graficas.py
├── graficas_generadas/         # Dos PNG incluidos y regenerables
├── main.py                     # Punto de entrada
├── requirements.txt
├── VALIDACION.md               # Registro de una revisión anterior
├── PROMPT.md                   # Registro del apoyo de herramientas
└── ape_guia simulacion semana 1.pdf
```

### Organización MVC

| Componente | Responsabilidad comprobable en el código |
|:--|:--|
| **Modelo** | `RegistroMeteorologico` y `ParametrosModelo` validan mediciones y pesos; `ModeloLluvia` calcula resultados sin pedir entradas, imprimir ni dibujar. |
| **Vista** | `VistaConsola` presenta tablas y captura texto; `VistaGraficas` crea los PNG y gestiona su visualización. |
| **Controlador** | `ControladorLluvia` coordina las opciones, entrega resultados a la vista y gestiona errores de generación. |
| **Inicio** | `main.py` construye y conecta modelo, vistas y controlador. |

Los registros, parámetros y resultados se representan con clases de datos inmutables. El controlador recibe sus dependencias al construirse y las pruebas las sustituyen cuando necesitan aislar su coordinación. Estas responsabilidades respaldan la organización MVC; no se afirma que el proyecto demuestre todos los principios SOLID.

---

## 6. Funcionamiento y resultados

### Fórmula y ajuste de pesos

Primero se normalizan los porcentajes: `H = humedad / 100` y `N = nubosidad / 100`.

| Configuración | Fórmula |
|:--|:--|
| Original | `I = 0.50H + 0.30N + 0.20Tf` |
| Ajustada | `I = 0.40H + 0.40N + 0.20Tf` |

Los pesos deben ser finitos, no negativos y sumar exactamente 1. El ajuste traslada 0.10 del peso de humedad al de nubosidad: `I_ajustado − I_original = 0.10(N − H)`. El índice disminuye si N es menor que H y aumenta si N es mayor. No hay datos de lluvia observada con los cuales afirmar que el ajuste predice mejor.

### Factor de temperatura y clasificación

| Temperatura °C | ≤10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | ≥28 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Tf | 1.00 | 0.90 | 0.80 | 0.70 | 0.60 | 0.50 | 0.40 | 0.30 | 0.20 | 0.10 |

Para temperaturas intermedias, el código interpola linealmente: entre 10 y 28 °C usa `Tf = 1 − (temperatura − 10) × 0.05`. A 15 °C corresponde 0.75 y a 17 °C, 0.65. Fuera de ese tramo mantiene los factores de los extremos de la tabla, respetando los límites de entrada.

| Índice | Estado |
|:--|:--|
| `I < 0.40` | Sin lluvia |
| `0.40 ≤ I < 0.60` | Baja posibilidad |
| `0.60 ≤ I < 0.75` | Lluvia probable |
| `I ≥ 0.75` | Lluvia |

### Resultados de los datos incluidos

Los siguientes valores corresponden al código actual y a los casos de referencia de `tests/test_modelo.py`, ejecutados durante esta revisión:

| Hora | Humedad % | Nubosidad % | °C | Tf | I original | I ajustado |
|:--|--:|--:|--:|--:|--:|--:|
| 06:00 | 65 | 40 | 14 | 0.80 | 0.605 | 0.580 |
| 08:00 | 70 | 50 | 16 | 0.70 | 0.640 | 0.620 |
| 10:00 | 68 | 45 | 18 | 0.60 | 0.595 | 0.572 |
| 12:00 | 60 | 30 | 22 | 0.40 | 0.470 | 0.440 |
| 14:00 | 75 | 70 | 20 | 0.50 | 0.685 | 0.680 |
| 16:00 | 85 | 85 | 18 | 0.60 | 0.800 | 0.800 |
| 18:00 | 92 | 95 | 16 | 0.70 | 0.885 | 0.888 |
| 20:00 | 88 | 90 | 17 | 0.65 | 0.840 | 0.842 |
| 22:00 | 80 | 75 | 15 | 0.75 | 0.775 | 0.770 |

En el modelo original hay lluvia probable a las 06:00, 08:00 y 14:00, y lluvia a las 16:00, 18:00, 20:00 y 22:00. El ajustado cambia la clasificación de las 06:00 a baja posibilidad. Ambos tienen su mínimo a las 12:00 y su máximo a las 18:00.

El ejemplo de la guía, con humedad 90 %, nubosidad 80 % y temperatura 18 °C, da `I = 0.81` con los pesos originales. Mostrar el índice como 81 % no lo convierte en una probabilidad calibrada.

### Precisión de los cálculos

[`Modelo/precision.py`](Modelo/precision.py) convierte el texto directamente a `Decimal` y dimensiona un contexto local para cada suma y producto. Activa las trampas `Inexact` y `Rounded`, de modo que una precisión insuficiente cause un error en lugar de un redondeo silencioso. Los resultados internos pueden tener más dígitos que las entradas admitidas.

Los umbrales se comparan sin redondeo ni tolerancias. La consola muestra el valor calculado y elimina únicamente ceros decimales finales; adapta las columnas a su contenido. La conversión a `float` se realiza al dibujar y no vuelve al modelo. Las pruebas incluyen referencias con `Fraction`, entradas de 120 dígitos y un índice de `1e-242`; esto no implica precisión infinita para operaciones ajenas a la aplicación.

---

## 7. Información adicional

### Pruebas y comprobaciones

Con las dependencias instaladas, desde `01APE`:

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py Modelo Vista Controlador tests
python -m pip check
```

La suite existente cubre índices de referencia, temperatura, umbrales, precisión, entradas inválidas, coordinación del menú, EOF, SIGINT en POSIX y generación PNG en carpetas temporales. Los casos de TkAgg y QtAgg simulan la llamada a `show`; no demuestran por sí solos que se abran ventanas reales.

**Comprobación de esta revisión documental:** se inspeccionaron los módulos, dependencias, pruebas y PDF actuales. En una copia temporal se ejecutaron las **12 pruebas de `tests.test_modelo` con Python 3.14.4**, todas correctas, y se comprobó la sintaxis mediante AST de los 15 archivos Python. No se ejecutó la suite completa ni se regeneraron los PNG del repositorio: el entorno local de esta práctica no tiene instalados Matplotlib, NumPy ni Pillow. Tampoco se repitió la instalación de dependencias ni se comprobaron ventanas reales.

[`VALIDACION.md`](VALIDACION.md) conserva un registro previo de pruebas e instalación; sus resultados no se presentan como ejecuciones de esta revisión.

### Problemas frecuentes

| Problema | Qué revisar |
|:--|:--|
| No se encuentra `matplotlib` o `PIL` | Usa el intérprete del entorno e instala `python -m pip install -r requirements.txt`. |
| No aparecen ventanas | Revisa la sesión gráfica y el backend de Matplotlib; con Agg se generan archivos sin ventanas. |
| El programa espera después de graficar | Cierra las ventanas de Matplotlib para volver al menú. |
| No se guardan los PNG | Comprueba los permisos de `graficas_generadas/`; el menú informa si falla la escritura. |
| Una tabla queda demasiado ancha | Las entradas largas conservan sus decimales; puede ser necesario ampliar la terminal. |

### Alcance respecto a la guía

El [PDF local](ape_guia%20simulacion%20semana%201.pdf) describe el índice de lluvia, pero sus resultados esperados y preguntas de control también mencionan crecimiento exponencial, r y P₀. Esta implementación sigue el procedimiento de lluvia. Además, la guía solicita Java y Python; esta carpeta contiene únicamente la implementación en Python.

### Declaración de uso de IA

[`PROMPT.md`](PROMPT.md) y `VALIDACION.md` registran asistencia previa de Codex en implementación, pruebas y documentación. En esta revisión se utilizó Codex para inspeccionar los archivos actuales, reorganizar y redactar este README y ejecutar las comprobaciones indicadas. No se atribuyen porcentajes de código generado, autorías del equipo ni autorización del docente que no estén acreditados. Corresponde al estudiante revisar y comprender lo entregado.
