# Validación de APE02 — 24 de octubre de 2026

Se inspeccionaron el repositorio real y la guía local de la semana 2. No se
recibieron diapositivas adicionales ni se afirma haberlas leído. Evidencia:
Linux x86_64, Python 3.14.4, NetLogo 7.0.4, pyNetLogo 0.5.2, JPype1 1.7.1 y
Java incorporado 17.0.2. Java del sistema: 21.0.12.1. No se promete haber
probado todas las entradas posibles.

## Resultado reproducible y conteo

Se creó `.venv-ape02` sin alterar el `.venv` existente. Después se creó otro
entorno vacío, `/tmp/ape02-instalacion-final`, y se instaló el manifiesto final
mediante su intérprete. Los `pip freeze` coincidieron y `pip check` no encontró
dependencias rotas. Hay 19 distribuciones necesarias para cálculos, gráficas,
puente y pruebas; pandas es dependencia real de pyNetLogo. No hay SciPy ni
paquetes de otras prácticas.

Comando final desde `02APE`, después de esa instalación nueva:

```bash
APE02_PROBAR_NETLOGO=1 \
NETLOGO_HOME="/ruta/real/NetLogo 7.0.4" \
MPLCONFIGDIR=/tmp/ape02-final-mpl MPLBACKEND=Agg \
/tmp/ape02-instalacion-final/bin/python -m pytest -q
```

La variable de ruta utilizó la instalación real detectada. Resultado:
**398 passed in 22.95s**, sin omisiones. Con el entorno activado se puede usar
`python` en lugar del intérprete temporal. `python -m pytest --collect-only -q`
recolectó exactamente 398 casos. Sin habilitar integración externa son
391 casos y 7 omisiones explícitas.

| Archivo | Casos o subcasos |
|---|---:|
| `tests/test_adversarios.py` | 257 |
| `tests/test_analisis.py` | 8 |
| `tests/test_base.py` | 7 |
| `tests/test_consola.py` | 62 |
| `tests/test_controlador.py` | 4 |
| `tests/test_estrategias.py` | 9 |
| `tests/test_graficas.py` | 4 |
| `tests/test_netlogo.py` | 45 |
| `tests/test_recursos.py` | 2 |
| **Total** | **398** |

Cada combinación parametrizada cuenta una vez; no se suman aserciones
internas. Hay regresiones pequeñas junto a cada algoritmo y un conjunto
independiente de referencias matemáticas y entradas adversas. No se cuentan
las cifras de un resultado como pruebas adicionales.

## Revisión 1: guía, arquitectura y funcionalidad

Se contrastaron PDF, requisitos explícitos, diez preguntas y código actual.
Un agente auxiliar efectuó una revisión de lectura independiente. Resultado:
cuatro ecuaciones y pseudocódigos, arreglo oficial, comparación, escenarios,
efecto de r y análisis de sigma presentes. No se implementó un simulador de colas.

`Modelo/` no importa vistas, imprime ni captura entradas. `main.py` contiene
la vista de consola. El controlador selecciona clases Strategy mediante un
contrato de una operación y conserva el experimento. Se revisaron separación
de responsabilidades, extensión e inyección de estrategias y contrato pequeño;
no se declara cumplimiento formal automático de los cinco principios SOLID.

Las pruebas verifican selección individual/común, modificación atómica de
parámetros y datos, escenarios, modo manual con ceros, invalidación y
reutilización de la misma realización para gráficas/NetLogo. Se añadió copia
defensiva de colecciones para que una lista externa no altere el experimento.

## Revisión 2: exactitud, aproximaciones y estabilidad

Se contrastaron las recurrencias con `Fraction`, independiente del cálculo
Decimal. Se verificaron 1100 para discreto, 1102.5 para Euler con dos medios
pasos, constancia con r=0, igualdad Euler(dt=1)/discreto y estocástico(sigma=0)/
discreto. El exponencial se contrastó con Decimal a 100 dígitos en la suite;
una revisión adicional usó 150 y encontró error absoluto aproximado 1.87e-47
para P0=1000, r=0.1, t=1 y precisión 50. La tolerancia de la suite es relativa
1e-48, con escala mínima 1; no se exige igualdad infinita de una aproximación.

Se comprobaron convergencia Euler en casos regulares, entradas largas y
contexto global con precisión 2. Las mallas incluyen ambos extremos,
horizonte cero, paso mayor, último paso reducido y límite de 10001 puntos.
Se rechazan factores Euler negativos incluso con diferencias minúsculas
respecto a cero. Las comparaciones no dependen del redondeo global.

La estimación usa las seis transiciones y desviación poblacional centrada de
residuos; los valores iniciales coinciden con README. El ruido controlado
comprueba la recurrencia, recorte a cero y recuperación posterior; un generador
controlado verifica sigma como desviación estándar. Se comprobó semilla
repetible y aislamiento de los estados globales NumPy/Python.

Se analizaron 30 semillas emparejadas, 42..71, por nivel sigma=0/base/2base.
Las desviaciones finales son 0, 90.562832952478617256218148821276556487810528590682
y 181.12566590495723451243629764255311297562105718136. La suite también usa
cinco realizaciones simétricas controladas. Se compara dispersión sin inferir
una tendencia universal de población; el recorte puede sesgar la distribución.

Fallo corregido: centrar con una media aproximada producía una desviación
minúscula ficticia para finales idénticas. Ahora media y varianza previas se
calculan como fracciones exactas; solo los resúmenes decimales y la raíz se
aproximan. Sigma=0 produce desviación exactamente cero.

## Revisión 3: entradas, recursos y recuperación

Se probaron vacío, espacios, texto, coma/punto decimal, formatos ambiguos,
NaN, infinitos, booleanos, float, negativos incompatibles, coeficientes y
exponentes extremos, arreglos vacíos/largos, datos insuficientes y divisores
cero, tanto por consola como mediante llamadas directas al dominio.

Los puntos se limitan antes de reservar las mallas; operaciones exactas
rechazan más de 10000 dígitos y cada serie admite hasta 2000000 dígitos
almacenados. Dos pruebas provocan esos límites con recurrencias reales.
También se rechazan rangos y exponentes inválidos sin ceros ficticios.

Se comprobó recuperación tras opciones inexistentes, configuración inválida,
errores de gráficos y puente; EOF real y Ctrl+C inyectado en varias lecturas.
Una prueba POSIX envía SIGINT real al proceso esperando una opción y exige
salida 0 sin traceback. Se verificaron rutas con espacios, destinos existentes,
directorio que es archivo, permisos reales de solo lectura, generación repetida
y cierre de figuras ante fallos. Errores CLI esperados dan mensaje y código 1.

Fallos corregidos:

- `str(10**5000)` fallaba antes de validar: se limita el entero previamente.
- La precisión aproximada mayor que los 80 dígitos admitidos para parámetros
  era incompatible con estimación: ahora la configuración es de 32 a 80.
- Se validan el objeto de parámetros y el ruido inyectado no invocable.
- Se añadió manejo de errores en arranque CLI, además del menú.
- Gráficas y NetLogo rechazan tiempos Decimal distintos que se fusionarían
  al convertirlos a float/double.

## Revisión 4: gráficas e integración real con NetLogo

Comandos de ejecución comprobados (también desde la instalación nueva para
escenarios y análisis; la suite limpia ejecutó el CLI de gráficas):

```bash
MPLBACKEND=Agg python main.py --comparar --graficas
MPLBACKEND=Agg python main.py --escenarios
python main.py --analizar-ruido
python main.py --netlogo --salida resultados
```

Se inspeccionó la comparación PNG: cuatro series, observaciones con cruces,
escalones discretos, etiqueta Euler aproximación, título, ejes, leyenda y
cuadrícula. Los escenarios conservan condiciones comunes salvo r/sigma.
El CSV conserva todos los valores Decimal. Se verificó igualdad binaria de
PNG al regenerar el mismo experimento.

Se abrió una ventana Matplotlib **real TkAgg** y un temporizador la cerró
tras mostrarse; terminó con cero figuras abiertas. Es una prueba adicional
a Agg y a los dobles usados en algunas pruebas de menú.

El puente real carga `netlogo/poblacion.nlogox`, envía parámetros y series,
ejecuta `representar` y consulta/compara todos los datos de retorno. El
experimento oficial produjo longitudes **(61,7,7,61)**, retorno verificado y
**0 tortugas**. Se probó repetición sin regenerar ruido, modelo inválido, JVM
inexistente, timeout, salida existente, horizonte cero y rutas con espacios.
Las 45 pruebas del puente pasaron también por separado.

Se probó la **ventana real de NetLogo** con el experimento oficial, se exportó
e inspeccionó `resultados/netlogo_oficial.png` y se comprobó cierre del proceso.
Sus finales double fueron aproximadamente 2204.7319003329753,
2101.5690404470874, 2048.8231193448173 y 2193.377096961199. Son valores de
visualización y no sustituyen los cálculos originales.

Fallos externos corregidos: pyNetLogo 0.5.2 convierte mal listas anidadas de
longitudes diferentes y listas vacías; se consultan series y observaciones
por separado. La firma instalada usa `jvmargs`. El cierre gráfico se bloqueaba
en `Frame.dispose()`; el worker GUI guarda/cierra la respuesta y termina su
proceso aislado, liberando ventanas/JVM. Headless cierra workspace y JVM
normalmente. Cada envío puede repetirse en un proceso nuevo.

El sandbox impidió inicialmente red para pip y escritorio para AWT. Se
repitieron con acceso revisado/autorizado y funcionaron. No se confunden
problemas de acceso con cálculos incorrectos.

## Revisión 5: instalación, documentación, ejecución e historial

Comandos adicionales ejecutados desde el entorno limpio:

```bash
python -m pip check
python -m pip freeze
python -m compileall -q main.py Modelo Controlador Vista tests
python main.py --help
git diff --check
```

Instalación y ejecución completa correctas. Freeze final coincide con
requirements.txt. NumPy 2.5.4 y contourpy 1.4.0 exigen Python ≥3.12 según
metadatos; se ejecutó realmente 3.14.4, no se certifica una ejecución en 3.12.
Se revisaron README de proyecto/carpetas, ecuaciones, preguntas, parámetros,
fuentes y declaración real de IA. PROMPT.md conserva el encargo íntegro.

Git inicial: raíz `APEs-Simulacion`, rama `main`, origin
`https://github.com/AndersonC15/Simulacion.git`, HEAD `7816c84`, índice vacío,
sin cambios rastreados. Existían `APE04_Java_NetLogo/` y `APE04_Java_NetLogo_QA.zip`
sin seguimiento y se conservaron. Cada avance se preparó con rutas explícitas,
revisión de diferencias y comprobaciones relevantes. Los diez commits de
APE02 se separan del commit de documentación/manifiestos del portafolio.
La entrega final informa hashes, pushes y estado después del último commit;
este documento no anticipa el hash del commit que lo contiene.

## Pendientes y alcance

No quedan comprobaciones pendientes de cálculo, instalación o puente real en
el Linux y las versiones enumeradas. No se probaron Windows, macOS, otro
NetLogo, un Python 3.12 instalado ni todos los toolkits gráficos. No se promete
compatibilidad universal, validación científica del ajuste ni ausencia total
de errores. Exp, estimación, raíces, Euler, generador normal y conversiones
visuales tienen las aproximaciones documentadas. El estudiante debe revisar
y poder explicar la implementación y el apoyo real de IA antes de entregar.
