# APE02 — Comparación de modelos determinísticos, estocásticos, discretos y continuos

Esta práctica compara cuatro formulaciones del crecimiento poblacional con
los datos y pseudocódigos de la [guía local de la semana 2](ape_guia%20simulacion%20semana%202-firmado-signed.pdf).
Python calcula las series; Matplotlib presenta comparaciones y NetLogo recibe
el mismo experimento mediante pyNetLogo para visualizarlo.

Tiempo, aleatoriedad y forma de evolución son dimensiones distintas: la
recurrencia discreta de esta práctica es determinística y el modelo
estocástico también avanza por períodos. La ecuación diferencial es continua
matemáticamente; Euler la aproxima con pasos discretos. Los cuatro nombres
no representan categorías mutuamente excluyentes.

## Tecnologías y requisitos

- Python ≥3.12 para las versiones fijadas de las dependencias; se comprobó
  Python 3.14.4 en Linux. El mínimo se deriva de metadatos de paquetes, no de
  una ejecución de esta práctica en Python 3.12.
- `decimal`, `fractions`, clases de datos y `typing.Protocol`, incluidos en
  Python: dominio, precisión, mallas y contrato Strategy.
- NumPy: generador normal pseudoaleatorio local; Matplotlib: gráficas y PNG.
- pyNetLogo, importado como `pynetlogo`: comunicación con NetLogo. JPype inicia
  la JVM; pandas es una dependencia del puente. No se incorporan cálculos
  artificiales para utilizar pandas o SciPy; SciPy no es necesaria aquí.
- pytest: pruebas automatizadas; el manifiesto final incluye sus dependencias
  y las transitivas obtenidas desde un entorno limpio.
- NetLogo y Java: instalaciones externas, no paquetes instalables por pip.
  El puente se comprobó con NetLogo 7.0.4, su Java incorporado 17.0.2 y
  pyNetLogo 0.5.2, en Linux x86_64. Los detalles de la comprobación real
  están en [VALIDACION.md](VALIDACION.md).

## Instalar y ejecutar

Desde la raíz del repositorio, entra en `02APE`. Crea un entorno propio y
utiliza siempre su intérprete:

```bash
cd 02APE
python3 -m venv .venv-ape02
source .venv-ape02/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python main.py
```

Si ya existe el entorno, actívalo sin recrearlo. Para salir: `deactivate`.
Las dependencias están fijadas en [requirements.txt](requirements.txt), que
incluye las versiones resueltas del entorno de esta práctica. No instales
este manifiesto sobre el entorno de otra APE.

En Windows PowerShell se puede utilizar el intérprete sin activar el entorno:

```powershell
py -3.12 -m venv .venv-ape02
.\.venv-ape02\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-ape02\Scripts\python.exe main.py
```

La receta Windows se ofrece como instrucción; su ejecución no se certifica
con las pruebas Linux. Sustituye `3.12` por una versión compatible instalada.

Comparación inicial, sin interacción:

```bash
python main.py --comparar --graficas
```

Escenarios comparables y una ruta de salida que puede contener espacios:

```bash
MPLBACKEND=Agg python main.py --escenarios --salida "/tmp/APE02 resultados"
python main.py --escenario decrecimiento --comparar --graficas
python main.py --help
```

`--mostrar` solicita ventanas cuando hay backend interactivo. Para generar
archivos sin escritorio usa Agg. La aplicación elige Agg en Linux cuando no
hay `DISPLAY` ni `WAYLAND_DISPLAY`. Los archivos se pueden generar sin NetLogo.

## Datos y parámetros iniciales

La guía proporciona `[1000, 1100, 1250, 1400, 1600, 1850, 2100]`. Se conservan
como observaciones de referencia en los períodos `0, 1, 2, 3, 4, 5, 6`; no se
suponen años, meses o días. No son siete condiciones iniciales ni resultados
que el simulador deba copiar. El valor inicial es `P0=1000` y el horizonte
inicial es de seis períodos.

La guía no fija cómo estimar parámetros. Esta implementación utiliza las
seis transiciones de las siete observaciones:

```text
r = (1/n) × suma((datos[i+1] - datos[i]) / datos[i]), n = 6
residuo[i] = datos[i+1] - (1+r) × datos[i]
media_residuo = suma(residuo[i]) / n
sigma = raíz(suma((residuo[i] - media_residuo)²) / n)
```

Se usa la desviación estándar **poblacional centrada**, con divisor n, no
n−1, como medida descriptiva. La media de residuos puede ser distinta de cero;
estimar su dispersión no valida una hipótesis de ruido normal centrado ni
una calibración científica. `sigma` es desviación estándar, no varianza.

Con precisión de aproximación 50, la configuración inicial muestra:

```text
p0 = 1000
tasa = 0.13176765239265239265239265239265239265239265239265
sigma = 22.368045617048172851535305682312036142656574707769
dt = 0.1
horizonte = 6
semilla = 42
precision = 50
```

`dt=0.1`, semilla 42 y precisión 50 son decisiones de implementación,
no valores oficiales. La estimación aproxima divisiones y raíz con Decimal,
utilizando 20 dígitos de guarda antes de obtener los parámetros a la precisión
solicitada. Las tasas y residuos usan todos los datos.

El dominio también conserva `Parametros()` como configuración manual
predefinida: P0=1000, r=0.1, sigma=0, dt=0.1, horizonte=6, semilla=42 y
precisión=50. El controlador normal comienza con la estimación del arreglo.

## Ecuaciones y correspondencia con el pseudocódigo

| Estrategia | Regla de la guía | Implementación |
|---|---|---|
| Determinística exponencial | `P(t)=P0 × exp(r×t)` | Recorre la malla y calcula cada población desde P0; no usa una recurrencia ni ruido. |
| Discreta | `P[k+1]=P[k]+r×P[k]` | Guarda P0 y agrega un estado por período. |
| Estocástica | `P[k+1]=max(0,P[k]+r×P[k]+epsilon[k])` | Genera ruido normal, actualiza y aplica la restricción a cero del pseudocódigo. |
| Continua aproximada con Euler | `dP/dt=rP`; `P(t+h)=P(t)+h×r×P(t)` | Guarda P0 y aplica el incremento con el paso real de cada intervalo. |

En el modelo estocástico, `epsilon ~ Normal(0,sigma²)`. Se genera una normal
estándar con NumPy y se multiplica por sigma; no se pasa sigma² como desviación
estándar. La restricción a cero solo se aplica al estocástico. Con ruido
aditivo una población que llegó a cero puede volver a aumentar.

Las clases están en [Modelo/estrategias.py](Modelo/estrategias.py). El
controlador ejecuta las cuatro estrategias con los mismos parámetros, guarda
sus series y entrega ese experimento a las vistas. Esto implementa el
pseudocódigo de comparación sin recalcular ruido al presentar una gráfica o
al enviarla a NetLogo.

El mismo número r tiene interpretaciones distintas: en la exponencial es una
tasa instantánea, mientras que en la recurrencia es un aumento relativo por
período. En general `exp(r)` difiere de `1+r`; por eso las curvas no tienen que
coincidir. Con r=0.1, P0=1000 y un período, la recurrencia termina en 1100,
Euler con h=0.5 en 1102.5 y la exponencial aproximadamente en
1105.1709180756476… . No se redondean estos resultados para calcular los
siguientes estados.

## Uso del menú y nuevos datos

El menú permite ejecutar cada modelo, comparar, consultar datos y parámetros,
modificarlos, elegir escenario, cambiar el arreglo, graficar y utilizar el
puente NetLogo. La opción `a` ejecuta el análisis de ruido con varias semillas. La opción 6 muestra la configuración real; la opción 7 permite
cambiar sus campos y conservar un valor con Enter. Los errores de entrada se
informan y permiten continuar. EOF y Ctrl+C cierran el menú.

Para un arreglo utiliza punto y coma entre observaciones:

```text
[1000;1100,25;1250.5]
```

Los corchetes son opcionales. El punto o la coma representan el separador
decimal; la coma no separa elementos ni miles. No se utiliza `eval()`.

El modo automático requiere al menos dos observaciones y prohíbe divisores
cero en las tasas relativas. Ante datos insuficientes o ceros intermedios se
puede elegir modo manual: conserva r, sigma, dt, semilla y precisión, toma
P0 del primer dato y ajusta el horizonte a `n−1`. Un único dato corresponde a
horizonte cero. Al cambiar datos o parámetros se invalida el experimento
anterior; la siguiente ejecución construye uno nuevo.

## Crecimiento, decrecimiento y aleatoriedad

Los escenarios de demostración conservan P0, horizonte, dt, semilla y
precisión de la configuración, y cambian r y sigma:

| Escenario | r | sigma | Propósito |
|---|---:|---:|---|
| crecimiento | 0.1 | 0 | Comparar el aumento y el efecto del método. |
| decrecimiento | −0.1 | 0 | Comparar el descenso con un paso Euler positivo. |
| constante | 0 | 0 | Comprobar conservación de la población inicial. |

Son decisiones de implementación. Se elimina el ruido en estos escenarios
para observar el efecto de r: el estocástico con sigma=0 coincide con el
discreto. El arreglo de referencia sigue visible; no se presenta como una
observación de decrecimiento cuando sus datos originales aumentan.

Para estudiar sigma se necesitan varias realizaciones controladas:

```bash
python main.py --analizar-ruido
```

`Modelo/analisis.py` compara sigma=0, sigma_base y 2×sigma_base con 30
realizaciones por nivel, usando las mismas semillas en cada nivel. Se parte
de la semilla configurada y se avanza una por realización, dentro de 64 bits.
Si la configuración tiene sigma=0 se adopta sigma_base=1 para evitar tres
niveles idénticos. La API admite entre 2 y 100 réplicas por nivel y limita el
horizonte a 100 períodos. Las medias y desviaciones poblacionales de los
valores finales son aproximaciones Decimal con la precisión configurada y
20 dígitos de guarda. La media y varianza previas se calculan como fracciones
exactas; así, resultados idénticos tienen varianza y desviación exactamente cero.

En la ejecución inicial con las semillas 42..71, las desviaciones finales
calculadas fueron:

| Nivel | Desviación poblacional de las 30 poblaciones finales |
|---|---|
| sigma=0 | 0 |
| sigma_base estimada | 90.562832952478617256218148821276556487810528590682 |
| 2×sigma_base | 181.12566590495723451243629764255311297562105718136 |

Estas son cifras aproximadas de este experimento reproducible, no una ley
que obligue a duplicar la dispersión cuando actúa la restricción a cero.
Una sola curva no demuestra que más ruido aumente o disminuya la población.
Las semillas emparejadas facilitan comparar niveles de ruido, pero esta
exploración no constituye una validación estadística exhaustiva. Consulta
[VALIDACION.md](VALIDACION.md) para los resultados comprobados.

## MVC, POO, Strategy y SOLID

- `Modelo/` conserva datos, parámetros, validación, estimación, mallas y las
  ecuaciones. No imprime, captura entradas, importa vistas ni abre ventanas.
- `Controlador/` coordina estrategias y mantiene el experimento calculado.
- `main.py` es la **vista de consola y el arranque**: menú, lectura y tablas.
  `Vista/` adapta resultados a gráficas y NetLogo.
- `Parametros`, `Serie` y `Experimento` son objetos de datos inmutables. Cada
  estrategia es una clase que implementa `simular(parametros)`.

`EstrategiaSimulacion` es un `Protocol` pequeño. El controlador selecciona la
estrategia por nombre o ejecuta todas mediante el mismo contrato. Se pueden
inyectar otras estrategias y un ruido controlado en las pruebas, sin añadir
fábricas o jerarquías decorativas.

Se aplican responsabilidades separadas (S), extensión mediante estrategias
(O) e inyección de esas estrategias en el controlador (D). El contrato de
una operación evita exigir métodos ajenos a cada algoritmo (I). Las pruebas
comprueban que cada estrategia devuelve una `Serie` válida; no se declara
cumplimiento formal de los cinco principios por tener carpetas o clases.

## Precisión, estabilidad y límites

Las entradas se convierten directamente de texto a Decimal. El dominio
admite texto, enteros o Decimal; rechaza float y booleanos para evitar una
conversión binaria previa. No utiliza redondeo de presentación, `round()`,
`quantize()` ni conversiones a entero para calcular poblaciones.

Las sumas y productos decimales finitos utilizan contextos locales de tamaño
adaptativo y trampas `Inexact`/`Rounded`: se calcula sin pérdida dentro del
límite o se devuelve un error. Las divisiones de estimación, la raíz y `exp`
son aproximaciones con precisión documentada. Multiplicar exactamente una
exponencial aproximada no convierte la solución en exacta.

NumPy utiliza precisión finita para la normal. Cada simulación crea
`default_rng(semilla)` sin modificar el generador global; el valor generado
se incorpora mediante su representación decimal y no recupera precisión
binaria perdida. La aritmética posterior conserva ese valor aproximado.
Las conversiones a float para Matplotlib y a double para NetLogo están en
`Vista/`; esos valores nunca regresan al modelo para continuar cálculos.

Límites deliberados de recursos:

| Concepto | Límite o condición |
|---|---|
| Número de entrada | Hasta 256 caracteres, 80 dígitos en el coeficiente y exponentes escrito/interno entre −100 y 100. |
| Arreglo | Entre 1 y 10001 observaciones; texto completo hasta 100000 caracteres. |
| Aproximaciones | Precisión configurable de 32 a 80 dígitos; inicialmente 50. |
| Aritmética exacta | Hasta 10000 dígitos requeridos por operación o resultado. |
| Resultado no nulo | Exponente decimal ajustado entre −250 y 250. |
| Exponencial | `abs(r×t) ≤ 500`. |
| Horizonte | Entre 0 y 10000 períodos; entero para discreto y estocástico. |
| Malla | Como máximo 10001 puntos, comprobados antes de reservarla. |
| Almacenamiento por serie | Hasta 2000000 dígitos de coeficientes de población; se comprueba durante el cálculo. |
| Parámetros | P0 y sigma no negativos; dt positivo; todos finitos. Semilla entera entre 0 y 2⁶⁴−1. |

Las cotas acotan recursos; no garantizan que toda combinación dentro de los
límites individuales pueda simularse. Por ejemplo, muchas multiplicaciones
con parámetros largos pueden alcanzar la cota de 10000 dígitos. En ese caso
se rechaza el cálculo con un mensaje, sin recortar resultados.

La malla se construye con índices enteros y cocientes racionales, sin sumar
dt reiteradamente. Incluye 0 y el horizonte; Euler reduce el último paso si
no cabe un paso completo. Si dt supera el horizonte se usa un solo paso final;
con horizonte cero se devuelve únicamente P0. Los tiempos son crecientes y
las longitudes coinciden.

Para varios períodos, el discreto requiere r≥−1. Euler comprueba
`1+h×r ≥ 0` en cada paso real: para decrecimiento esto evita valores negativos
y oscilaciones por el paso. No se arreglan con ceros ficticios. Reducir dt
acerca Euler a la exponencial en casos regulares; dt=1 coincide con la
recurrencia discreta en los mismos períodos. Los desbordamientos, resultados
no finitos y rangos incompatibles producen errores comprensibles.

La consola presenta una tabla de extremos de cada serie sin formatos `.2f`
o `.3f`; los CSV guardan todos los puntos como texto Decimal. Un resultado
exacto de una recurrencia puede contener muchos dígitos. El CSV es más cómodo
para inspeccionarlos; no se reutiliza como entrada de cálculo.

## NetLogo desde Python

NetLogo se utiliza como visualizador de las series ya calculadas. Se envían
los parámetros, tiempos, poblaciones y observaciones; no se genera otra
trayectoria aleatoria ni un agente por habitante. La representación usa
curvas y cero tortugas. Mantén juntos los archivos de [netlogo/](netlogo/README.md).

Configura la ruta de instalación, sin confundirla con el lanzador:

```bash
export NETLOGO_HOME="/ruta/NetLogo 7.0.4"
```

El adaptador también permite una ruta explícita. Si hay varias instalaciones,
selecciona una mediante esta variable. El worker busca primero la JVM incluida
en NetLogo; `NETLOGO_JVM_PATH` permite indicar su biblioteca JVM cuando haga
falta. No se fija una ruta privada como único método de configuración.

Desde la consola se puede enviar la comparación y exportar el plot real:

```bash
python main.py --netlogo --salida resultados
python main.py --netlogo-home "/otra/ruta/NetLogo 7.0.4" --netlogo
```

La opción 11 del menú envía el experimento conservado. Los archivos exportados
por NetLogo tienen un identificador en el nombre para conservar ejecuciones
anteriores. El CSV del plot NetLogo no sustituye el puente: se carga el
modelo, se ejecutan comandos y se consultan los datos de vuelta.

Ejemplo con la API real, desde `02APE` y con el entorno activado:

```python
from Controlador.simulacion import ControladorSimulacion
from Vista.puente_netlogo import PuenteNetLogo

controlador = ControladorSimulacion()
experimento = controlador.ejecutar()
informe = PuenteNetLogo().enviar(experimento)
print(informe)
```

`PuenteNetLogo.enviar` recibe el experimento existente. El subproceso carga
realmente el modelo, ejecuta comandos y consulta sus datos mediante reporters.
El proceso principal compara las series y parámetros recuperados con los
enviados. La igualdad se comprueba después de la conversión de transporte;
no representa exactitud Decimal infinita dentro de NetLogo.

Cada envío utiliza un proceso auxiliar con su propia JVM, para evitar
intentar reiniciar JPype dentro del mismo proceso. En modo sin ventana se
cierra el workspace y la JVM. La GUI de pyNetLogo 0.5.2 se bloqueó al cerrar
`Frame.dispose()`; se corrigió finalizando su proceso aislado después de
escribir la respuesta. El sistema libera la JVM y sus ventanas; esta decisión
y su prueba real se describen en [netlogo/README.md](netlogo/README.md). Hay límite de
90 segundos por defecto, configurable hasta 300, y memoria JVM máxima de
768 MiB de heap. El transporte admite hasta 100000 puntos totales. Se detectan instalación ausente, rutas erróneas, modelo inválido,
fallos de arranque/cierre y tiempo agotado. Python y las gráficas siguen
funcionando aunque NetLogo no esté disponible.

Para solicitar ventana usa `python main.py --netlogo-gui`, o `gui=True` en
la API; requiere
escritorio y permanece abierta un intervalo acotado, inicialmente cinco
segundos. `salida_plot` exporta un gráfico NetLogo y `salida_interfaz` requiere
GUI; se rechazan archivos de salida ya existentes. El informe devuelve las
versiones reales y el resultado de comunicación. Consulta
[VALIDACION.md](VALIDACION.md) para distinguir el puente real, los casos
simulados y el alcance de las comprobaciones gráficas. En Linux se probó
Matplotlib con TkAgg real y con Agg, y NetLogo tanto sin ventana como con
interfaz real. Windows, macOS y otras versiones NetLogo quedan sin comprobar.

## Resultados, estructura y pruebas

Las salidas por defecto están en [resultados/](resultados/README.md):
`comparacion.png/.csv` y, con `--escenarios`, pares
`crecimiento`, `decrecimiento` y `constante`. Los envíos CLI a NetLogo exportan
`netlogo-<identificador>.csv` y, con GUI, su PNG de interfaz; el ejemplo
validado de interfaz se encuentra en `resultados/netlogo_oficial.png`.
PNG y CSV de Matplotlib se reemplazan mediante
archivos temporales al repetir el mismo nombre. No existe una transacción
conjunta entre ambos: un fallo posterior al PNG puede dejar ese PNG y el CSV
anterior. Las figuras se cierran en `finally`.

```text
02APE/
├── Modelo/          # Dominio, estimación, precisión, tiempo y estrategias
├── Controlador/     # Coordinación y conservación del experimento
├── Vista/           # Gráficas y puente/proceso auxiliar NetLogo
├── netlogo/         # Modelo visualizador y documentación
├── tests/           # Matemática, entradas, consola, gráficas y puente
├── resultados/      # PNG y CSV regenerables
├── main.py          # Vista de consola y arranque
├── requirements.txt
├── PROMPT.md         # Encargo y uso real de IA
└── VALIDACION.md     # Cinco revisiones y evidencia de comandos/resultados
```

Desde `02APE`, con su entorno activado:

```bash
python -m pytest -q
python -m pytest --collect-only -q
python -m compileall -q main.py Modelo Controlador Vista tests
python -m pip check
```

Los casos parametrizados se cuentan como subcasos distintos; las aserciones
internas no se suman para inflar la cantidad. El resultado final, cantidad
comprobada, comandos de integración real y cinco revisiones se registran en
[VALIDACION.md](VALIDACION.md), no se deducen del tamaño del código. Consulta
[tests/README.md](tests/README.md) para el alcance de cada archivo de pruebas.

## Preguntas de control de la guía

1. **¿Qué representa el arreglo de entrada?** Observaciones de población en
   períodos consecutivos. Aquí sirven como referencia y para estimar los
   parámetros iniciales; el primer dato determina P0.
2. **¿Qué diferencia al determinístico del estocástico?** Con los mismos
   parámetros el primero aplica una regla sin ruido. El segundo incorpora
   perturbaciones normales; una semilla fija permite reproducirlas.
3. **¿Qué efecto produce modificar r?** r positiva produce crecimiento en
   los modelos sin ruido; r=0 conserva población y r negativa produce
   decrecimiento con condiciones numéricas válidas. El ruido puede alterar
   el aumento o descenso de una trayectoria particular.
4. **¿Qué representa sigma?** La desviación estándar del ruido aditivo por
   período, expresada en unidades de población; su cuadrado es la varianza.
5. **¿Qué ocurre cuando aumenta el ruido?** Aumenta la dispersión introducida
   por las perturbaciones. Debe analizarse con varias realizaciones; la
   restricción a cero también puede afectar la distribución final.
6. **¿Qué diferencia al discreto del continuo?** El primero actualiza por
   períodos; la ecuación continua define una derivada en el tiempo. Euler
   aproxima esa ecuación con una malla, sin convertirla en una solución exacta.
7. **¿Qué función cumple dt?** Es el paso numérico de Euler y de la malla
   de presentación exponencial. Un paso menor suele reducir el error de Euler
   y aumenta el trabajo; no cambia el período de los modelos discreto y estocástico.
8. **¿Por qué visualizar con gráficas?** Permite comparar tendencias, ruido
   y separación entre métodos. Las observaciones usan cruces y las series
   estilos distintos; la gráfica complementa los valores, no demuestra validez científica.
9. **¿Qué modelo presenta aleatoriedad?** La estrategia `Estocastico`, cuando
   sigma>0. Con sigma=0 coincide con la recurrencia discreta en condiciones válidas.
10. **¿Qué cambia con un nuevo arreglo?** Cambian las observaciones, P0 y el
    horizonte. En modo automático se recalculan r y sigma con todas las
    transiciones; en manual se conservan los demás parámetros seleccionados.

## Problemas frecuentes, límites verificados y uso de IA

- Un import ausente suele indicar otro intérprete: activa el entorno y usa
  `python -m pip install -r requirements.txt` con ese mismo Python.
- Si no aparecen ventanas, comprueba el escritorio y el backend. Agg genera
  archivos sin ventanas; una prueba con Agg no acredita una ventana real.
- Un horizonte fraccionario sirve para exponencial/Euler, pero impide comparar
  las cuatro estrategias periódicas; usa un horizonte entero para esa comparación.
- Si Euler rechaza decrecimiento, reduce dt hasta que cada `1+h*r` sea no
  negativo. Si se exceden puntos, dígitos o rango, reduce el tamaño del
  experimento; el programa no redondea para aceptar la entrada.
- Si un arreglo no permite estimar, selecciona modo manual con parámetros
  válidos. Si una salida no puede escribirse, revisa permisos y el directorio.
- NetLogo ausente o una JVM incompatible no impiden las simulaciones Python.
  Revisa instalación, `NETLOGO_HOME`, JVM y [netlogo/README.md](netlogo/README.md).

Se utilizó Codex para inspeccionar la guía y el repositorio, implementar y
revisar el programa, diseñar y ejecutar pruebas y preparar documentación y
manifiestos. [PROMPT.md](PROMPT.md) registra el encargo y las instrucciones
realmente utilizadas; [VALIDACION.md](VALIDACION.md) distingue lo ejecutado de
lo pendiente. No se afirma haber leído diapositivas que no estén disponibles,
ni se declara una nota o porcentaje de autoría de IA. El estudiante debe
revisar y poder explicar las decisiones y el código antes de entregar.
