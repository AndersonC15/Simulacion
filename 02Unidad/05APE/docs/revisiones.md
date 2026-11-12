# Registro de cinco revisiones

Fecha: **8 de noviembre de 2026**, zona horaria America/Guayaquil. Se realizaron cinco pasadas con objetivos diferentes. No se trata de cinco ejecuciones idénticas del mismo conjunto de pruebas.

## 1. Revisión de requisitos y fuentes

Se leyeron las tres páginas de la guía y las 25 páginas de las diapositivas. Se extrajeron los ocho pasos del procedimiento, parámetros, resultados esperados y cinco preguntas. Se separaron los requisitos académicos de los requisitos de software solicitados por el usuario.

Resultado: implementación centrada en la práctica 05; [requisitos.md](requisitos.md) relaciona cada requisito con su evidencia. La segunda semilla está identificada como elección del experimento. El PDF original se conservó y la copia de las diapositivas coincide en SHA-256 con su fuente, registrada en [fuentes.md](fuentes.md).

## 2. Revisión matemática y numérica

Se comprobó que la salida comienza en X1, la recurrencia conserva el estado y la normalización usa división real. Los dos lenguajes se verificaron contra el vector conocido que empieza por `87628868, 71072467, 2332836374, 2726892157, 3908547000, 483019191`.

Se revisaron las tres condiciones de Hull–Dobell y se distinguió período teórico de repetición observada. Un ciclo de módulo 16 comprueba el cierre completo y otro de módulo 8 comprueba una etapa previa al ciclo. También se verifica una operación extrema que excedería la capacidad de multiplicación de un `long` sin aritmética exacta.

Resultado: siete pruebas Python y siete Java aprobadas, sin errores. El período teórico es `4294967296`; no se reporta la muestra de 10 000 como período medido.

## 3. Revisión de arquitectura y código

Se revisaron los imports y responsabilidades de modelos, vistas, controladores y puntos de entrada. El modelo no depende de consola, archivos ni gráficas. Los controladores reciben una estrategia de generación y una vista mediante contratos; las pruebas utilizan implementaciones controladas. Parámetros y resultados se conservan inmutables; cada generador encapsula su estado.

Resultado: MVC y Strategy identificables en ambos lenguajes, con aplicación concreta de SOLID documentada en el README. Python usa paquete instalable con `pyproject.toml`; Java usa paquetes, POM y estructura Maven. `bash -n` valida la sintaxis de los tres scripts de shell.

## 4. Revisión de ejecución y resultados

Se ejecutaron ambas aplicaciones con semillas 12345 y 54321. Se validaron las 10 000 filas de cada CSV, índices, recurrencia, normalización, metadatos, estadísticas y PNG. Se compararon 20 000 pares entre lenguajes y se generaron las dos tablas de 20 observaciones y el informe. Se inspeccionaron visualmente gráficas de ambos lenguajes.

Resultado: coincidencia numérica exacta en todos los pares y cambio de las 10 000 posiciones al cambiar de semilla. Durante la revisión se corrigió una diferencia exclusivamente de redondeo de consola y se ajustó una etiqueta de eje de Java para evitar solapamiento. Se volvió a ejecutar `scripts/verificar.sh` sobre las correcciones; la salida está en [verificacion.log](verificacion.log).

## 5. Revisión de uso, errores y documentación

Se comprobaron los comandos de preparación y ejecución descritos en el README. Se ejecutaron ambos programas desde un directorio temporal, con rutas de salida que contienen espacios, ayuda, las semillas límite 0 y 4294967295 y una sola observación. Se probaron cinco entradas inválidas por lenguaje: semilla negativa, semilla igual a m, cantidad cero, cantidad mayor al límite y semilla no numérica. Se verificó que terminan con código 2 y un mensaje, sin traza técnica.

Se alteró una copia temporal de una salida Java: el comparador rechazó la recurrencia incorrecta con código 1. Los resultados entregados no fueron alterados. Se revisaron los enlaces locales, la correspondencia de las preguntas y el contenido del informe y del README.

Resultado: comandos reproducibles, errores controlados y documentación que distingue requisitos, decisiones propias y límites de las observaciones. La guía no aporta rúbrica numérica; este registro acredita verificaciones realizadas y no garantiza una calificación.
