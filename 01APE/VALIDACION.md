# Validación de APE 01

Revisión del 24 de octubre de 2026 (America/Guayaquil). Alcance: solamente
`01APE`. Se leyó el PDF completo mediante `pdftotext -layout`, los README y
el código inicial. No se encontraron AGENTS.md aplicables en la ruta ni
dentro de esta práctica.

## 1. Funcionalidad y arquitectura

Inicio real: raíz `APEs-Simulacion`, rama `main`, HEAD `f49636b`, remoto
`https://github.com/AndersonC15/Simulacion.git`. El árbol y el índice estaban
limpios; `git ls-remote --heads origin main` confirmó ese mismo HEAD remoto.

Se conservaron dos tablas de nueve registros, caso manual, dos imágenes y
menú 1/2/3/4/0. `main.py` solo construye y conecta los componentes. Modelo:
mediciones, pesos, resultados, validación y matemática. Vista: texto, tablas
y gráficas. Controlador: coordinación y recuperación. Hay objetos inmutables
de dominio y clases con comportamiento; no solo funciones movidas de carpeta.
Se aplican responsabilidad única e inyección de dependencias, sin jerarquías
artificiales. Las pruebas MVC verifican coordinación, ancho adaptable de
tablas y ausencia de llamadas a input/print/float en el modelo.

La guía mezcla lluvia con crecimiento exponencial, r y P₀. La solución sigue
el procedimiento de lluvia y el alcance Python solicitado; no inventa horas
ni implementa población o Java. El README explica la diferencia.

## 2. Exactitud matemática

Los 18 índices coinciden exactamente con la tabla de referencia del README.
También se comprobaron todos los factores tabulados, 15 °C → 0.75,
17 °C → 0.65, extremos térmicos y ambos juegos de pesos de suma exacta 1.
El ejemplo (90,80,18) produce 0.81.

Regresiones comprobadas en modelo y consola real:

| Humedad | Nubosidad | °C | Índice exacto | Clasificación |
|---:|---:|---:|---:|---|
| 35 | 35 | 18 | 0.40 | Baja posibilidad |
| 70 | 100 | 20 | 0.75 | Lluvia |

Se reprodujo la expresión anterior con float: 0.39999999999999997 y
0.7499999999999999. Al reconstruir el barrido anterior con `numpy.interp`
y esa expresión se reprodujeron **75 clasificaciones incorrectas de 946**.
La referencia independiente entera es `1000I = 5h + 3n + 300 − 10t`.
La suite recorre h,n enteros en [0,100] y t en [10,28], selecciona los 946
casos exactos en 0.40, 0.60 y 0.75 y verifica el índice con Fraction y su
categoría: **cero errores** con el modelo corregido.

Se prueban valores iguales, inferiores y superiores a los tres umbrales,
tanto en clasificación directa como en evaluación completa con diferencias
de humedad de 1e-100. Las referencias largas usan Fraction, no las funciones
evaluadas. Se verifican coeficientes de 120 dígitos, pesos de 120 dígitos,
contexto externo de precisión 2 y un índice 1e-242 con porcentaje 1e-240.
Los contextos por operación derivan su precisión y activan Inexact/Rounded;
no se usan redondeos ni tolerancias para clasificar.

## 3. Entradas y menú

Pruebas con 0/100 %, −50/60 °C, texto, vacío, espacios externos, punto,
coma, exponentes admitidos, signos, separadores mezclados/repetidos, espacios
internos, negativos inválidos, NaN/sNaN/Inf/Infinity, longitud excesiva y
exponentes fuera de política. Se exige un error claro y recuperación.
Las mismas validaciones se prueban construyendo registros directamente.
La consola conserva números de más de 28 dígitos sin recortarlos.

Se verificaron opciones inexistentes, repetición de tablas y casos manuales,
EOF/Ctrl+C en cada campo mediante simulación y **EOF/SIGINT en procesos
reales**. Los procesos terminaron con código 0 y sin traceback. SIGINT real
se prueba en POSIX; en otras plataformas esa prueba se omite explícitamente.

## 4. Gráficas

Desde el programa real:

```bash
printf '3\n3\n0\n' | MPLBACKEND=Agg python main.py
```

Se abrieron e inspeccionaron visualmente los dos PNG generados: curvas,
nueve horarios, títulos, ejes, leyendas y cuadrícula legibles; comparación
con líneas 0.40, 0.60 y 0.75. La suite también verifica las coordenadas
contra listas independientes y abre los PNG con Pillow para validar su formato.

Agg se verificó realmente sin ventanas. Una prueba adicional con TkAgg,
fuera de la suite, ejecutó el show real y su bucle de eventos: dos ventanas
confirmaron `winfo_ismapped() == True`; un callback las cerró tras un segundo.
Resultado: `Ventanas Tk realmente visibles: [True, True]`; backend final TkAgg
y ninguna figura pendiente. Se usó un script temporal de instrumentación,
sin sustituir el show real por una respuesta falsa.

También se ejecutó el menú sin DISPLAY ni WAYLAND_DISPLAY y solicitando
TkAgg: Matplotlib seleccionó agg, guardó ambas imágenes y el programa
explicó que no había ventanas. La ejecución del main real desde `/tmp`
guardó los PNG dentro del `01APE` real, no en el directorio de la terminal.

La decisión de llamar a show con TkAgg/QtAgg se comprueba además mediante
**simulación** sobre renderer Agg. Qt real no se comprobó: no hay PyQt6,
PySide6, PyQt5 ni PySide2 instalados. El registro real de Matplotlib sí
identifica Agg como estático y TkAgg/QtAgg como interactivos.

Se probaron repetición, cierre solo de figuras propias, directorio ocupado
por un archivo real, y fallos simulados de permisos, escritura, inicio de
backend y show. No se anuncia éxito al fallar el guardado; el menú continúa.

## 5. Instalación y ejecución final

El entorno `.venv` existente se conservó; inicialmente no tenía NumPy ni
Matplotlib y el programa no iniciaba por ModuleNotFoundError. Se crearon
entornos nuevos en `/tmp` y se instalaron las dependencias con pip sin
instalaciones globales. La instalación final se ejecutó sobre una copia
de esta práctica en `/tmp/ape01-instalacion-yzj8V7/01APE`, siguiendo la receta
Linux del README (`python3 -m venv .venv`, activación e instalación).

Python ejecutado: 3.14.4. Metadatos instalados: NumPy 2.5.3 requiere ≥3.12;
Matplotlib 3.11.2 requiere ≥3.11; contourpy 1.4.0 requiere ≥3.12. El mínimo
documentado es 3.12. No se ejecutaron Python 3.12 ni Windows/PowerShell.

Comandos de cierre desde `01APE`, con el entorno temporal activado:

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py Modelo Vista Controlador tests
python -m pip check
git diff --check
printf '1\n2\n3\n4\n90\n80\n18\n4\n35\n35\n18\n4\n70\n100\n20\n0\n' | MPLBACKEND=Agg python main.py
```

Resultados: 30 pruebas correctas; sintaxis/imports correctos; dependencias
sin conflictos; diff sin errores de espacios; sesión completa con dos
tablas, ambas gráficas, ejemplo y regresiones; salida normal con código 0.
Las pruebas de gráfica son temporales y la sesión real conserva los PNG.

## Evidencia de Git

Cada etapa se ejecutó y probó antes de su commit. Se revisaron diff e índice,
se añadieron rutas explícitas de `01APE` y se usó `git commit --only` con
esas rutas. No se empleó add global, commit -a, reescritura ni push forzado.
Se comprobó cada push normal con `git ls-remote --heads origin main`.

Las primeras cuatro etapas publicadas son dbe78db (precisión), 91e8ca0
(MVC), 4c53dac (entradas) y 10f2497 (gráficas). La quinta incluye este
registro, documentación y pruebas adicionales. Su hash y resultado de push
se informan en la entrega final, evitando registrar un hash autorreferente.
El historial y las rutas por commit se consultan con:

```bash
git log -5 --oneline
git log -5 --format='%h %s' --name-only
git status --short --branch
git ls-remote --heads origin main
```

Limitaciones: Qt real, Python 3.12 y Windows no ejecutados; no se ha medido
exactitud predictiva con lluvia observada. La suite y las pruebas descritas
no garantizan ausencia de cualquier error posible.
