# Correspondencia de requisitos

Se distingue entre lo solicitado por el usuario y lo establecido por los documentos académicos. La guía se identifica como «Práctica Nro. 05» aunque su encabezado diga «Guía ... Nro. 004»; se usa el número de práctica y su título, sin corregir el PDF original.

| Fuente | Requisito | Implementación o evidencia |
|:---|:---|:---|
| Guía, §5, paso 1 | a=1664525, c=1013904223, m=2³², semilla=12345 | Valores predeterminados de `ParametrosLCG` y `ParametrosLCG.deLaGuia`. |
| Guía, §5, paso 2 | Generar 10 000 valores en Python | `resultados/python/semilla_12345.csv`, 10 000 filas más cabecera. |
| Guía, §5, paso 3 | Mismo algoritmo en Java | `GeneradorLCG.java`; CSV independiente en `resultados/java`. |
| Guía, §5, paso 4 | Comparar primeras 20 observaciones | `comparacion_20_semilla_12345.csv` y tabla en `resultados/informe.md`. |
| Guía, §5, paso 5 | Graficar secuencia | PNG de cada lenguaje y semilla, con todas las observaciones. |
| Guía, §5, paso 6 | Analizar período | Hull–Dobell y detección de repeticiones; JSON e informe distinguen teoría y muestra. |
| Guía, §5, paso 7 | Cambiar semilla | Segundo experimento con 54321, elección explícita del proyecto. |
| Guía, §5, paso 8 | Comparar resultados | Segundo CSV comparativo, cotejo completo y análisis del cambio en el informe. |
| Guía, §6 | Tabla y conclusiones | Dos tablas de 20 filas y conclusiones en el informe. |
| Guía, §7 | Cinco preguntas de control | Las cinco preguntas respondidas en `docs/fundamento.md` y en el informe generado. |
| Guía, §9 | Bibliografía: diapositivas semana 5 | Diapositivas encontradas en `Simulacion/Diapos`, revisadas e identificadas en `fuentes.md`. |
| Diapositivas, pp. 7–10 | Recurrencia, normalización, período y Hull–Dobell | Dominio matemático y justificación del período completo. |
| Diapositivas, pp. 14–15 | Limitaciones y pares consecutivos | Gráficas de pares y explicación sin atribuir independencia a la apariencia visual. |
| Diapositivas, pp. 19–20 | Estado persistente y errores comunes | Inicialización única, pruebas de continuidad y explicación de período frente a calidad. |
| Usuario | Python con entorno virtual y dependencias | `.venv`, `pyproject.toml`, requirements y script de preparación. |
| Usuario | Java con pom.xml y estructura nativa | Proyecto Maven, paquetes, `src/main`, `src/test`, JAR ejecutable. |
| Usuario | MVC y POO | Modelos, vistas y controladores separados en ambos lenguajes. |
| Usuario | Patrón adecuado, Clean Code y SOLID | Strategy, inyección, contratos pequeños, estado encapsulado y tabla explicativa en README. |
| Usuario | README y cinco revisiones | README con ejecución y diseño; `docs/revisiones.md` registra cinco pasadas diferenciadas. |

No se añadieron pruebas estadísticas de uniformidad o independencia de la semana 6 ni otros generadores a los experimentos de la guía. La media, mínimo, máximo y varianza son únicamente descriptivos, como complemento de lo mencionado en las diapositivas.
