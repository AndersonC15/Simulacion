# Análisis 1 de 4 — lectura y alcance de la guía

Fuente primaria: `ape_guia simulacion semana 7-signed.pdf`, cuatro páginas,
SHA-256 `649135d1d507ca217afb48b18f867169ba7ea254be0efa57446d484b2ce4137a`.
Se conservó sin modificaciones. Se contrastó el texto con la página 3 renderizada.

## Requisitos trazables

| Fuente | Requisito | Evidencia prevista en 07APE |
|---|---|---|
| p. 1, objetivos | Implementar Monte Carlo, analizar tamaño/error y comparar Python/Java | Código independiente de ambos lenguajes, tabla y conclusiones |
| p. 2, modelo | Puntos en un cuadrado y círculo inscrito; π ≈ 4 Nc/N | Estimador con cuadrado [-1,1)² y círculo de radio 1 |
| p. 2 | N = 1000, 10000, 100000, 1000000 | Cuatro filas de la tabla consolidada |
| pp. 2–3 | π estimado, error absoluto, tiempo Python y tiempo Java | CSV, gráficas e informe académico |
| p. 2, resultados esperados | Misma secuencia con mismos parámetros; tabla y conclusiones | Comparación exacta de todos los estados y puntos |
| p. 3 | Ocho preguntas de análisis de resultados | Informe, apartado 6 |
| p. 3 | Cuatro preguntas numeradas y una quinta sin numerar | Informe, apartado 7: se responden las cinco |
| pp. 3–4, rúbrica | Defensa y demostración: 4 puntos | Programa reproducible y guía de defensa |
| pp. 3–4, rúbrica | Implementación: 3 puntos | Modelo, resultados y verificación |
| p. 4, rúbrica | Documento y evidencias, video: 3 puntos | PDF académico, CSV, PNG y video de resultados |
| Usuario | MVC y un patrón adecuado | Modelo, vista, controlador y Strategy |
| Usuario | Diez pruebas profundas y cuatro análisis | Diez campañas QA y cuatro documentos de revisión |

## Contradicciones que no se deben ocultar

1. La rúbrica dice «Implementación correcta del modelo M/M/1», mientras el título,
   los objetivos, la fórmula y el procedimiento completos tratan de Monte Carlo
   para π. Tras la consulta, el estudiante comunicó que el docente confirmó que
   corresponde a Monte Carlo. La implementación de π sigue ese alcance confirmado;
   la referencia a M/M/1 se conserva únicamente como discrepancia del documento original.
2. El título extraído comienza «stimación». Se emplea «Estimación» en el reporte,
   sin alterar el documento firmado.
3. La bibliografía de la guía dice «Diapositivas semana 6». Se respeta esa
   referencia; no se inventa un archivo de diapositivas de semana 7.
4. La guía no fija generador, semilla, número de repeticiones, reloj ni sistema
   de coordenadas. Se documentan como decisiones de implementación.

La fecha académica es 12 y 13 de noviembre de 2026; asignatura Simulación,
ciclo 5, unidad U2, docente José O. Guamán Q. El nombre del estudiante se
verificó previamente en el informe APE 06: Anderson Mateo Coello Jaramillo.

No se puede garantizar 10/10: cuatro puntos dependen de la defensa personal.
El alcance Monte Carlo quedó aclarado por el docente, según lo comunicado por
el estudiante el 12 de noviembre de 2026.
