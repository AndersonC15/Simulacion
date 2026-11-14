# Guía para defender el APE 07

La defensa oral vale cuatro puntos en la rúbrica. Este guion permite preparar
una explicación personal y ejecutar el código frente al docente.

## Explicación del estudiante

«Mi práctica aproxima π mediante Monte Carlo. Genero puntos pseudoaleatorios
en un cuadrado de lado dos. El círculo inscrito tiene radio uno. Como sus áreas
son cuatro y π, la proporción de puntos interiores aproxima π/4. Por eso
multiplico esa proporción por cuatro.

Cada punto usa dos valores consecutivos del LCG. Mantengo los mismos
parámetros y semilla en Python y Java para comparar implementaciones. N cuenta
puntos, no números individuales del generador.

El programa registra estimación, error absoluto y tiempo para mil, diez mil,+cien mil y un millón de puntos. Realizo cinco mediciones y reporto la mediana.
No incluyo archivos ni gráficas en el tiempo del cálculo.

En la ejecución entregada la mejor aproximación ocurrió con diez mil puntos.
Esto muestra que más muestras no obligan a que el error de cada prefijo
disminuya. La escala ideal 1/raíz(N) explica una tendencia, no una garantía.

La arquitectura separa modelo, vista y controlador. Strategy permite inyectar
la fuente de números; así pruebo puntos del centro, borde y esquina con
resultados conocidos. Las diez campañas intentan romper la CLI, las entradas,
las secuencias y las mediciones. Java incluye diez pruebas JUnit adicionales».

## Demostración en vivo desde 07APE

```bash
bash scripts/ejecutar.sh
bash scripts/verificar.sh
```

Para un ejemplo pequeño y rápido, sin sobrescribir la entrega:

```bash
.venv/bin/python -m ape07 --tamanos 1000 --repeticiones 1 --salida resultados/demo_python
java -jar java/target/ape07.jar --tamanos 1000 --repeticiones 1 --salida resultados/demo_java
```

Para demostrar un rechazo de entrada: `--tamanos 0`. Ambos programas explican
el error y terminan con código 2. Para explicar Strategy, abrir
`python/src/ape07/modelo.py` y
`java/src/main/java/ec/edu/simulacion/ape07/modelo/FuenteUniforme.java`.

## Preguntas para practicar

- ¿De dónde sale el factor cuatro? De la razón de áreas del círculo y el cuadrado.
- ¿Por qué <= y no solo <? Se incluye la frontera; la elección está documentada y se prueba.
- ¿Por qué dos millones de valores? Un millón de puntos requiere dos coordenadas por punto.
- ¿Por qué pueden coincidir π y diferir los tiempos? Se ejecuta la misma matemática en implementaciones y entornos de ejecución distintos.
- ¿Qué mide el error? La distancia absoluta a math.pi/Math.PI, no un porcentaje.
- ¿Por qué reiniciar la semilla? Para repetir el mismo problema y comparar cálculos y tiempos.
- ¿Las cinco mediciones son independientes estadísticamente? No: reproducen el mismo experimento para medir rendimiento.
- ¿El LCG demuestra azar verdadero? No, es determinista; la coincidencia prueba reproducción del cálculo.
- ¿Por qué no hay un modelo M/M/1? El docente confirmó que la práctica corresponde a Monte Carlo, según lo comunicado por el estudiante. Ese es el alcance implementado; la mención de M/M/1 es una discrepancia del documento original.

## Video

`evidencias/APE07-demostracion.mp4` es una demostración visual sin audio,
generada desde los datos reales. Muestra el modelo animado, fragmento de código,
salidas capturadas, tabla, gráficas y comprobaciones. No sustituye tu defensa
personal ni se presenta como una grabación de tu voz o de una interfaz en vivo.
