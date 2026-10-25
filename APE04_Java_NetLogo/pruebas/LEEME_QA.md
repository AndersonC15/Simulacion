# Revision tecnica de la APE 04

Esta revision corresponde al ZIP proporcionado y a su version corregida. No es el informe academico de la practica. Los resultados de cada caso estan en `RESULTADOS_QA.md` y `RESULTADOS_INTERFAZ.md`, y el codigo que los ejecuta se incluye en esta carpeta.

## Fallos reproducidos en el ZIP anterior

| Caso | Lo que ocurrio | Causa y correccion |
|---|---|---|
| O01 | El modelo avanzo a t=2 aunque su horizonte era 1 | `paso()` no comprobaba el limite. Ahora rechaza un paso posterior sin modificar el tiempo |
| O02 | `ResultadoPaso(-1,-5,105,0)` se acepto | Faltaba validar el objeto de resultados. Ahora rechaza tiempos/conteos negativos y sumas fuera del limite |
| O03 | Modificar un individuo obtenido del getter y asignarle null provoco `NullPointerException` al contar | La lista era no modificable, pero sus individuos seguian siendo los originales. Ahora se devuelven copias y se rechazan estados nulos |
| O04 | Al cargar, NetLogo quedaba en t=100 | El controlador asignaba directamente el horizonte al indice. Ahora comienza en t=0 |
| O05 | ANIMAR al abrir no avanzaba | Ya estaba al final y `avanzar` terminaba inmediatamente. La ventana nueva comienza a reproducir y permite pausar/continuar |
| O06 | VER COMPLETO no producia un cambio visible al abrir | El archivo ya se habia mostrado completo. Ahora se distingue inicio, reproduccion, pausa y vista completa |
| O07 | Se acepto un CSV que pasaba de 5 infectados a 100 recuperados en un solo paso | Solo se comprobaban suma y monotonia. Ahora tambien se comprueban las transiciones posibles del SIR discreto |
| O08 | Un CSV valido con N=10 y dos pasos fue rechazado | El importador exigia N=100 y 101 filas para cualquier archivo. Se mantienen esos valores en el ejemplo base, pero se aceptan otros escenarios dentro de limites explicitos |
| O09 | Indicar la misma ruta en `--csv` y `--png` sustituyo el CSV por una imagen PNG | No se validaban destinos en conflicto. La nueva version deriva nombres diferentes del mismo nombre base y no sobrescribe archivos existentes |

O02 y O03 son ataques desde codigo Java, no desde campos de la interfaz. O04, O05 y O06 describen sintomas de una misma decision incorrecta al cargar; no se presentan como tres fallos independientes de calculo. No se provoco un agotamiento intencional de toda la memoria de la maquina para demostrar la falta de limites del ZIP anterior.

Durante el desarrollo del visor integrado se encontraron y corrigieron dos problemas adicionales: la API integrada no resolvia los editores `__includes`, y el refresco visual podia conservar la imagen de un paso anterior. El adaptador reune los archivos de codigo temporalmente y solicita el refresco desde el hilo apropiado. Las pruebas de interfaz y la captura final corresponden a la version corregida.

## Cobertura

Resultado final: 195 casos de modelo/CLI/archivos/NetLogo y 28 casos de interfaz, todos aprobados: 223 en total. Los registros por caso se encuentran en los dos archivos `RESULTADOS_*.md`. Una comprobacion adicional ejecuto el JAR desde `/tmp`, con una ruta de proyecto que contenia espacios: aparecio la ventana real, y Ctrl+Q cerro el motor y devolvio codigo 0. Tambien se ejecutaron los comandos de ayuda, gamma=0, gamma=4.9e-324 y beta=0.299999/gamma=0.30.

Las pruebas incluyen limites de N/I0/beta/gamma/pasos/contactos, valores casi iguales, cero, uno, NaN/infinito, desbordamientos numericos, opciones CLI invalidas y repetidas, semillas largas, rutas con espacios/comillas/Unicode, reproducibilidad, invariantes de SIR, archivos vacios/corruptos/grandes, UTF-8 incorrecto, transiciones imposibles, conservacion del escenario anterior, exportacion CSV/PNG/parametros, dos exportaciones simultaneas, reservas de archivo, escenarios con distintos horizontes y controles reales de la ventana.

Se probaron ademas 1000 semillas del escenario base y 500 escenarios aleatorios validos, agrupados en pruebas de propiedades. Cada trayectoria se comprobo por sus reglas de conservacion y transiciones, no mediante una grafica inventada. Los casos de rechazo solo pasan si efectivamente se produce el rechazo esperado.

Las graficas exportadas por NetLogo se contrastan punto por punto con las tres columnas del CSV principal. En el escenario base hay 303 valores S/I/R, mas sus tiempos. La semilla 42 mantiene el final S=4/I=0/R=96 y el pico de 49 infectados en t=20; la semilla 7 mantiene S=9/I=0/R=91.

El entorno de verificacion fue Linux, Java Temurin 21.0.13 y NetLogo 7.0.4. Las pruebas graficas accionaron los botones reales de Swing en una pantalla virtual X11. La captura se reviso visualmente. Esto no equivale a probar cada distribucion de Linux, cada controlador grafico o la version exacta de Java del estudiante.

## Cumplimiento del proyecto

| Requisito | Estado y limite de la afirmacion |
|---|---|
| SIR con los parametros de la guia | Incluido como escenario base; probabilidades discretas, no solucion diferencial |
| Algoritmo por individuos con copia de estados | Implementado en Java; no se altero la trayectoria base de la version anterior |
| CSV de Java y lectura en NetLogo | Incluidos y comprobados |
| Graficas S/I/R y comparaciones | Cinco paneles NetLogo: A, B y comparaciones S/I/R. B es otro CSV Java |
| Cambio de escenarios | Terminal y campos de interfaz; beta, gamma, N, I0, pasos y semilla |
| Graficas de cada ejecucion | Cada ejecucion Java guarda su propio CSV, PNG y parametros |
| MVC, POO y estrategia de exportacion | Conservados; reglas separadas de vistas y exportacion |
| Tiempo de ejecucion | Medicion real de pasos y registro en `.properties`; excluye creacion inicial de poblacion, archivos y vistas |
| Comparacion entre herramientas | Se puede explicar que Java genera y NetLogo importa/visualiza. Dos CSV Java no son dos implementaciones independientes |
| Python | Excluido por la asignacion indicada por el grupo |
| Modelo SIR autonomo en NetLogo | Excluido por instruccion expresa: NetLogo solo importa. La guia tambien lo enumera en resultados esperados; esa diferencia debe aclararse al evaluar |
| Tabla de ventajas/limitaciones, siete etapas, preguntas de control | Pendientes del documento academico; no se rellenan aqui como si ya se hubieran entregado |
| Documento, video y exposicion | Fuera del encargo actual, pendientes |

## Nota y limitaciones

La rubrica dedica 3 puntos a implementacion, 4 a defensa/demostracion y 3 al documento, incluido el video. Por eso un ZIP por si solo no demuestra 10/10 ni permite asegurar una nota total. La rubrica menciona M/M/1, mientras que el procedimiento y los parametros describen SIR; esta discrepancia existe en la guia.

El objetivo tecnico es el nivel Bien de implementacion (3/3), sujeto a que el docente acepte el alcance Java-generador/NetLogo-visualizador comunicado por el grupo. Una estimacion de QA no es una calificacion oficial. La version anterior presentaba defectos observables y no justificaba asegurar el maximo nivel antes de corregirlos.

Pasar estas pruebas no significa ser imposible de romper. No se certifican cortes de energia, cierre forzado, disco lleno durante una escritura final, corrupcion externa de bibliotecas o archivos mientras se utilizan, dispositivos defectuosos, todos los permisos posibles ni instalaciones modificadas de NetLogo. Ante archivos invalidos y entradas fuera del alcance comprobado, se busca un error controlado que conserve el trabajo anterior.

Para aspirar al total, faltan el documento en el formato del docente, siete etapas, preguntas de control, tabla comparativa basada en la experiencia, graficas/evidencias y analisis; video de al menos cinco minutos segun los apuntes; enlaces de Git y video, prompt y declaracion de IA en anexos; y defender individualmente algoritmo, parametros, escenarios y resultados. No se oculta la asistencia sustancial de IA ni se afirma un porcentaje no medido.
