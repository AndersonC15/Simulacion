# Visualización con NetLogo

`poblacion.nlogox` es un modelo XML para NetLogo **7.0.4**, la versión cargada
realmente durante la validación. Dibuja las series recibidas; no contiene las
ecuaciones poblacionales ni genera otra trayectoria aleatoria. No crea tortugas:
se usan únicamente gráficas, independientemente de la población matemática.

El recorrido es `Python → pynetlogo.NetLogoLink → JVM → NetLogo`. La distribución
pip se llama `pynetlogo`; la versión comprobada es **0.5.2** y su importación es
`import pynetlogo`, en minúsculas. Esta versión depende realmente de NumPy,
pandas y JPype1; SciPy no figura en su metadata de dependencias. JPype1 comprobado:
**1.7.1**. Se probó Python **3.14.4**, Linux **x86_64**, Java incorporado a NetLogo
**17.0.2** y NetLogo **7.0.4**. El sistema también tiene Java **21.0.12.1**;
el puente prefiere la JVM incorporada cuando encuentra su biblioteca.

Desde `02APE`, después de instalar `../02APE/requirements.txt` en el entorno:

```bash
export NETLOGO_HOME="/ruta/a/NetLogo 7.0.4"
.venv-ape02/bin/python main.py --netlogo --salida resultados
```

También se admite `--netlogo-home "/otra/ruta con espacios/NetLogo 7.0.4"`.
Si no se configura la ruta, se buscan instalaciones en `~/Aplicaciones`,
`~/Applications` y `/opt`. Si se encuentra más de una, se pide seleccionar la
ruta explícitamente. No se fija una ruta privada como única posibilidad.
La variable opcional `NETLOGO_JVM_PATH` permite indicar directamente `libjvm.so`,
`libjvm.dylib` o `jvm.dll`. Java y NetLogo son instalaciones externas a pip.

El modo sin ventana crea el plot real y exporta sus datos a un CSV. Este CSV es
un resultado adicional: la integración no se limita a escribir un archivo.
El puente carga el modelo, transmite parámetros y series, ejecuta `representar`
y consulta todos los tiempos, poblaciones, observaciones, parámetros y escenario
para compararlos con el envío. También recupera las versiones y comprueba
`count turtles = 0`. Los archivos existentes se rechazan para conservarlos.
Los datos del CSV coinciden al repetir el experimento; su cabecera incluye la
fecha de exportación y por tanto no se promete igualdad binaria entre archivos.

Para probar una ventana real, cuando existe escritorio y permiso de acceso:

```bash
.venv-ape02/bin/python main.py --netlogo-gui --salida resultados
```

La ventana se mantiene cinco segundos después de recibir y verificar el
experimento y se exporta una captura PNG. La API permite de 5 a 30 segundos.
El tiempo máximo total por envío es 90 segundos, configurable en la API hasta
300. La JVM tiene un límite de heap de 768 MiB; se aceptan hasta 100000 puntos
totales de transporte y se valida el límite antes de convertir listas.

Cada envío usa un proceso auxiliar nuevo. Sin ventana se llaman
`kill_workspace()` y `jpype.shutdownJVM()`. En las pruebas de la interfaz,
`kill_workspace()` de pyNetLogo 0.5.2 se bloqueó en `Frame.dispose()`: por eso
el proceso de GUI termina explícitamente después de escribir y cerrar su
respuesta, liberando JVM y ventanas mediante el sistema operativo. Un timeout
también termina el proceso auxiliar. El proceso de consola nunca inicia una
JVM y puede repetir envíos o continuar calculando después de un error.

Las poblaciones y tiempos Decimal se convierten a double exclusivamente aquí.
Se rechazan infinitos, subdesbordamiento a cero, error relativo mayor que
`1e-12` y tiempos distintos que se fusionarían al convertirlos. Los parámetros
se reciben además como texto para preservar sus decimales y semillas enteras.
Las conversiones no se reutilizan para calcular nuevas poblaciones. Euler
puede tener más puntos que las recurrencias: se consulta cada serie por separado
para evitar el fallo de pyNetLogo 0.5.2 al convertir listas anidadas de longitudes
distintas. Las listas vacías se consultan sin invocar su conversor defectuoso.

Pruebas desde `02APE`:

```bash
.venv-ape02/bin/python -m pytest -q tests/test_netlogo.py
APE02_PROBAR_NETLOGO=1 .venv-ape02/bin/python -m pytest -q tests/test_netlogo.py
```

La primera orden ejecuta 38 casos de la frontera y omite 7 pruebas externas.
La segunda añade 7 pruebas con una instalación real, incluyendo el experimento
oficial de cuatro series, repeticiones, horizonte cero, mallas distintas,
modelo inválido, ruta JVM inválida, timeout, archivos existentes y rutas con
espacios. Las pruebas externas no son mocks. Los resultados finales y la
comprobación separada de la GUI se registran en `../VALIDACION.md`.

Si falta NetLogo, hay una ruta incorrecta, falla Java, el modelo no carga o se
agota el tiempo, se muestra `ErrorNetLogo` y continúan disponibles los cálculos
y las gráficas de Python. Un escritorio inaccesible puede dar errores de AWT:
el modo sin ventana sigue funcionando. Windows, macOS y otras versiones de
NetLogo no se comprobaron durante esta implementación.

Fuentes primarias consultadas para contrastar la instalación:

- [API de pyNetLogo](https://pynetlogo.readthedocs.io/en/latest/_docs/pynetlogo.html).
- [Requisitos de NetLogo](https://docs.netlogo.org/requirements).
- [Gráficas en NetLogo](https://docs.netlogo.org/programming.html#plotting).
- [JPype: no se puede reiniciar una JVM cerrada](https://jpype.readthedocs.io/en/latest/api.html#jpype.shutdownJVM).

La firma instalada de 0.5.2 usa `jvmargs`; se inspeccionó el código instalado
para resolver la diferencia con documentación que muestra `jvm_args`.
