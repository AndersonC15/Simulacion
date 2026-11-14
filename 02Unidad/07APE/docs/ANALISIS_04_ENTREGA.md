# Análisis 4 de 4 — revisión final y evidencia de entrega

## Resultado matemático observado

Las ejecuciones reales produjeron:

| N | Puntos interiores | π estimado | Error absoluto |
|---:|---:|---:|---:|
| 1000 | 765 | 3.060000 | 0.08159265358979306 |
| 10000 | 7850 | 3.140000 | 0.0015926535897929917 |
| 100000 | 78608 | 3.144320 | 0.002727346410206888 |
| 1000000 | 785969 | 3.143876 | 0.002283346410206999 |

La mejor aproximación ocurrió con 10000 puntos, no con el mayor tamaño.
Esto se mantuvo en las conclusiones y las respuestas: el error no se corrigió
para fabricar una tendencia monótona. En las mediciones conservadas Java
registró menores medianas; no se generaliza a todas las implementaciones.

## Verificación de software

- `resultados/revision/qa.log`: diez campañas aprobadas, con subcasos adversarios
  e integración real. Incluye carga de un millón de puntos con semilla m-1.
- `resultados/revision/java.log`: diez pruebas JUnit, cero fallos, errores u omisiones;
  Maven registra BUILD SUCCESS.
- El auditor verificó dos millones de estados y reconstruyó un millón de puntos;
  comprobó recurrencia, coordenadas, interiores, estimación y error de cada N.
- Los cuarenta tiempos originales, veinte por lenguaje, son positivos y finitos;
  sus medianas y mínimos coinciden con las tablas publicadas.
- El comparador rechazó secuencias alteradas incluso con hash actualizado,
  archivos truncados, resultados falsos, tiempos NaN y coordenadas adulteradas.
- Entradas CLI inválidas terminan con código 2 en ambos lenguajes sin mostrar
  trazas internas. Las rutas con espacios y el caso N=1 fueron probados.

## Documento y recursos

El informe académico tiene nueve páginas, con formato institucional e identidad
verificada, tres objetivos, modelo y decisiones, MVC/Strategy, tabla de la guía,
comparación inicial, gráficas, ocho respuestas de análisis y cinco de control,
conclusiones, QA, bibliografía y anexos. Incluye una versión Markdown editable.

La revisión documental contrasta cifras del PDF con los CSV originales, verifica
encabezados/paginación y comprueba la presencia de las cinco preguntas. Las
gráficas se producen desde los estados reales. El video de 76 segundos se
codifica desde puntos, código, registros y tablas reales; se decodifica completo
para detectar un archivo corrupto. No contiene audio ni pretende sustituir la
defensa personal.

`scripts/auditar_entrega.py` reproduce esta auditoría y guarda sus resultados
en `resultados/revision/auditoria_final.json`. El SHA-256 de la guía firmada
coincide con la lectura inicial. No se modificaron los proyectos APE 05 y 06.

## Límites que afectan la evaluación

Se cubre el procedimiento de Monte Carlo, confirmado por el docente según
lo comunicado por el estudiante el 12 de noviembre de 2026. La referencia
contradictoria a un modelo M/M/1 se conserva como una discrepancia del PDF
original; el alcance está aclarado. Cuatro puntos de la rúbrica requieren defensa oral y
dominio personal del estudiante: el código y este informe no garantizan 10/10.

El generador y su semilla son decisiones documentadas, y no se afirma haber
demostrado independencia o aleatoriedad verdadera. Las cuatro muestras son
prefijos de una misma secuencia, y las cinco mediciones repiten ese problema.
La escala 1/sqrt(N) explica el modelo ideal, no certifica la calidad del LCG.
