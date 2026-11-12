## Análisis del período

Hull–Dobell, presentado en las diapositivas de la semana 5, garantiza período máximo del LCG mixto cuando se cumplen estas tres condiciones:

1. `gcd(c,m)=1`. Aquí `c=1013904223` es impar y `m=2^32`; son coprimos.
2. Todo factor primo de `m` divide a `a−1`. El único primo es 2 y `1664524` es par.
3. Si 4 divide a `m`, también divide a `a−1`. Se cumple `1664524 / 4 = 416131`.

Por tanto, **τ = m = 4 294 967 296**, para cualquier semilla válida de estos parámetros. La prueba es teórica: no se recorrieron cuatro mil millones de estados.

En cada experimento se revisaron `X0` y las 10 000 salidas sin detectar repetición. La longitud de muestra **no es** el período empírico. Para parámetros generales puede existir una etapa previa al ciclo: el analizador distingue esa etapa de la longitud del ciclo. Los casos de prueba pequeños verifican ambos escenarios.

Con período completo, las semillas 12345 y 54321 pertenecen al mismo ciclo, con distintos puntos de inicio. Cambiar de semilla no crea independencia garantizada ni mejora los parámetros.

## Preguntas de control

1. **¿Qué significa pseudoaleatorio?** Una secuencia producida por reglas deterministas que busca imitar propiedades del azar. Con estado inicial y parámetros se puede reproducir; su calidad requiere evaluación.
2. **¿Qué función cumple la semilla?** Es el estado inicial `X0`. Los mismos parámetros y la misma semilla producen exactamente la misma secuencia. Se inicializa una vez, antes del bucle.
3. **¿Qué significa período?** Es la longitud del ciclo de estados que se repite. En el generador de la guía, el ciclo incluye la semilla y τ es el menor entero positivo tal que `Xτ=X0`. Otros parámetros pueden tener una etapa previa al ciclo.
4. **¿Qué ocurre con parámetros inadecuados?** Pueden producir ciclos cortos, patrones geométricos y correlaciones que perjudican una simulación. No cumplir Hull–Dobell descarta período máximo del LCG mixto, pero no calcula automáticamente el período restante.
5. **¿Qué ventaja tiene usar dos lenguajes?** Verificar reproducibilidad y detectar errores de índices, normalización, tipos numéricos o desbordamiento. La coincidencia comprueba implementación; no demuestra calidad estadística.

## Conclusiones

1. Las implementaciones reprodujeron exactamente 10 000 estados y sus normalizados por semilla, con dos semillas, cumpliendo la comparación entre Python y Java.
2. Hull–Dobell permite justificar el período completo sin recorrerlo; el análisis empírico se limita a la muestra realmente observada.
3. Cambiar la semilla modifica el inicio y las observaciones, mientras conserva el período garantizado por los parámetros.
4. La práctica permite estudiar determinismo y reproducibilidad. El período máximo no elimina los hiperplanos, la correlación de bits bajos ni la predictibilidad tratados en clase. El LCG no es apropiado para criptografía; las pruebas estadísticas formales se desarrollan en la semana 6.

## Fuentes y alcance

- `ape_guia simulacion semana 5.pdf`, pp. 1–2: objetivos, parámetros, procedimiento, resultados y preguntas.
- `simulacion Semana 5.pptx [Repaired].pdf`, pp. 6–10, 14–15 y 19–20: determinismo, LCG, Hull–Dobell, limitaciones y errores comunes.
- La guía de la práctica tiene prioridad para elegir parámetros. Las diapositivas complementan la explicación; su ejemplo MINSTD no sustituye el LCG solicitado.
- Los casos pequeños de las pruebas son recursos de verificación del software; no reemplazan los experimentos de 10 000 valores.
