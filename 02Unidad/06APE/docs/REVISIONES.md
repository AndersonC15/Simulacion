# Cinco revisiones de la entrega

Las revisiones se hicieron sobre el software ejecutado en este equipo. Son cinco comprobaciones diferentes; no se declara una calificación ni se reemplaza una rúbrica del docente.

## 1. Revisión del material y cobertura

Se leyeron la guía 006 y las presentaciones de Semanas 5 y 6. La matriz de [BASE_ACADEMICA.md](BASE_ACADEMICA.md) vincula los requisitos con código y archivos de evidencia.

Se verificaron los parámetros MINSTD, glibc y ZX81 contra las páginas indicadas. La semilla de ZX81, el método para estimar π, la definición del error, la medición de tiempos y el método numérico de KS están identificados como decisiones de implementación cuando el material no los especifica.

**Resultado:** cubiertos el LCG, los 10 000 valores, Chi-cuadrado, KS, gráficas, dos lenguajes, comparación de configuraciones, tabla de π/rendimiento, conclusiones y cinco preguntas. Se agregó rachas por su desarrollo en Semana 6. No se afirma haber ejecutado baterías que la guía no desarrolla.

## 2. Revisión matemática y de casos límite

Se ejecutaron **32 pruebas Python y 19 pruebas Java**, sin fallos ni omisiones en la verificación completa. Evidencias:

- `resultados/revision/pytest.log`
- `resultados/revision/maven.log`
- Casos de prueba en `python/tests/` y `java/src/test/java/`.

Se comprobaron un ciclo LCG calculado a mano, el vector conocido Park–Miller, parámetros de 48 bits, normalización, límites de intervalos, Ei>=5, D+ y D− con un ejemplo manual, preservación del orden, valores de la distribución de Kolmogorov, rachas y empates, p=alfa, secuencias constantes y entradas inválidas.

Las tres configuraciones se contrastaron con `scipy.stats.chisquare` y `scipy.stats.kstest(method="asymp")`. El caso de π con ocho puntos tiene seis aciertos comprobables a mano y estimación 3. Un caso con frecuencias uniformes pero orden predecible permite comprobar que uniformidad e independencia no se confunden.

**Resultado:** cálculos coherentes con las fórmulas declaradas; no se inventan valores p cuando rachas no es aplicable.

## 3. Revisión de equivalencia entre lenguajes

Se ejecutaron independientemente Python y Java y se compararon:

- **30 000 estados y valores normalizados:** 10 000 por cada una de tres configuraciones.
- Todas las posiciones, recurrencias y normalizaciones, con igualdad exacta de los estados y valores exportados.
- Frecuencias, estadísticos, críticos, valores p, detalles y decisiones de las tres pruebas.
- **12 estimaciones de π:** tres configuraciones por cuatro tamaños, incluidos sus conteos interiores.

Las tolerancias para resultados estadísticos se registran en `resultados/comparacion/verificacion.json`. Los datos completos comparados están en `secuencia_*.csv` y `tabla_guia.csv`.

La integración también ejecuta el JAR real con parámetros de 48 bits y comprueba que alterar intencionalmente una fila haga fallar la comparación.

**Resultado:** equivalencia confirmada; pequeñas diferencias de redondeo en estadísticas se mantienen dentro de las tolerancias documentadas.

## 4. Revisión de instalación y ejecución

Se ejecutaron correctamente:

```bash
./scripts/preparar.sh
./scripts/ejecutar_todo.sh
./scripts/verificar.sh
```

Entorno verificado: Python 3.14.4 en `.venv`, Maven 3.9.12 y JDK Temurin 25.0.5 local. Se conservó `release=25` del `pom.xml`. Como el Java 25 del sistema no tenía compilador y el compilador predeterminado era 21, se preparó un JDK local con origen y SHA-256 registrados en `.tools/jdk-25-origen.json`. No se cambió el Java global.

Se verificaron las opciones de consola y la sintaxis de los scripts. Las gráficas Java se generaron sin pantalla, sin ejecutar Python desde el programa Java.

**Resultado:** entorno instalado, JAR ejecutable y flujo completo operativo. Los logs de preparación y ejecución se conservan en `resultados/revision/`.

## 5. Revisión de resultados, presentación y documentación

Se comprobaron los CSV, los archivos JSON y las imágenes producidas:

- Seis secuencias y seis tablas KS con 10 000 filas de datos cada una.
- Seis tablas de frecuencias con diez filas de datos.
- Dieciocho PNG de los programas, más la gráfica consolidada de error y rendimiento.
- Doce filas de benchmark por lenguaje y **120 tiempos individuales** entre ambos.
- Medianas y mínimos de los CSV coincidentes con las mediciones individuales guardadas.

El PDF se revisó mediante extracción de texto y renderizado visual, comprobando tablas legibles, gráficas, resultados, conclusiones y preguntas de control. Se ajustó la distribución de gráficas y encabezados para evitar páginas con una sola gráfica aislada o títulos separados de su contenido. El informe también se conserva en Markdown y los datos completos en CSV.

Se verificó que el modelo no importe vistas ni controladores. El README explica preparación, ejecución independiente, comparación, arquitectura MVC/Strategy y límites de interpretación.

**Resultado:** entrega documentada y revisada. En N=10 000 las tres configuraciones no son rechazadas por estas pruebas; esto se informa sin forzar resultados. Con un millón de puntos, los errores absolutos de π observados son aproximadamente 0.00163135 (MINSTD), 0.00034335 (glibc) y 0.01859665 (ZX81). La discusión distingue estos resultados de una garantía general de calidad.
