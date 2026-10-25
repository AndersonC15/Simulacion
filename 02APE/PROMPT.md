# Registro del encargo y uso real de IA

Fecha de la sesión: 24 de octubre de 2026 (America/Guayaquil).

El usuario adjuntó el encargo reproducido abajo y añadió literalmente:
**«NO ALUCINES»**. No se inventan prompts anteriores de otras sesiones.

Codex inspeccionó Git, los archivos actuales y la guía PDF local mediante
`pdftotext`; implementó el dominio, controlador, consola, gráficas e integración,
escribió y ejecutó pruebas, investigó fallos, preparó documentación y manifiestos
y realizó los commits/pushes autorizados. Tres agentes auxiliares de Codex
trabajaron en integración NetLogo, QA independiente y documentación/Maven del
portafolio. Sus tareas técnicas fueron: verificar versiones/API y retorno real
de las mismas series; contrastar matemática con Fraction/Decimal de mayor
precisión y entradas adversas; inspeccionar imports y validar otros proyectos
en copias temporales sin cambiar sus algoritmos. No son encargos históricos
ni instrucciones adicionales atribuidas al usuario.

Se consultó documentación primaria de pyNetLogo/NetLogo; los enlaces y versiones
están en netlogo/README.md. No se recibieron diapositivas adicionales en el
equipo y no se afirma haberlas leído. La guía local y este encargo sustentan
las decisiones académicas. VALIDACION.md distingue pruebas reales, simuladas,
limitaciones y plataformas no comprobadas.

La implementación nueva y buena parte de las pruebas y documentación fueron
producidas con asistencia de IA. No se calcula un porcentaje de autoría: contar
líneas no lo demuestra. El estudiante todavía debe revisar, ejecutar y poder
explicar los archivos antes de entregar. No se atribuye una revisión humana
ya realizada ni una aprobación del docente.

## Encargo adjunto, transcripción íntegra

Necesito que implementes desde cero mi práctica 02 de Simulación, trabajando sobre mi repositorio real. Después debes completar la documentación y los manifiestos de dependencias del portafolio.

Realiza la implementación, ejecútala, prueba sus errores y corrige los problemas encontrados. No te quedes únicamente en recomendaciones.

Soy estudiante de quinto ciclo de Computación. Necesito una solución correcta que pueda comprender y explicar ante mi docente.

**1. Repositorio, alcance y comprobación inicial**

Repositorio: [AndersonC15/Simulacion](https://github.com/AndersonC15/Simulacion.git)

La ruta previamente utilizada en mi equipo es:

`/home/anderson-coello/Escritorio/WorkSpace-QUINTOCICLO/Simulacion/APEs-Simulacion`

Verifica la ubicación real mediante Git. La terminal podría estar abierta dentro de una subcarpeta.

Antes de modificar:

- Lee los `AGENTS.md` aplicables.
- Comprueba raíz, rama, remoto, HEAD, estado del índice y cambios existentes.
- Confirma que `origin` corresponde al repositorio indicado.
- Conserva los cambios del usuario.
- Inspecciona los archivos actuales; no dependas de una revisión antigua.
- Lee la guía de la semana 2 que está dentro de `02APE`.
- Consulta la documentación existente de las otras prácticas para respetar su funcionamiento.

El trabajo tiene dos alcances separados:

A. Implementar `02APE` mediante diez commits exclusivos de esa carpeta.

B. Crear un commit adicional para los README y manifiestos necesarios del resto del portafolio, incluido el README general.

En el alcance B no debes refactorizar ni cambiar la lógica matemática de `01APE`, `03APE-Grupal` o `04APE-Grupal`.

No reorganices ni elimines `Practica4`, archivos ZIP u otras copias del usuario para “limpiar” el repositorio.

**2. Fuentes académicas y requisitos**

El título de APE02 es:

“Comparación de modelos determinísticos, estocásticos, discretos y continuos”.

La guía utiliza crecimiento poblacional y pide:

- Implementación de cuatro modelos en Python.
- Uso del arreglo de datos proporcionado.
- Comparación gráfica de los modelos.
- Gráficas de crecimiento y decrecimiento.
- Análisis de la influencia de `r`.
- Análisis del efecto de la aleatoriedad.
- Interpretación matemática.
- Conexión con NetLogo mediante pyNetLogo.
- Implementación del pseudocódigo.
- Respuestas a las preguntas de control.

Mis requisitos adicionales son:

- Arquitectura MVC.
- Programación orientada a objetos.
- Un patrón de diseño justificado.
- Clean Code.
- Aplicación proporcional de SOLID.
- Validaciones en el dominio y en las entradas.
- Precisión numérica documentada.
- Pruebas reproducibles.
- README que permita al docente descargar y ejecutar el proyecto.
- Registro del prompt y del uso real de IA.

Las diapositivas explican que tiempo, aleatoriedad y forma de evolución son dimensiones diferentes. No describas los cuatro modelos como categorías mutuamente excluyentes: el discreto puede ser determinístico y el estocástico de esta guía también avanza por períodos.

El modelo continuo es continuo matemáticamente; Euler es una aproximación numérica con pasos discretos.

Las diapositivas de teoría de colas sirven como contexto de la materia. No conviertas APE02 en otro simulador M/M/1 ni copies lógica de otras prácticas.

Si alguna diapositiva adjunta al chat no está disponible en el equipo, no afirmes haberla leído. Usa la guía local y los requisitos explícitos de este encargo, y documenta cualquier ambigüedad restante.

**3. Modelos matemáticos obligatorios**

Implementa estas ecuaciones y sus pseudocódigos:

Modelo determinístico:

`P(t) = P0 × exp(r × t)`

Modelo discreto:

`P[k+1] = P[k] + r × P[k]`

Modelo estocástico:

`P[k+1] = max(0, P[k] + r × P[k] + epsilon[k])`

con:

`epsilon[k] ~ Normal(0, sigma²)`

Aquí `sigma` es la desviación estándar. No pases `sigma²` como desviación estándar al generador normal.

Modelo continuo mediante Euler:

`dP/dt = r × P`

`P(t+h) = P(t) + h × r × P(t)`

La restricción de población negativa a cero pertenece al pseudocódigo estocástico. No la uses para ocultar un paso de Euler inválido ni para modificar silenciosamente los otros modelos.

Datos oficiales:

`[1000, 1100, 1250, 1400, 1600, 1850, 2100]`

Interpreta inicialmente los tiempos como `0, 1, 2, 3, 4, 5, 6`, en períodos. La guía no especifica años, días o meses.

El arreglo contiene observaciones de referencia, no siete condiciones iniciales independientes ni valores que deban copiarse como resultados simulados.

**4. Parámetros y decisiones de implementación**

La guía no fija un procedimiento concreto para obtener `r`, `sigma`, `dt` o la semilla. Debes distinguir lo solicitado por el docente de las decisiones de implementación.

Para el arreglo oficial:

- Usa el primer valor como `P0`.
- Usa seis períodos como horizonte inicial.
- Utiliza todos los datos al estimar parámetros automáticamente.
- Permite consultar los parámetros y modificarlos desde el menú.
- Conserva una configuración predefinida dentro del modelo o su configuración del dominio.

Como opción inicial sencilla para estimar `r`, puedes emplear la media de las tasas relativas entre observaciones consecutivas:

`r = media((P[i+1] - P[i]) / P[i])`

Si eliges otro método, explica su fórmula, motivo y consecuencias.

Para estimar `sigma`, puedes utilizar una medida descriptiva de dispersión de los residuos de la recurrencia discreta:

`residuo[i] = datos[i+1] - (1+r) × datos[i]`

Explica qué estimador utilizas y sus limitaciones. No lo presentes como un valor oficial ni como una calibración científicamente validada.

Puedes adoptar `dt = 0.1` y semilla `42` como decisiones iniciales reproducibles. Identifícalas expresamente como decisiones de la implementación.

La estimación automática debe detectar datos insuficientes y divisiones entre cero. Cuando un arreglo impida estimar parámetros, permite una configuración manual válida o explica por qué no puede utilizarse ese modo.

Incluye escenarios identificados de:

- Crecimiento.
- Decrecimiento.
- Población constante.

Usa configuraciones comparables y explica por qué se modificaron sus parámetros. No inventes escenarios “oficiales”.

Conserva las ecuaciones de la guía. Si utilizas el mismo valor numérico de `r` en el modelo exponencial y en la recurrencia discreta, explica que sus interpretaciones no son idénticas y que no tienen por qué coincidir.

**5. MVC, POO y patrón de diseño**

Respeta especialmente estas indicaciones del docente:

- `Modelo` debe ser una carpeta.
- `main.py` debe actuar como la vista de consola.

Una estructura posible es:

- `Modelo/`: datos, parámetros, resultados, estimación y modelos matemáticos.
- `Controlador/`: coordinación de ejecuciones y experimentos.
- `Vista/`: gráficas y adaptación de la visualización.
- `netlogo/`: modelo y recursos de NetLogo.
- `tests/`: pruebas.
- `main.py`: vista de consola y arranque.
- `README.md`.
- `PROMPT.md`.
- `VALIDACION.md`.
- `requirements.txt`.

Puedes ajustar los nombres de los módulos si mejora la claridad.

En `main.py` pueden estar la clase de vista de consola, el menú, la lectura de entradas y la presentación de tablas. No coloques allí las ecuaciones, la estimación de parámetros ni el generador de ruido.

El modelo no debe importar la vista, imprimir, pedir datos ni abrir ventanas.

El controlador recibe solicitudes y coordina el modelo. La vista presenta los resultados devueltos.

Usa objetos para parámetros y resultados cuando corresponda. Evita diccionarios con claves inconsistentes y listas cuyo significado no esté documentado.

Los cuatro algoritmos permiten aplicar Strategy mediante un contrato pequeño de simulación. Utilízalo si resulta una separación real y explica dónde se selecciona la estrategia. No añadas patrones decorativos, fábricas innecesarias o jerarquías difíciles de justificar.

Aplica SOLID con decisiones concretas y proporcionales. No afirmes cumplir sus cinco principios sin explicar lo que el código demuestra.

**6. Política de precisión**

No quiero redondeos intermedios ni pérdidas silenciosas de los decimales admitidos.

Sin embargo, debes reconocer que:

- `exp`, logaritmos y raíces suelen requerir aproximaciones numéricas.
- Euler aproxima una ecuación diferencial.
- Los generadores pseudoaleatorios tienen precisión finita.
- NetLogo y las bibliotecas gráficas pueden utilizar números de precisión limitada.

No prometas resultados exactos infinitos.

Define una política explícita:

- Lee las entradas numéricas sin convertirlas primero a `float` si se conservarán como Decimal.
- Usa constantes decimales construidas desde texto.
- Conserva los datos originales.
- Evita `round()`, `quantize()` y formatos de pocos decimales dentro de los cálculos.
- Evita convertir una población a entero solo por tratarse de una población matemática.
- Controla la precisión del contexto Decimal cuando lo utilices.
- Distingue operaciones exactas posibles de operaciones aproximadas.
- Comprueba las aproximaciones con una referencia de mayor precisión o con tolerancias justificadas.
- No conviertas un `float` a Decimal y afirmes que recuperaste precisión perdida.

Puedes utilizar NumPy para el generador normal, dejando explícita esa frontera numérica. Usa un generador local reproducible; no alteres el estado aleatorio global.

No reutilices datos redondeados de una tabla, gráfica o NetLogo para continuar los cálculos.

Las tablas deben mostrar los resultados con su precisión de cálculo documentada, sin imponer `.2f` o `.3f` para ocultar diferencias. Controla su presentación sin destruir datos.

Las conversiones necesarias para Matplotlib o NetLogo deben estar aisladas en la visualización.

Establece límites amplios pero finitos para longitud de entrada, exponentes, precisión y cantidad de puntos. Rechaza claramente lo que los exceda. No recortes las entradas para aceptarlas.

**7. Tiempo, Euler y validaciones matemáticas**

Construye las mallas temporales sin acumulación descontrolada de errores.

Comprueba:

- Tiempo inicial incluido.
- Horizonte final incluido.
- Igual longitud de tiempos y poblaciones.
- Tiempos estrictamente crecientes cuando hay varios puntos.
- Ningún punto posterior al horizonte.
- Horizonte cero con un único estado inicial.
- Paso mayor que el horizonte.
- Horizonte no divisible entre `dt`.

En Euler puedes utilizar un último paso reducido para terminar exactamente en el horizonte. Documenta esa decisión.

Evita un `while` que no avance porque el paso sea demasiado pequeño respecto a la precisión utilizada.

Valida los parámetros según el modelo:

- `P0` no negativo y finito.
- `sigma` no negativo y finito.
- `dt` positivo y finito.
- Horizonte válido para la forma de simulación elegida.
- Semilla válida para el generador utilizado.
- Tasa finita.
- Cantidad de pasos dentro de límites de recursos.

No rechaces toda tasa negativa: se necesita simular decrecimiento.

Para la recurrencia discreta, controla cuándo `1+r` produciría poblaciones negativas.

Para Euler con decrecimiento, controla la condición de positividad del paso y las condiciones numéricas relevantes. No presentes oscilaciones o poblaciones negativas causadas por un paso inadecuado como comportamiento físico válido.

Detecta resultados no finitos, desbordamientos y pérdidas numéricas relevantes. Devuelve errores comprensibles sin sustituir el resultado por un cero ficticio.

**8. Menú y resultados**

Implementa una vista de consola que permita:

- Ejecutar cada uno de los cuatro modelos.
- Comparar los cuatro con una configuración común.
- Mostrar el arreglo y los parámetros utilizados.
- Modificar parámetros.
- Utilizar escenarios de crecimiento, decrecimiento y constancia.
- Introducir otro arreglo.
- Mostrar las gráficas.
- Enviar un experimento a NetLogo.
- Salir limpiamente.

No es necesario crear una aplicación web ni una interfaz de escritorio completa.

Para ingresar arreglos, utiliza un formato claro y seguro. No uses `eval()`. Distingue los separadores de elementos de los separadores decimales.

Las cuatro series de un mismo experimento deben corresponder a la misma configuración y a la misma realización estocástica cuando se muestran en distintos lugares.

No generes otra trayectoria aleatoria silenciosamente al enviarla a NetLogo o volver a presentar una gráfica.

Explica cómo leer los resultados y por qué los modelos difieren.

**9. Gráficas e integración real con NetLogo**

La comparación debe mostrar los cuatro modelos, con título, ejes Tiempo/Población, leyenda y cuadrícula.

Distingue visualmente las observaciones de referencia de las series simuladas.

Representa adecuadamente los puntos o escalones del modelo discreto y etiqueta Euler como aproximación.

Deja disponibles comparaciones de crecimiento y decrecimiento. Guarda imágenes reproducibles en una carpeta documentada.

No inventes una cantidad de gráficas exigida por el docente. Implementa las necesarias para demostrar los resultados pedidos.

Comprueba el funcionamiento con y sin escritorio gráfico y cierra las figuras al terminar.

La guía incluye expresamente Python → pyNetLogo → NetLogo. Implementa y verifica ese puente; un CSV aislado no sustituye esta integración.

Python debe calcular las series y generar los parámetros. NetLogo debe recibir los parámetros y visualizar coherentemente el experimento.

Una solución válida es transmitir también los resultados calculados en Python, de modo que NetLogo los reproduzca. Documenta esta decisión y evita generar una segunda trayectoria estocástica diferente en NetLogo.

No crees un agente por habitante si eso puede agotar recursos. Usa una representación visual limitada e identifica su significado.

Antes de elegir formato y API:

- Detecta la instalación real de NetLogo y Java.
- Comprueba la versión real de pyNetLogo y el nombre correcto de su módulo.
- Consulta documentación primaria cuando sea necesario.
- Configura rutas sin fijar la ruta privada de mi equipo como única posibilidad.
- Comprueba compatibilidad entre Python, JVM, NetLogo y arquitectura del sistema.
- Usa un archivo de modelo compatible con la versión probada.

Carga realmente el modelo, transmite valores, ejecuta comandos y recupera al menos un resultado que permita comprobar la comunicación.

Gestiona NetLogo ausente, ruta equivocada, modelo inválido, fallo de inicio y cierre de la sesión.

La ausencia de NetLogo no debe impedir utilizar los cálculos y gráficas de Python. Sin embargo, si no puedes probar el puente real, deja esa parte marcada como pendiente; no declares cumplimiento completo basándote en mocks.

Evita reiniciar incorrectamente una JVM dentro del mismo proceso. Si la integración requiere aislamiento para controlar fallos o tiempos de espera, utiliza una solución sencilla y justificada.

**10. QA: intenta provocar fallos y corrígelos**

Necesito pruebas con aserciones útiles y resultados reproducibles. Implementa las pruebas junto con las funcionalidades; no esperes al final para comprobar todo.

Ejemplos matemáticos mínimos:

- `P0=1000`, `r=0`: determinístico, discreto y Euler deben permanecer en 1000.
- `sigma=0`: el estocástico debe coincidir con el discreto cuando ambos usan condiciones válidas.
- Euler con `dt=1` debe coincidir con la recurrencia discreta en los mismos períodos.
- `P0=1000`, `r=0.1`, un período: el discreto termina en 1100.
- Con esos parámetros, Euler con dos pasos de 0.5 termina en 1102.5.
- El exponencial termina aproximadamente en 1105.1709180756476…, comprobado con una referencia de precisión suficiente.
- En un caso regular, reducir el paso de Euler debe acercar el resultado a la solución exponencial.
- Una secuencia de ruido controlada debe permitir comprobar exactamente la recurrencia y la restricción a cero.

Comprueba reproducibilidad con la misma semilla y aislamiento del generador.

No escribas pruebas que exijan que dos semillas diferentes siempre produzcan resultados diferentes. Tampoco exijas que una población estocástica siempre crezca con `r>0`.

Con ruido aditivo, una población que llegó a cero puede volver a aumentar. No conviertas el cero en un estado absorbente si la ecuación no lo establece.

Analiza el efecto de aumentar sigma mediante varias realizaciones controladas. No concluyas que aumenta o disminuye la población a partir de una sola curva.

Comprueba entradas vacías, texto, espacios, coma y punto decimal, formatos ambiguos, negativos inválidos, NaN, infinitos, exponentes extremos, arreglos vacíos, datos insuficientes, ceros, entradas largas y parámetros incompatibles.

Prueba también llamadas directas al modelo, no solo el menú.

Prueba opciones inexistentes, recuperación después de errores, EOF y Ctrl+C.

Comprueba rutas con espacios, ejecución desde la ubicación documentada, permisos de escritura, archivos de salida existentes y generación repetida de gráficos.

Comprueba límites de tiempo y memoria antes de reservar arreglos enormes. Los límites deben tener explicación y mensajes claros.

No captures indiscriminadamente todas las excepciones ni silencies fallos.

Ejecuta al menos 100 casos o subcasos significativos entre matemática, invariantes y entradas adversas. No infles la cantidad con comprobaciones triviales o duplicadas. Identifica cómo los contaste.

Antes de terminar realiza cinco revisiones distintas:

1. Cumplimiento de la guía, arquitectura y funcionalidad.
2. Exactitud, aproximaciones y estabilidad numérica.
3. Entradas adversas, recursos y recuperación.
4. Gráficas e integración real con NetLogo.
5. Instalación limpia, documentación, ejecución final e historial Git.

Si falla una comprobación, corrige el problema y repite las verificaciones afectadas.

No prometas haber probado todas las entradas posibles.

**11. Documentación de APE02**

Sigue estos componentes de un buen README:

- Descripción y propósito.
- Tecnologías y función de cada una.
- Instalación.
- Configuración.
- Uso con ejemplos.
- Estructura del proyecto.
- Información adicional relevante.

En `02APE/README.md` incluye también:

- Ecuaciones y correspondencia con el pseudocódigo.
- Origen e interpretación del arreglo.
- Parámetros y método de estimación.
- Decisiones que no están fijadas por la guía.
- Escenarios de crecimiento y decrecimiento.
- MVC, POO y patrón utilizado.
- Política de precisión.
- Uso de la semilla.
- Funcionamiento de NetLogo.
- Ubicación de resultados.
- Comandos reales de pruebas.
- Problemas frecuentes y limitaciones verificadas.
- Uso real de IA.

Responde brevemente las diez preguntas de control de la guía y relaciona las respuestas con el programa real.

Crea `PROMPT.md` registrando este encargo y las instrucciones adicionales realmente utilizadas. No inventes prompts históricos.

Crea `VALIDACION.md` con las cinco revisiones, comandos, resultados, errores corregidos y comprobaciones pendientes.

Añade README breves a las carpetas del proyecto que contengan código, pruebas, modelo de NetLogo o recursos que el docente necesite comprender.

No generes README dentro de `.git`, entornos virtuales, cachés o dependencias instaladas.

La declaración de IA debe reflejar lo que realmente hiciste. No afirmes automáticamente que se utilizó menos del 20 % ni que un contador de líneas demuestra ese porcentaje. Identifica los aportes para que yo pueda revisar el alcance antes de entregar.

**12. Dependencias y entorno virtual**

El nombre correcto es `requirements.txt`. No crees un `requirements.py` para simular un manifiesto de dependencias.

Antes de instalar bibliotecas:

- Crea o utiliza un entorno virtual adecuado para este proyecto.
- Comprueba qué intérprete estás utilizando.
- Ejecuta pip mediante ese intérprete: `python -m pip`.
- No instales globalmente.
- No alteres el entorno existente de otras prácticas.

La guía menciona NumPy, Matplotlib, pandas, SciPy y pyNetLogo. Determina las dependencias reales y las necesarias para el puente.

No añadas imports o funcionalidades artificiales solo para justificar bibliotecas.

Obtén el registro de versiones con `python -m pip freeze` desde un entorno limpio y revisa que el manifiesto no incluya bibliotecas ajenas. No sobrescribas el archivo con paquetes de todo un entorno compartido.

Comprueba la versión mínima real de Python y la compatibilidad de las versiones seleccionadas.

Java, NetLogo y las bibliotecas gráficas del sistema deben documentarse como requisitos externos; no inventes paquetes pip para instalarlos.

Prueba una instalación nueva con el archivo final.

No versiones `.venv`, `venv`, cachés, archivos del editor ni instalaciones de NetLogo o Java.

**13. Diez commits exclusivos de APE02**

Organiza el trabajo en diez avances reales. Esta secuencia es orientativa:

1. `Crear la estructura MVC y los datos de la APE02`
2. `Implementar el modelo determinístico de población`
3. `Agregar el modelo discreto`
4. `Agregar el modelo estocástico con semilla`
5. `Implementar el modelo continuo con Euler`
6. `Incorporar el menú y la comparación de modelos`
7. `Agregar las gráficas de crecimiento y decrecimiento`
8. `Conectar la visualización con NetLogo`
9. `Reforzar las validaciones y las pruebas del programa`
10. `Completar la documentación y las dependencias de la APE02`

Adapta los títulos si los cambios reales lo requieren.

Cada commit debe aportar algo verificable. Mantén una entrada ejecutable y evita introducir regresiones entre etapas. Las validaciones básicas y pruebas deben acompañar cada implementación, aunque después se amplíen.

No crees commits vacíos para completar el número ni afirmes que una etapa incompleta ya funciona.

Estos diez commits deben contener únicamente rutas de `02APE`.

**14. Commit adicional: documentación y manifiestos del portafolio**

Después de completar APE02, realiza un commit separado con un mensaje similar a:

`Actualizar los README y las dependencias del portafolio`

En ese commit:

- Actualiza el `README.md` general.
- Completa los README faltantes de las prácticas y sus carpetas relevantes.
- Revisa o completa `requirements.txt` en las tres primeras prácticas Python.
- Añade un `pom.xml` funcional para el proyecto Java de la práctica 4.
- Ajusta la documentación que deba reflejar esa incorporación.
- Completa las exclusiones de archivos generados que sean necesarias.

Conserva la documentación existente que sea correcta. No la reemplaces toda por textos genéricos.

El README general debe describir lo que realmente contiene cada práctica y enlazar su ubicación y sus instrucciones.

Como referencia de lo previamente inspeccionado:

- `01APE`: índice de lluvia.
- `02APE`: los cuatro modelos poblacionales de este encargo.
- `03APE-Grupal`: líneas de espera M/M/1 con SimPy.
- `04APE-Grupal/APE04_Java_NetLogo`: modelo SIR en Java y visualización con NetLogo.

Verifica esos contenidos antes de documentarlos. No describas APE04 como M/M/c si el código actual es SIR.

Corrige instrucciones heredadas que todavía mencionen carpetas de ZIP que no coincidan con las rutas reales del repositorio.

Para las prácticas anteriores, documenta sus dependencias reales sin cambiar sus algoritmos. No copies el mismo `requirements.txt` en todas.

No inventes usos históricos de IA, integrantes, autores, licencias, pruebas realizadas o capacidades inexistentes. Puedes documentar el apoyo real de IA en esta actualización de documentación y manifiestos.

**15. Maven para APE04**

Java no requiere Maven obligatoriamente, pero en este encargo sí quiero un `pom.xml` útil.

Ubícalo en la raíz del proyecto Java real, que debes verificar. No añadas un POM vacío.

Inspecciona los archivos Java y los scripts actuales. La versión previamente revisada utiliza fuentes en `src/sir`, entrada `sir.Main` y compilación con `--release 17`.

Si esa estructura continúa:

- Configura el directorio real de fuentes.
- Configura UTF-8.
- Selecciona una versión de Java compatible y comprobada.
- Configura el empaquetado y la clase principal.
- Comprueba `mvn clean package`.
- Comprueba cómo ejecutar el artefacto generado.
- Conserva el método de ejecución existente cuando siga siendo válido.

No reestructures todo el proyecto Java para ajustarlo a una plantilla Maven.

No añadas dependencias externas si el programa usa únicamente la biblioteca estándar.

Distingue la aplicación Java de la instalación externa de NetLogo.

No afirmes que `mvn test` ejecuta las pruebas existentes si son programas Java independientes y no están integrados con un ejecutor de pruebas.

Documenta por separado los comandos reales de esas pruebas y los requisitos de las pruebas que dependan de NetLogo.

Para validar los otros proyectos, evita sobrescribir sus resultados versionados. Utiliza copias temporales cuando sea necesario.

**16. Reglas para commits y pushes**

Está autorizado crear los diez commits de APE02 y el commit adicional de documentación/manifiestos, y hacer push al remoto correcto después de verificar cada avance.

Antes de cada commit:

- Revisa `git diff`.
- Añade rutas explícitas.
- Revisa los archivos preparados.
- Ejecuta las comprobaciones relevantes.
- Confirma que no incluyes cambios ajenos.

No utilices `git add .` desde la raíz ni `git commit -a` para incluir todo.

No alteres el índice ajeno ni reviertas cambios del usuario para facilitar tus commits.

No cambies identidad, autoría o fechas para simular trabajo. Utiliza mensajes sencillos en español que describan cambios reales.

No reescribas el historial, no hagas push forzado y no modifiques commits anteriores sin autorización.

Si falla un push, conserva los commits locales, informa la causa y no afirmes que el trabajo está publicado.

No necesitas detenerte entre etapas para solicitar confirmaciones rutinarias. Respeta los permisos del entorno y explica los bloqueos reales.

**17. Entrega final**

Responde en español indicando:

- Qué implementaste.
- Qué decisiones completaron ambigüedades de la guía.
- Cómo se cumplen MVC, POO y el patrón de diseño.
- Dónde se aplican las decisiones de SOLID.
- Política de precisión y límites.
- Comandos reales de instalación y ejecución.
- Cómo ejecutar NetLogo desde Python.
- Ubicación de gráficas y resultados.
- Pruebas ejecutadas y cantidad de casos.
- Fallos encontrados y correcciones.
- Resultado de las cinco revisiones.
- Documentación y manifiestos añadidos a otras prácticas.
- Hash y mensaje de los once commits previstos.
- Resultado de los pushes y estado final de Git.
- Comprobaciones pendientes o limitaciones reales.

Si no pudiste comprobar una plataforma, una ventana gráfica, Maven o el puente real de NetLogo, dilo expresamente.

No garantices una nota de 10/10, un porcentaje de IA ni que el programa sea imposible de hacer fallar. Sustenta el resultado con evidencia.

Empieza inspeccionando el repositorio y continúa hasta completar la implementación, las verificaciones y los commits autorizados.