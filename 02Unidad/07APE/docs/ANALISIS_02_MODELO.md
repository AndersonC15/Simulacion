# Análisis 2 de 4 — modelo, diseño y decisiones numéricas

## Geometría y fórmula

El cuadrado tiene lado 2, área 4 y coordenadas [-1,1)². El círculo inscrito
tiene radio 1 y área π. La proporción de área interior es π/4; por tanto:

```text
x = 2 U1 - 1; y = 2 U2 - 1
interior ⇔ x*x + y*y <= 1
pi_estimado = 4 * interiores / N
error_absoluto = abs(pi_estimado - pi_referencia)
```

La frontera se incluye mediante <=. N cuenta puntos: se consumen exactamente
2N valores del generador. Los cuatro tamaños utilizan prefijos de una misma
secuencia, reiniciada con la misma semilla. Son comparaciones anidadas, no
cuatro muestras independientes.

## Estrategia de generación

Se elige el LCG MINSTD del material ya utilizado en el APE 06:
a=16807, c=0, m=2147483647, semilla=123457. No son parámetros impuestos por
la guía 07. La semilla debe estar entre 1 y m-1; se excluye cero para evitar
la secuencia degenerada del LCG multiplicativo. Python usa enteros y Java
long: a*(m-1) cabe en long, por lo que aquí no se necesita BigInteger.

La división es real en ambos lenguajes. Con m=2^31-1, los normalizados no
son, en general, fracciones binarias exactas; ambos programas usan IEEE-754
binary64 y las mismas operaciones. La comparación exige igualdad exacta de
estados, coordenadas, conteos y estimaciones para el experimento ejecutado.

## Arquitectura

- Modelo: parámetros inmutables, contrato FuenteUniforme, LCG, estimador y medición.
- Vista: consola y exportación CSV, JSON y binario.
- Controlador: valida tamaños y coordina modelo/vista.
- Strategy: EstimadorPi recibe FuenteUniforme. En producción se inyecta LCG;
  en pruebas se inyectan fuentes controladas para verificar centro, borde,
  esquina y datos inválidos sin depender de resultados aleatorios.

No existe un patrón universalmente óptimo. Strategy encaja aquí porque
separa la generación de números de la geometría y permite comprobar ambos
componentes con claridad, sin introducir un framework innecesario.

## Tiempo y reproducibilidad

Se realizan tres calentamientos de hasta 10000 puntos y cinco mediciones por
tamaño, con reinicio de semilla en cada una. Se publica la mediana, el mínimo
y los cinco tiempos originales. Se mide generación y clasificación de puntos;
se excluyen archivos, gráficas, comparación, compilación y calentamiento.
Los relojes son perf_counter y System.nanoTime. Las cinco repeticiones miden
rendimiento, no son cinco réplicas estadísticas independientes.

Se exportan 2 millones de estados uint32 big-endian (8 MB por lenguaje) para
verificar realmente toda la secuencia, además de una tabla legible inicial.
El comparador verifica longitud, SHA-256, recurrencia estado por estado,
coordenadas, pertenencia al círculo, cada conteo acumulado y cada tiempo.
No confía únicamente en el hash ni en los resúmenes escritos por los programas.

## Alcance de la explicación del error

En Monte Carlo ideal con puntos uniformes independientes, la desviación
estándar del estimador es 4 sqrt(p(1-p)/N), con p=π/4: escala como 1/sqrt(N).
Esto explica la tendencia de precisión/costo, no garantiza disminución
monótona del error absoluto en una trayectoria ni demuestra independencia
del LCG. La referencia visual 1/sqrt(N) no es una cota ni un intervalo de confianza.

Los límites N<=1000000 y repeticiones<=30 son protecciones operativas
documentadas. Se permiten tamaños pequeños para comprobar el modelo; la
entrega académica exige específicamente los cuatro tamaños de la guía.
