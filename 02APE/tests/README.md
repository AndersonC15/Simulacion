# Pruebas de APE02

Desde `02APE`, con el entorno del proyecto activado:

```bash
python -m pytest -q
python -m pytest --collect-only -q
```

El segundo comando cuenta los casos recolectados. Cada combinación declarada
con `pytest.mark.parametrize` es un subcaso: comprueba un valor, una condición
matemática o una entrada adversa distinta. No se cuentan las aserciones internas
como pruebas adicionales.

`test_adversarios.py` contrasta las recurrencias con `fractions.Fraction` y la
exponencial con un contexto `Decimal` de 100 dígitos. Comprueba conservación de
decimales, disminución del error de Euler en casos regulares, extremos de las
mallas, restricciones de positividad, parámetros incompatibles y límites antes
de reservar arreglos. También verifica estimación con todas las observaciones,
reproducibilidad, aislamiento del estado aleatorio global y ruido controlado.
La prueba de dispersión usa cinco realizaciones simétricas por nivel de sigma;
no deduce tendencias de población a partir de una sola trayectoria.
Los casos del controlador verifican configuración común, reutilización del
experimento guardado y conservación del estado cuando falla una modificación.

`test_consola.py` ejercita el menú mediante entradas inyectadas y verifica
salida, recuperación de errores, fin de entrada y cancelación. Los comandos y
resultados de la ejecución completa se registran en `../VALIDACION.md`.
También ejecuta procesos reales para comprobar EOF, comparación y exportación
gráfica desde directorios con espacios. Comprueba el análisis de ruido mediante
la opción `a` del menú y `--analizar-ruido` en la terminal. En POSIX envía una
señal SIGINT real al subproceso cuando espera una opción; además inyecta
`KeyboardInterrupt` durante distintas fases de lectura.

Las comprobaciones de un puente simulado no acreditan comunicación real con
NetLogo. La prueba de integración real y los requisitos externos se documentan
por separado en `../VALIDACION.md`.

La ejecución final incluyó 398 casos aprobados, con NetLogo habilitado. Sin
`APE02_PROBAR_NETLOGO=1` se ejecutan 391 y se omiten las 7 pruebas externas.
El desglose y los comandos del entorno limpio están en VALIDACION.md.
