# APE 01 — Índice de lluvia

Práctica de Simulación en Python. Procesa las nueve mediciones de la guía,
clasifica un índice de lluvia, compara dos configuraciones de pesos, permite
evaluar un caso manual y genera dos gráficas. No completa las 24 horas con
mediciones inventadas ni representa una predicción meteorológica validada.

## Instalación y ejecución

Se requiere **Python 3.12 o posterior** y `pip`. Las versiones fijadas son
`numpy==2.5.3` (metadatos: Python ≥3.12) y `matplotlib==3.11.2`
(Python ≥3.11). La instalación y ejecución se verificaron con Python 3.14.4;
no se ejecutó este proyecto en un intérprete 3.12. NumPy se conserva como
dependencia de Matplotlib y material de la guía; no participa en los cálculos
del dominio. Las pruebas usan `unittest`, incluido en Python.

Abrir una terminal en `01APE`, no en la raíz del repositorio.

Linux/macOS, para una instalación nueva:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Windows (PowerShell), para una instalación nueva:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Si ya existe `.venv`, activarlo sin recrearlo. Sustituir `3.12` por una versión
posterior instalada cuando corresponda. Para salir del entorno: `deactivate`.
La receta PowerShell está documentada, pero no se ejecutó en Windows.

El menú conserva estas opciones:

```text
1. Tabla del modelo original
2. Tabla del modelo ajustado
3. Generar gráficas
4. Evaluar un caso manual con el modelo original
0. Salir
```

Con un backend interactivo, cerrar las ventanas de las gráficas para volver al menú.

Una entrada incorrecta permite volver a intentarlo. EOF y Ctrl+C finalizan
limpiamente, también durante la captura de un caso manual.

## Fórmulas y reglas

`H = humedad / 100`, `N = nubosidad / 100`.

- Original: `I = 0.50H + 0.30N + 0.20Tf`.
- Ajustado: `I = 0.40H + 0.40N + 0.20Tf`.

Los pesos son finitos, no negativos y suman **exactamente 1**. Trasladar 0.10
del peso de humedad al de nubosidad produce `I_ajustado − I_original = 0.10(N−H)`.
Si N < H, el índice disminuye; si N > H, aumenta; si son iguales, no cambia.
Este ajuste estudia la influencia de un parámetro: no hay observaciones de
lluvia real que permitan afirmar que predice mejor.

| Temperatura °C | ≤10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | ≥28 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tf | 1.00 | 0.90 | 0.80 | 0.70 | 0.60 | 0.50 | 0.40 | 0.30 | 0.20 | 0.10 |

Se conserva la interpolación lineal como decisión de implementación para
temperaturas intermedias. Todos los tramos tienen pendiente −0.05 por grado:
entre 10 y 28 °C se calcula `Tf = 1 − (temperatura − 10) × 0.05`.
Por ejemplo, a 15 °C corresponde 0.75 y a 17 °C, 0.65. Fuera de la tabla se
aplican los factores constantes de sus extremos.

| Índice | Estado |
|---|---|
| I < 0.40 | Sin lluvia |
| 0.40 ≤ I < 0.60 | Baja posibilidad |
| 0.60 ≤ I < 0.75 | Lluvia probable |
| I ≥ 0.75 | Lluvia |

El ejemplo de la guía, 90 % de humedad, 80 % de nubosidad y 18 °C, produce
exactamente `I = 0.81` (81 %) con los pesos originales. Es un índice ponderado;
mostrarlo como porcentaje no lo convierte en una probabilidad calibrada.

## Datos y resultados

| Hora | Humedad % | Nubosidad % | °C | Tf | I original | I ajustado |
|---|---:|---:|---:|---:|---:|---:|
| 06:00 | 65 | 40 | 14 | 0.80 | 0.605 | 0.580 |
| 08:00 | 70 | 50 | 16 | 0.70 | 0.640 | 0.620 |
| 10:00 | 68 | 45 | 18 | 0.60 | 0.595 | 0.572 |
| 12:00 | 60 | 30 | 22 | 0.40 | 0.470 | 0.440 |
| 14:00 | 75 | 70 | 20 | 0.50 | 0.685 | 0.680 |
| 16:00 | 85 | 85 | 18 | 0.60 | 0.800 | 0.800 |
| 18:00 | 92 | 95 | 16 | 0.70 | 0.885 | 0.888 |
| 20:00 | 88 | 90 | 17 | 0.65 | 0.840 | 0.842 |
| 22:00 | 80 | 75 | 15 | 0.75 | 0.775 | 0.770 |

En el original hay lluvia probable a las 06:00, 08:00 y 14:00; lluvia a las
16:00, 18:00, 20:00 y 22:00. El ajustado cambia la categoría de las 06:00 a
baja posibilidad. El mínimo de ambos índices está a las 12:00 y el máximo
a las 18:00. No hay mediciones de lluvia observada para evaluar su acierto.

## Precisión y límites de entrada

La captura convierte directamente el texto a `Decimal`, sin pasar por
`float`. Se admiten espacios externos, signo, punto **o** coma decimal y
notación científica (`3.5e1`). La coma siempre es decimal: `1,000` significa
uno; no se admiten separadores de miles. Separadores mezclados, repetidos o
espacios internos se rechazan, igual que texto vacío, NaN, sNaN e infinitos.

Los límites se aplican tanto a consola como a mediciones y pesos construidos
directamente en el modelo:

- Hasta 256 caracteres, incluidos los espacios externos.
- Hasta 120 dígitos en el coeficiente decimal, contando ceros finales conservados por Decimal.
- Exponente escrito entre −120 y 120 y exponente de la representación
  `Decimal.as_tuple()` entre −120 y 120. Por ejemplo, `1.23e-120` se rechaza:
  su exponente interno sería −122. No se recorta ni redondea para admitirlo.
- Humedad y nubosidad entre 0 y 100, incluidos los extremos.
- Temperatura entre −50 y 60 °C, incluidos los extremos. Es una decisión de
  esta aplicación, **no** un rango exigido por la guía.
- Las API aceptan texto, enteros y Decimal; rechazan float y booleanos para
  evitar arrastrar una conversión binaria previa.

Los resultados intermedios pueden superar los 120 dígitos o tener exponentes
menores que −120. No se vuelven a someter al límite de captura ni se redondean.
Las operaciones públicas sobre valores normalizados comprueban finitud y
rango [0,1]; los límites de captura corresponden a mediciones y pesos.

`Modelo/precision.py` deriva la precisión **en cada operación**:

- Producto: la suma de las longitudes de los coeficientes de sus operandos
  es una cota suficiente de los dígitos del producto.
- Suma: sean E el menor exponente y M la mayor posición decimal (`adjusted`)
  de sus operandos. Se reservan `max(1, M−E+1) + len(str(n))` dígitos para
  alinear los coeficientes y admitir el acarreo de n términos.

Normalizar usa el producto por 0.01; interpolar usa sumas y el producto por
−0.05; índice y porcentaje usan esas mismas operaciones. Todas tienen
expansión decimal finita. Cada contexto local activa las trampas `Inexact`
y `Rounded`: una precisión insuficiente produce un error en lugar de un
redondeo silencioso. Con los límites admitidos, los exponentes de las
operaciones quedan ampliamente dentro del rango estándar de Decimal.
Las pruebas incluyen pesos y mediciones de 120 dígitos, contexto externo de
solo dos dígitos y un índice exacto de `1e-242`, contrastados con `Fraction`.
No se promete precisión infinita ni exactitud para operaciones ajenas al modelo.

Los umbrales se comparan como Decimal exactos, sin `round`, `quantize` ni
tolerancias. La consola muestra el valor calculado sin limitar decimales y
solo elimina ceros finales; sus columnas se adaptan al contenido. Una
entrada larga puede requerir desplazamiento horizontal en una terminal estrecha.
La conversión a float ocurre únicamente al dibujar: nunca regresa al modelo
ni determina categorías.

## Estructura MVC y clases

```text
01APE/
├── Modelo/
│   ├── datos.py        # Nueve registros de la guía
│   ├── modelo.py       # Objetos, validaciones, fórmula y clasificación
│   └── precision.py    # Conversión y aritmética decimal exacta acotada
├── Vista/
│   ├── consola.py      # Lectura, mensajes y tablas exactas
│   └── graficas.py     # Dibujo, guardado y visualización
├── Controlador/controlador.py  # Coordinación del menú y recuperación
├── tests/             # Matemática, entradas, MVC y gráficas
├── graficas_generadas/
├── main.py            # Construcción y conexión de objetos
├── requirements.txt
├── VALIDACION.md       # Evidencia de las cinco revisiones
├── PROMPT.md           # Registro del apoyo de herramientas
└── ape_guia simulacion semana 1.pdf
```

`RegistroMeteorologico` valida y conserva una medición; `ParametrosModelo`
valida los pesos; `ResultadoLluvia` conserva el resultado, su clasificación y
su porcentaje exacto. Son objetos de datos inmutables. `ModeloLluvia` evalúa
registros individuales o tablas sin imprimir, pedir entradas ni dibujar.
`ControladorLluvia` coordina las solicitudes. `VistaConsola` recibe texto y
presenta los resultados; delega la validación al modelo. `VistaGraficas`
genera las imágenes y devuelve sus rutas en `EntregaGraficas`.

Se aplican responsabilidades separadas (S de SOLID) e inyección de las
dependencias al construir el controlador: modelo, consola y operación de
gráficas se pueden sustituir en pruebas sin cambiar su coordinación. Los
pesos permiten comparar modelos sin duplicar la fórmula. No se introducen
jerarquías ni interfaces vacías y no se afirma demostrar los cinco principios.

## Gráficas

La opción 3 guarda, respecto a la ubicación del proyecto y no a la terminal:

- `graficas_generadas/variables_modelo.png`: H, N y Tf normalizados.
- `graficas_generadas/comparacion_modelos.png`: índices de ambos modelos
  con umbrales 0.40, 0.60 y 0.75.

Matplotlib decide el backend disponible. El registro de backends distingue
Agg sin ventanas de TkAgg/QtAgg interactivos; no se busca la subcadena `agg`.
Con un escritorio y toolkit disponibles se abren ventanas; al cerrarlas se
regresa al menú. Si un backend forzado no puede iniciarse, se intenta Agg y se
informa de la situación. Para generar solo archivos en Linux/macOS:

```bash
printf '3\n0\n' | MPLBACKEND=Agg python main.py
```

Los errores de directorio o escritura se informan y permiten continuar. No se
anuncia éxito de ambas imágenes si falla el guardado; puede quedar un archivo
anterior o parcial. Un fallo de visualización posterior al guardado se
distingue de un fallo de escritura. Las figuras de cada operación se cierran
en `finally`, incluso si se produce un error.

## Pruebas

Desde `01APE`, con el entorno activado:

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py Modelo Vista Controlador tests
python -m pip check
git diff --check
```

La suite usa Agg para gráficos y no abre ventanas. Incluye los 18 índices de
referencia, tabla térmica, interpolación, ejemplo 0.81, límites y vecinos de
alta precisión, pesos inválidos, menú y llamadas directas al modelo, EOF,
SIGINT real en POSIX, PNG, errores de escritura y pruebas **simuladas** de
la llamada a `show` con TkAgg y QtAgg. El barrido usa como referencia entera
independiente `1000I = 5h + 3n + 300 − 10t`: encuentra 946 combinaciones
exactamente en los umbrales entre 193819 combinaciones candidatas y exige
cero índices o clasificaciones incorrectos. `VALIDACION.md` distingue esta
suite de la comprobación adicional de ventanas Tk reales.

## Interpretación de la guía y uso de herramientas

El procedimiento y sus datos desarrollan un índice de lluvia, pero los
resultados esperados y preguntas de control mencionan crecimiento
exponencial, r y P₀. Se documenta esa inconsistencia y se sigue el procedimiento
de lluvia. Aunque el PDF también menciona Java y Python, el alcance acordado
para esta entrega es Python. No se implementa un simulador poblacional.

Se utilizó Codex para inspeccionar PDF y código, corregir precisión, organizar
clases MVC, implementar validaciones y gráficas, escribir y ejecutar pruebas,
actualizar documentación y crear los commits y pushes autorizados. No se
atribuye un porcentaje de autoría ni una política institucional no comprobada.
El estudiante debe revisar, comprender y poder explicar la solución.
`PROMPT.md` resume el encargo y `VALIDACION.md` registra lo verificado.
