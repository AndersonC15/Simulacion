# Guía de exposición — APE 07

Esta guía reúne lo que necesito explicar de mi proyecto: el modelo matemático, la generación de puntos, el código, los resultados y los comandos de demostración. Está basada en los archivos que conserva actualmente `07APE`.

## 1. Qué hice y qué quiero comparar

Implementé un experimento Monte Carlo para aproximar π en Python y Java. Genero puntos en un cuadrado, cuento cuántos pertenecen a un círculo inscrito y utilizo esa proporción para estimar π.

Comparo cuatro tamaños: 1 000, 10 000, 100 000 y 1 000 000 de puntos. Para cada tamaño obtengo la estimación, el error absoluto y los tiempos de ambos lenguajes.

El flujo del experimento es:

```text
Semilla → estados del LCG → valores normalizados → coordenadas
        → clasificación de puntos → conteo → estimación de π
```

Monte Carlo es el método de aproximación. El LCG proporciona los números pseudoaleatorios que utiliza el experimento.

## 2. De dónde sale el modelo matemático

Trabajo con un cuadrado de lado 2, centrado en el origen. Su área es 4. Dentro coloco un círculo de radio 1, también centrado en el origen; su área es π.

Si los puntos fueran uniformes e independientes en el cuadrado, la probabilidad de caer dentro del círculo sería la razón de áreas:

```text
P(dentro) = área del círculo / área del cuadrado = π / 4
```

Estimo esa probabilidad mediante el conteo observado:

```text
Nc / N ≈ π / 4
π estimado = 4 * Nc / N
```

`N` cuenta todos los puntos y `Nc` los interiores, incluyendo la frontera. El factor cuatro procede del área del cuadrado.

Para decidir si un punto pertenece al círculo utilizo:

```text
x*x + y*y <= 1
```

Esto equivale a exigir que su distancia al origen sea como máximo uno, sin calcular la raíz cuadrada.

| Punto | x² + y² | Clasificación |
|---|---:|---|
| (0, 0) | 0 | Interior |
| (0.5, 0.5) | 0.5 | Interior |
| (0.9, 0.9) | 1.62 | Exterior al círculo, dentro del cuadrado |
| (−1, 0) | 1 | Frontera; se cuenta |

La geometría admite esos casos de prueba. El LCG usado en el experimento produce normalizados estrictamente entre cero y uno; las fuentes controladas permiten probar también los extremos admitidos por el contrato.

## 3. Cómo funciona mi generador

LCG significa generador congruencial lineal. Su expresión general es:

```text
S(k+1) = (a*S(k) + c) mod m
```

Uso `S` para el estado entero del generador y reservo `x` e `y` para las coordenadas. Mi configuración es:

| Parámetro | Valor |
|---|---:|
| Multiplicador a | 16807 |
| Incremento c | 0 |
| Módulo m | 2147483647 |
| Semilla S0 | 123457 |

La recurrencia queda `S(k+1) = 16807*S(k) mod 2147483647`. El módulo obtiene el residuo de la división. Cada resultado se convierte en el estado que produce el siguiente.

La semilla determina dónde comienza la secuencia. Con la misma semilla y los mismos parámetros obtengo los mismos estados. Esta reproducibilidad permite comparar Python y Java.

Rechazo la semilla cero porque, al ser un generador multiplicativo, produciría cero indefinidamente. Admito semillas enteras entre 1 y 2147483646.

El generador es determinista. La coincidencia de resultados demuestra reproducción del cálculo; por sí sola no demuestra uniformidad ni independencia estadística.

## 4. Cómo convierto los números en puntos

Primero normalizo un estado:

```text
U = S / m
```

La división debe ser real. En Java se convierte el módulo a `double`. Después utilizo dos valores consecutivos:

```text
x = 2*U1 - 1
y = 2*U2 - 1
```

La transformación coloca las coordenadas en el cuadrado. El contrato de la fuente acepta `[0,1)` y la transformación corresponde a `[-1,1)` por eje; este LCG válido no produce los extremos cero o uno.

Cada punto necesita dos valores. Un millón de puntos consume dos millones de estados en una estimación. Las repeticiones, los calentamientos y la exportación recorren nuevamente la secuencia, por lo que el total de operaciones de una ejecución completa es mayor.

El primer punto real de la entrega se obtiene así:

```text
S1 = 2074941799        U1 ≈ 0.96622007
S2 = 559872160         U2 ≈ 0.26071079
x ≈ 0.93244014        y ≈ −0.47857842
x² + y² ≈ 1.09848192  → exterior
```

## 5. Qué hace cada componente del código

En Python, el paquete está en `python/src/ape07`. En Java, las clases están en `java/src/main/java/ec/edu/simulacion/ape07`.

| Componente | Responsabilidad |
|---|---|
| `Parametros` | Guarda la semilla y define las constantes del LCG. Valida la semilla. |
| `FuenteUniforme` | Define el contrato `siguiente()` para obtener un valor. |
| `GeneradorLCG` | Mantiene el estado, aplica la recurrencia y normaliza. |
| `Resultado` | Guarda puntos e interiores; calcula estimación y error a partir de ellos. |
| `EstimadorPi` | Valida N, consume dos valores por punto, transforma y cuenta interiores. |
| `Medicion` | Agrupa un resultado con las duraciones y calcula la mediana. |
| `MedidorRendimiento` | Realiza calentamientos, repeticiones y comprobación de reproducibilidad. |
| `ControladorExperimento` | Valida los tamaños, solicita las mediciones y coordina su presentación. |
| `VistaResultados` | Exporta archivos y muestra la tabla en consola. |

En Python, las clases del dominio están reunidas en `modelo.py`. Java tiene un archivo por clase o interfaz dentro de `modelo/`.

Los puntos de entrada son `__main__.py` y `App.java`: leen los argumentos, construyen los objetos y llaman al controlador. `__init__.py` identifica y describe el paquete Python.

Los parámetros y resultados se representan con `dataclass(frozen=True)` en Python y `record` en Java. Las mediciones guardan una tupla en Python y una copia no modificable de la lista en Java. El estado del generador sí cambia a medida que avanza.

Java utiliza `long` en el LCG para que el producto de estado por multiplicador quepa en su representación. Las coordenadas y estimaciones utilizan `double`; Python usa `float` para esas operaciones.

## 6. Cómo explico MVC y Strategy

MVC distribuye las responsabilidades:

| Capa | Python | Java | Trabajo |
|---|---|---|---|
| Modelo | `modelo.py` | `modelo/` | Generación, estimación y mediciones |
| Vista | `vista.py` | `vista/` | Consola y exportación |
| Controlador | `controlador.py` | `controlador/` | Validación de tamaños y coordinación |
| Composición | `__main__.py` | `App.java` | Argumentos y construcción de dependencias |

La vista regenera la secuencia para exportarla después de las mediciones. Esa tarea de exportación está fuera del intervalo cronometrado. Las gráficas y la comparación cruzada se realizan mediante herramientas adicionales.

Strategy permite que `EstimadorPi.estimar(puntos, fuente)` reciba una fuente intercambiable. En Python el contrato es un `Protocol`; en Java es una interfaz funcional.

En la ejecución se proporciona `GeneradorLCG`. En las pruebas de Python se utiliza `FuenteFija`, que entrega una secuencia controlada; Java utiliza funciones lambda para casos equivalentes. Así compruebo centro, borde y esquina sin modificar la clasificación del círculo.

La sustitución existe en el estimador. `MedidorRendimiento` construye actualmente el LCG y la CLI no permite seleccionar otros algoritmos. Para incorporar otra fuente a la ejecución habitual tendría que ajustar esa construcción.

Puedo defender el diseño así: «MVC separa cálculo, presentación y coordinación. Strategy me permite probar el estimador con diferentes fuentes de números manteniendo la misma geometría».

## 7. Cómo mido el tiempo

Para cada tamaño realizo tres calentamientos de `min(N, 10000)` puntos y cinco mediciones por defecto. Cada calentamiento y cada medición construyen un generador con la misma semilla.

Python mide con `perf_counter`; Java con `System.nanoTime`, convirtiendo la diferencia a segundos. El intervalo incluye la construcción inmediata del generador y la ejecución del estimador, con sus validaciones y creación del resultado. La estimación y el error se consultan después desde el objeto de resultado.

Quedan fuera del intervalo la compilación, los calentamientos, la consola, los archivos y las gráficas.

La mediana es el tiempo central de las duraciones ordenadas. Con cinco mediciones es el tercero. También conservo el mínimo y cada tiempo original. Las repeticiones comprueban rendimiento del mismo problema; no son cinco muestras estadísticas independientes.

Cada tamaño empieza con la misma semilla. Los casos de 1 000, 10 000, 100 000 y un millón son prefijos de una misma secuencia. El programa vuelve a calcular cada tamaño para medirlo por separado.

## 8. Cómo interpreto mis resultados

Estos valores proceden de `resultados/comparacion/tabla_guia.csv`:

| N | Interiores | π estimado | Error absoluto | Python (s) | Java (s) |
|---:|---:|---:|---:|---:|---:|
| 1 000 | 765 | 3.060000 | 0.08159265 | 0.00036424 | 0.00007351 |
| 10 000 | 7 850 | 3.140000 | 0.00159265 | 0.00402105 | 0.00063327 |
| 100 000 | 78 608 | 3.144320 | 0.00272735 | 0.03984748 | 0.00088667 |
| 1 000 000 | 785 969 | 3.143876 | 0.00228335 | 0.39313000 | 0.00649209 |

El error absoluto es `abs(pi_estimado - pi_referencia)`. Es una distancia, no un porcentaje. `math.pi` y `Math.PI` proporcionan la referencia de doble precisión; la clasificación de puntos no utiliza esa referencia.

La mejor aproximación de los cuatro casos ocurrió con 10 000 puntos. Al aumentar a 100 000, el error creció, y con un millón volvió a disminuir. Más puntos no garantizan un error menor en cada prefijo.

Bajo muestreo uniforme e independiente, la desviación estándar ideal del estimador escala como `1/sqrt(N)`. Reducirla aproximadamente a la mitad requiere cuatro veces los puntos. Esa tendencia no es una garantía para cada resultado ni certifica la calidad del LCG.

El costo del estimador es O(N): realiza un trabajo constante por punto. Su memoria adicional es constante respecto de N; la exportación de estados y el análisis completo ocupan espacio proporcional a N.

Java registró menores medianas en los datos conservados. La conclusión corresponde a estos programas y este entorno. El bucle medido de Python es Python ordinario; NumPy se usa después para analizar las secuencias y construir las gráficas.

## 9. Qué guarda cada archivo

| Archivo o carpeta | Uso |
|---|---|
| `resultados/python/` y `resultados/java/` | Resultados principales de cada lenguaje |
| `resumen.csv` | N, interiores, estimación, error, mediana, mínimo y repeticiones |
| `tiempos.csv` | Duraciones individuales: veinte por lenguaje con la configuración predeterminada |
| `primeros20.csv` | Estados, coordenadas y clasificación de hasta veinte puntos iniciales |
| `secuencia.bin` | Los 2N estados correspondientes al mayor tamaño |
| `entorno.json` | Lenguaje, versión, parámetros, protocolo y huella de la secuencia; Python añade datos del sistema |
| `resultados/comparacion/tabla_guia.csv` | Tabla consolidada Python/Java |
| `primeros20_comparados.csv` | Coordenadas iniciales de ambos programas para lectura |
| `convergencia.csv` | Estimaciones para prefijos intermedios |
| `puntos_convergencia.png` | Hasta 5 000 puntos y evolución de la estimación |
| `error_tiempos.png` | Error y tiempos de ambos lenguajes |
| `verificacion.json` | Resultado de la comparación completa |
| `resultados/demo_python/`, `demo_java/`, `demo_comparacion/` | Datos de demostración separados de los principales |
| `resultados/revision/` | Registros conservados de compilación, ejecución y verificaciones |

Cada estado binario ocupa cuatro bytes en orden big-endian. Dos millones de estados ocupan 8 000 000 de bytes por lenguaje. Los binarios se excluyen de Git y se regeneran ejecutando los programas.

La curva de referencia `1/√N` de la gráfica está anclada al primer error observado. Solo ilustra una forma de escala: no es una cota ni un intervalo de confianza.

## 10. Qué comprueba la comparación

`python/src/ape07/comparacion.py` contiene las funciones de verificación. `auditar()` revisa una carpeta; `comparar()` audita ambas, exige su igualdad y escribe una tabla conjunta y un JSON.

Comprueba parámetros, tamaños y repeticiones; longitud y SHA-256 del binario; recurrencia de todos los estados; reconstrucción de coordenadas e interiores; estimación y error para cada N; tiempos positivos y finitos; medianas y mínimos; y primeros puntos exportados.

El hash permite detectar cambios respecto de la huella registrada. Comprobar además la recurrencia permite rechazar una secuencia alterada aunque se haya actualizado su hash.

La igualdad se exige para todos los estados y resultados de este experimento. No basta con ver que ambos programas imprimen 3.14 o con comparar solamente las primeras filas.

## 11. Para qué sirve cada script

| Script | Qué hace | Consideración actual |
|---|---|---|
| `scripts/preparar.sh` | Comprueba herramientas, crea `.venv`, instala dependencias y el paquete editable; compila y prueba Java con Maven. | Necesita conexión para descargas que aún no estén disponibles. No instala un JDK. |
| `scripts/ejecutar.sh` | Empaqueta Java sin ejecutar sus pruebas, ejecuta ambos programas con valores predeterminados y llama a `entrega.py`. Guarda registros de compilación y ejecución. | Reemplaza los resultados principales. Su mensaje final todavía menciona generar informe y video, cuyos scripts ya no están. |
| `scripts/verificar.sh` | Ejecuta Maven/JUnit y unittest, guarda sus registros y llama a `entrega.py`. | Necesita resultados principales existentes para su última etapa. No vuelve a medir el experimento principal. |
| `scripts/entrega.py` | Compara los resultados principales y reconstruye tablas, convergencia y dos PNG mediante NumPy, Pandas y Matplotlib. | Sus rutas de entrada y salida están fijadas al proyecto. No genera el PDF ni el video. |
| `scripts/entregar.sh` | Encadena preparación, ejecución, pruebas, generación documental y auditoría. | El recorrido completo está incompleto: llama a `generar_informe.py` y `generar_video.py`, que fueron retirados. Puede reemplazar resultados antes de fallar. |
| `scripts/auditar_entrega.py` | Comprueba la antigua entrega completa: guía, secuencias, PDF, registros, análisis y video. | No funciona completo con la carpeta actual: faltan la guía original, los análisis y el video. El primer acceso a la guía ya falla. |

Los scripts Bash cambian al directorio del proyecto a partir de su ubicación. Los ejemplos individuales de esta guía se ejecutan desde `07APE`.

## 12. Para qué sirven los archivos de configuración y las carpetas auxiliares

| Elemento | Uso |
|---|---|
| `python/pyproject.toml` | Define el paquete instalable, Python >= 3.11 y el comando `ape07`. |
| `python/requirements.txt` | Declara rangos de dependencias. NumPy/Pandas/Matplotlib se usan en comparación y gráficas; ReportLab quedó de la generación del informe; imageio-ffmpeg se usa en la auditoría antigua del video. |
| `python/requirements-lock.txt` | Conserva las versiones exactas del entorno original. No es la lista que instala por defecto `preparar.sh`. |
| `java/pom.xml` | Configura Maven, compilación con release 21, JUnit y el JAR ejecutable `ape07.jar`. |
| `.gitignore` | Excluye entorno virtual, cachés, compilados y secuencias binarias, entre otros archivos generados. |
| `.venv/` | Intérprete y paquetes locales de Python; se recrea al preparar el proyecto. |
| `java/target/` | Clases, JAR e informes de pruebas generados por Maven. |
| `.cache/matplotlib/` | Caché que utilizan los scripts para Matplotlib. |
| `__pycache__/` y `*.egg-info/` | Caché de Python y metadatos de instalación, generados automáticamente. |
| `APE07-CoelloAnderson-U2-Simulacion.pdf` | Informe académico conservado de la ejecución original. |
| `README.md` | Instrucciones técnicas para instalar, ejecutar y revisar el proyecto. |

La ejecución Java usa clases del JDK; JUnit interviene en las pruebas. El cálculo central Python usa la biblioteca estándar. Las herramientas de comparación y gráficas requieren los paquetes adicionales.

## 13. Qué pruebas puedo explicar

`python/tests/test_qa.py` contiene diez campañas con subcasos. Algunas ejecutan de verdad el JAR, por lo que debe estar construido. Si falta, la suite falla en lugar de omitir la integración.

| Campaña | Qué comprueba |
|---|---|
| 01 | Estados conocidos y rangos con semillas extremas |
| 02 | Centro, frontera, esquina y consumo exacto de 2N valores |
| 03 | Semillas, tamaños y valores de fuente inválidos |
| 04 | Reproducibilidad con varias semillas |
| 05 | Catorce entradas inválidas por lenguaje y salida con código 2 |
| 06 | Comparación real, un solo punto y rutas con espacios |
| 07 | Estado alterado aun con hash actualizado y archivo truncado |
| 08 | Resúmenes, tiempos, coordenadas y metadatos manipulados |
| 09 | Ruta de salida incorrecta y medianas pares e impares |
| 10 | Ejecución de un millón de puntos con semilla máxima y comparación completa |

`java/src/test/java/ec/edu/simulacion/ape07/ModeloTest.java` añade diez pruebas: vector conocido, semillas y rangos, geometría, fuente y tamaños inválidos, reproducibilidad, millón de puntos con fuente controlada, mediana/inmutabilidad y repeticiones/reinicio.

Las pruebas verifican operaciones y contratos. No exigen que el error disminuya en todos los tamaños ni que un lenguaje gane siempre en tiempo.

## 14. Demostración en vivo

Desde `02Unidad` entro con `cd 07APE`. Si abro otra terminal, primero me sitúo en esa carpeta. Para una computadora nueva preparo el entorno:

```bash
bash scripts/preparar.sh
```

Para demostrar los cuatro tamaños con la misma configuración y conservar los resultados principales:

```bash
.venv/bin/python -m ape07 \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_python
```

```bash
java -jar java/target/ape07.jar \
  --semilla 123457 \
  --tamanos 1000,10000,100000,1000000 \
  --repeticiones 5 \
  --salida resultados/demo_java
```

Comparo esas carpetas con el mismo verificador:

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

La columna `coinciden` debe mostrar `True`. Este bloque genera tabla y JSON; las gráficas principales se generan con `scripts/entrega.py` a partir de las carpetas principales.

Para mostrar el código central abro `python/src/ape07/modelo.py`. Para mostrar una validación:

```bash
.venv/bin/python -m ape07 --tamanos 0
```

El mensaje de error y el código 2 son esperados. Para ejecutar las pruebas sin reconstruir las gráficas:

```bash
mvn -B -ntp -f java/pom.xml verify
.venv/bin/python -m unittest discover -s python/tests -v
```

En el escritorio Linux puedo abrir las evidencias conservadas:

```bash
xdg-open resultados/comparacion/puntos_convergencia.png
xdg-open resultados/comparacion/error_tiempos.png
xdg-open APE07-CoelloAnderson-U2-Simulacion.pdf
```

Al repetir una carpeta de salida se reemplazan sus archivos. Los conteos se reproducen con la misma configuración; los tiempos nuevos pueden diferir de los del PDF.

## 15. Preguntas que debo poder responder

| Pregunta | Respuesta que debo comprender |
|---|---|
| ¿Por qué multiplico por cuatro? | La razón de áreas es π/4 para el círculo y cuadrado elegidos. |
| ¿Cómo sé si un punto está dentro? | Compruebo `x²+y²<=1`. |
| ¿Por qué dos números por punto? | Cada punto requiere coordenadas x e y. |
| ¿Por qué uso una semilla? | Permite reproducir la secuencia y comparar los programas. |
| ¿Qué cambia si uso otra semilla? | Cambia la secuencia y pueden cambiar conteos y estimaciones. |
| ¿Qué tamaño dio mejor resultado? | 10 000 puntos en los cuatro casos conservados, con esta semilla. |
| ¿Más puntos siempre reducen el error? | No en cada prefijo; la reducción de variabilidad es una tendencia bajo los supuestos ideales. |
| ¿Qué mide el error? | La distancia absoluta a la referencia de π. |
| ¿Por qué coinciden los resultados? | Ambos programas aplican la misma recurrencia, normalización, orden y geometría. |
| ¿Por qué cambian los tiempos? | Las implementaciones, entornos de ejecución y condiciones de medición influyen. |
| ¿Para qué cinco repeticiones? | Para resumir rendimiento con una mediana; repiten el mismo problema. |
| ¿Qué aporta Strategy? | Permite suministrar otra fuente al estimador, incluidas fuentes controladas de prueba. |
| ¿Qué aporta MVC? | Separa dominio, presentación y coordinación. |
| ¿Qué aplicaciones tiene Monte Carlo? | Estimación de áreas, integración, probabilidades y escenarios con incertidumbre; aquí implementé π. |
| ¿Realicé pruebas estadísticas de uniformidad? | En este APE no; las pruebas de software y la coincidencia entre lenguajes no las sustituyen. |

## 16. Guion breve para practicar

«Mi práctica aproxima π mediante Monte Carlo. Utilizo un cuadrado de lado dos y un círculo inscrito de radio uno. Como sus áreas son cuatro y π, la proporción de puntos interiores aproxima π dividido para cuatro.

Genero los puntos con un LCG. Cada punto utiliza dos valores consecutivos, que normalizo y transformo en coordenadas. Compruebo si x al cuadrado más y al cuadrado es menor o igual que uno y acumulo los interiores.

Implementé el mismo procedimiento en Python y Java. Evalué cuatro tamaños de muestra y medí cinco veces cada tamaño, informando la mediana. Los resultados numéricos coincidieron; Java tuvo menores tiempos en las mediciones conservadas.

La mejor aproximación de esta ejecución ocurrió con diez mil puntos. Más puntos no obligan a que el error disminuya en cada prefijo.

Organicé el código con MVC y utilicé Strategy para que el estimador reciba su fuente de números. Las pruebas verifican la geometría, la reproducibilidad, las entradas y la coherencia de los archivos».

## 17. Estado actual de los documentos

El PDF permanece, pero conserva referencias a la guía original, documentos de análisis, una versión editable del informe y un video que ya no están en la carpeta. También fueron retirados los scripts que generaban el PDF y el video.

`entregar.sh` y `auditar_entrega.py` todavía dependen de parte de ese material. Por eso preparo la demostración con los comandos individuales anteriores y distingo la verificación del cálculo de la auditoría documental antigua. Un `auditoria_final.json` conservado describe una verificación anterior; no certifica la presencia actual de los archivos eliminados.

El PDF registra la aclaración de alcance Monte Carlo frente a la mención M/M/1 de la rúbrica. Actualmente puedo consultar esa explicación en el informe; la guía original ya no está disponible dentro de `07APE` para contrastarla de nuevo.
