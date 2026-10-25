# Pruebas de APE02

Desde `02APE`, con el entorno del proyecto activado, instala las dependencias
de la práctica y `pytest` para desarrollo:

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
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
`KeyboardInterrupt` durante distintas fases de lectura. También comprueba que
la opción retirada `11` permite recuperar el menú y que los argumentos de la
integración retirada se rechazan con un error de uso.

Las pruebas del dominio y de las gráficas se ejecutan localmente. El programa
usa Python, NumPy y Matplotlib; `pytest` solo se necesita para ejecutar esta
suite. Los resultados comprobados y sus comandos se registran en
`../VALIDACION.md`.
