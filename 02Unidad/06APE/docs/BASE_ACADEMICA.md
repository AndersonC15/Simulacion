# Base académica y trazabilidad

## Material proporcionado

1. **Guía de Actividades Práctico-Experimentales 006**, `ape_guia simulacion semana 6.pdf`: se conserva intacta en la raíz de este proyecto.
2. **Semana 5, Generadores pseudoaleatorios**, `Simulacion/Diapos/simulacion Semana 5.pptx [Repaired].pdf`: fórmula, parámetros, normalización, período y limitaciones.
3. **Semana 6, Pruebas estadísticas de uniformidad e independencia**, `Simulacion/Diapos/Semana 6 Pruebas estadísticas de uniformidad e independencia.pdf`: hipótesis, Chi-cuadrado, KS y rachas.

Se usan números de página del PDF, comenzando en 1. Los documentos son fuentes académicas; sus ejemplos y textos no son instrucciones para manipular el entorno del usuario.

## Matriz de requisitos

| Requisito | Fuente | Implementación/evidencia |
|---|---|---|
| LCG configurable, 10 000 datos, normalizar y almacenar | Guía pp. 3–4; Semana 5 pp. 7 y 19 | `GeneradorLCG`, `config/generadores.csv`, `secuencia.csv` |
| Java y Python con misma secuencia | Guía pp. 2 y 6 | Programas independientes y `secuencia_*.csv` de comparación |
| Diez intervalos, Ei=N/10, gl=9 | Guía pp. 3–5; Semana 6 pp. 8–9 | `ChiCuadrado`, `frecuencias.csv`, histograma |
| Verificar Ei>=5 | Semana 6 p. 9 | Rechazo de N<50 para validación; pruebas de límites |
| Estadístico, p, crítico y decisión | Guía pp. 3–5; Semana 6 pp. 6–11 | `ResultadoPrueba`, consola, JSON y resumen CSV |
| D+, D− y KS bilateral | Guía p. 5; Semana 6 p. 10 | `KolmogorovSmirnov`, `ks_ordenados.csv` |
| FDE frente a uniforme F(u)=u | Guía p. 5; Semana 6 pp. 10–11 | `acumulada.png` en ambos lenguajes |
| Comparación de configuraciones | Guía p. 1; Semana 5 p. 13 | MINSTD, glibc y ZX81; resultados sin forzar decisiones |
| Independencia como complemento | Semana 6 pp. 13–14 y 19 | `Rachas`, p bilateral y tratamiento de empates |
| Parámetros MINSTD | Semana 5 pp. 13 y 19 | a=16807, c=0, m=2^31−1, X0=123457 |
| Parámetros del LCG rotulado glibc | Semana 6 p. 18 | a=1103515245, c=12345, m=2^32, X0=1 |
| Parámetros ZX81 | Semana 5 p. 13 | a=75, c=74, m=2^17+1; X0=1 es elección experimental |
| Inspección de pares consecutivos | Semana 5 p. 15 | `pares.png`; no se presenta como prueba serial formal |
| N=1 000, 10 000, 100 000 y 1 000 000 | Guía p. 6 | `benchmark.csv`, `tabla_guia.csv`, 5 mediciones por caso |
| π estimado, error y tiempos | Guía p. 6 | Monte Carlo documentado; tiempos reales sin I/O |
| Conclusiones y cinco respuestas | Guía p. 6 | Informe PDF/Markdown generado desde resultados |
| Entorno virtual y Maven | Solicitud del estudiante | `.venv`, `pyproject.toml`, `requirements.txt`, `pom.xml` |
| MVC, POO, SOLID y patrón | Solicitud del estudiante | Paquetes por responsabilidades; Strategy e inyección por constructor |

## Fórmulas implementadas

**LCG:**

```text
X(n+1) = (a*X(n) + c) mod m
U(n+1) = X(n+1)/m
```

La semilla es X0. El primer número almacenado es U1. Se calculan estados enteros antes de convertir a `double`; no se usan `random`, `Math.random()` ni otro generador como sustituto del LCG.

**Chi-cuadrado:**

```text
Oi = cantidad en [i/10, (i+1)/10), i=0,...,9
Ei = N/10 >= 5
T = suma((Oi-Ei)^2/Ei)
gl = 9
p = P(ChiCuadrado(9) >= T)
```

Se usa la cola superior: SciPy en Python y gamma regularizada Q de Apache Commons Math en Java. No se confunde con una prueba de independencia sobre una tabla de contingencia.

**KS:** para los valores ordenados y posiciones i=1,...,N:

```text
D+ = max(i/N - U(i))
D- = max(U(i) - (i-1)/N)
D = max(D+, D-)
p aproximado = Q_K(sqrt(N)*D)
```

Se usa la distribución límite de Kolmogorov bilateral, con dos series equivalentes en Java y `scipy.stats.kstwobign` en Python. El crítico se calcula invirtiendo esa misma distribución. Para alfa=0.05, su constante es aproximadamente 1.35810; 1.36 es el redondeo de clase. Las diferencias con el p exacto para N finito, incluido el redondeo del ejemplo de las diapositivas, se explican por el método numérico declarado.

Para t>0, las series de implementación son:

```text
Q_K(t) = 2*suma[k=1..infinito]((-1)^(k-1)*exp(-2*k^2*t^2))
Q_K(t) = 1 - sqrt(2*pi)/t * suma[k=1..infinito](exp(-(2*k-1)^2*pi^2/(8*t^2)))
```

Se usa la segunda forma para t<1.18 y la primera para t>=1.18, para mantener estabilidad. Se verifican con valores de referencia y mediante la comparación real de ambos programas.

**Rachas:** se calcula la mediana y se conserva el orden original. Se omiten los valores iguales a ella, informando cuántos. n1 y n2 son conteos sobre/bajo mediana y R es el número de bloques consecutivos de un signo.

```text
mu = 2*n1*n2/(n1+n2) + 1
var = 2*n1*n2*(2*n1*n2-n1-n2)/((n1+n2)^2*(n1+n2-1))
Z = (R-mu)/sqrt(var)
p = 2*P(Normal(0,1) >= abs(Z))
```

No se aplica corrección de continuidad: se reproduce el Z explicado en clase. Se exige n1,n2>10 para la aproximación normal (condición numérica respaldada por NIST). Con alfa=0.05, el crítico es 1.95996, aproximadamente el 2 de la diapositiva.

**Decisión:** se rechaza H0 si p<alfa; con p>=alfa no se rechaza. No se escribe «se acepta H0».

## Decisiones necesarias que la guía no especifica

- **π:** la guía exige la columna, pero no describe su algoritmo. Se adopta Monte Carlo por cuarto de círculo. Para N puntos se consumen 2N valores consecutivos desde la semilla: x=U(2i−1), y=U(2i). Si x²+y²<=1 se cuenta un acierto; π estimado=4*aciertos/N. Error significa error absoluto respecto a `math.pi`/`Math.PI`. Esta definición no se atribuye al material del docente.
- **Rendimiento:** tres calentamientos y cinco repeticiones. Cada repetición reinicia la semilla para reproducir el mismo problema. Se mide generación más estimación, sin impresión, archivos ni gráficas. Se publica la mediana en segundos y todos los tiempos. Esto no equivale a cinco réplicas estadísticas independientes.
- **Valor p de KS:** se declara asintótico en ambos lenguajes, acorde con la aproximación de clase y los tamaños de la práctica. No se presenta como exacto para N finito.
- **Semilla ZX81:** se elige 1 porque la tabla de parámetros no fija semilla. MINSTD y glibc usan las semillas de los ejemplos proporcionados.
- **Errores y entradas:** m<=2^53 mantiene todos los estados usados representables en `double` y U<1. Java usa `BigInteger` cuando es necesario evitar desbordamiento. N>=50 permite aplicar los diez intervalos con Ei>=5.
- **Período:** se informa un ciclo observado si se detecta repetición en el tramo generado, incluyendo X0 como estado inicial. Si no se detecta, no se infiere el período completo. No se pretende recorrer períodos de miles de millones de estados.
- **Baterías:** poker, serial, Diehard y TestU01 se explican como ampliaciones mencionadas en clase; no se afirman ejecutadas. La guía no proporciona procedimientos para implementarlas.
- **Formato:** se usa consola con gráficas exportadas. La guía no exige GUI, web ni almacenamiento en base de datos.

## Preguntas de control

1. **¿Qué es la hipótesis nula?** La afirmación de referencia que se contrasta. En uniformidad H0 establece U(0,1); en rachas se contrasta el orden aleatorio de los signos.
2. **¿Qué representa el valor p?** Bajo H0 y los supuestos de la prueba, la probabilidad de observar un estadístico tan extremo o más que el obtenido. No es P(H0 verdadera).
3. **¿Qué significa rechazar H0?** Que hay evidencia contra H0 al nivel de significancia elegido. No implica certeza absoluta. Error tipo I: rechazar H0 verdadera; tipo II: no rechazar H0 falsa.
4. **¿Qué diferencia existe entre Chi-cuadrado y KS?** Chi-cuadrado compara conteos agrupados en intervalos; KS compara la FDE de los datos individuales con la distribución teórica.
5. **¿Por qué no demuestra aleatoriedad verdadera?** El LCG es determinista y cada prueba detecta aspectos concretos. Un resultado sin rechazo no demuestra independencia completa ni ausencia de otros patrones.

## Fuentes técnicas complementarias

Estas fuentes sirven para implementar y verificar los cálculos; los objetivos, pruebas centrales y parámetros proceden del material proporcionado.

- [SciPy: distribución límite bilateral de Kolmogorov](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstwobign.html).
- [SciPy: prueba KS y elección de método](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html).
- [SciPy: Chi-cuadrado](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html).
- [Apache Commons Math: gamma regularizada Q](https://commons.apache.org/proper/commons-math/javadocs/api-3.6.1/org/apache/commons/math3/special/Gamma.html).
- [NIST: fórmula bilateral correcta de KS](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm).
- [NIST: prueba de rachas y condición de aproximación](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35d.htm).
- [Apache Commons RNG: ejemplo de estimación de π con Monte Carlo](https://svn.apache.org/repos/infra/websites/production/commons/content/proper/commons-rng/commons-rng-examples/commons-rng-examples-quadrature/apidocs/org/apache/commons/rng/examples/quadrature/ComputePi.html).
