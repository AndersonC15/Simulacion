# Análisis 3 de 4 — diez campañas de QA adversaria

Las campañas se implementan en `python/tests/test_qa.py`, con unittest. Son
diez pruebas identificables, con múltiples subcasos y procesos reales de Java;
la suite falla, en vez de omitir integración, si no existe el JAR.
Java tiene además diez pruebas JUnit independientes del núcleo matemático.

| Nro. | Campaña | Intento de hacer fallar el trabajo |
|---|---|---|
| 01 | Vector conocido y aritmética extrema | Contrastar cinco estados conocidos; generar 10000 valores con semillas mínima y máxima |
| 02 | Geometría y 2N consumos | Fuente controlada: centro, dos fronteras y esquina; agotar exactamente ocho valores para cuatro puntos |
| 03 | Fuentes y parámetros inválidos | Cero, negativos, booleanos, decimales, texto, entero enorme, NaN, infinito, tamaños vacíos o duplicados |
| 04 | Reproducibilidad | Comparar 20000 estados con cada una de tres semillas; comprobar cambio de estado inicial |
| 05 | CLI adversaria Python/Java | Catorce entradas inválidas por lenguaje; código 2 y ausencia de trazas técnicas |
| 06 | Integración y rutas con espacios | Comparación completa de una ejecución real; N=1 y carpetas con espacios en ambos lenguajes |
| 07 | Manipulación de secuencia | Alterar un estado y actualizar su hash para intentar engañar al auditor; luego truncar el archivo |
| 08 | Resultados, tiempos y metadatos adulterados | Alterar π, conteo, mediana, tiempo NaN, repetición y coordenada; falsificar lenguaje, geometría, hash, cantidad y protocolo; eliminar la secuencia |
| 09 | Fallo de escritura y mediana | Usar un archivo como carpeta de salida; comprobar medianas con cantidad par e impar |
| 10 | Carga y semilla límite | Ejecutar los cuatro tamaños, hasta un millón de puntos, con semilla m-1; cotejar dos millones de estados |

## Ejecución y evidencia

```bash
bash scripts/verificar.sh
```

Los registros reales se guardan en `resultados/revision/java.log` y `qa.log`.
Los experimentos adulterados se crean exclusivamente en directorios temporales;
no se alteran los datos académicos para conseguir un resultado esperado.

Las comprobaciones numéricas son exactas para las secuencias y conteos de este
experimento. No se exige que el error disminuya en cada N ni que Java sea más
rápido: esos son resultados que deben observarse, no condiciones fabricadas.
Los tiempos deben ser finitos, positivos y coherentes con sus mediciones originales.

Las diez pruebas JUnit comprueban vector, semillas inválidas, rangos, geometría,
fuentes no válidas, tamaños no válidos, reproducibilidad, millón de puntos,
medianas/inmutabilidad y reinicio/repeticiones. Los resultados se reportan solo
después de consultar los registros; este documento describe la cobertura,
no sustituye una ejecución de la suite.
