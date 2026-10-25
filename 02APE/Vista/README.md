# Adaptadores de visualización

La vista de consola está en `../main.py`. Esta carpeta adapta un `Experimento`
ya calculado a Matplotlib y a NetLogo; no recalcula las ecuaciones ni genera
otra realización estocástica.

- `graficas.py`: `VistaGraficas.guardar` convierte a float únicamente para
  dibujar. Distingue observaciones, escalones discretos, ruido y Euler, genera
  PNG y exporta CSV con los valores Decimal como texto. Usa un directorio de
  resultados explícito o `../resultados`, reemplaza archivos mediante
  temporales y cierra figuras incluso ante errores.
- `puente_netlogo.py`: valida instalación, modelo, rutas, conversiones y
  límites; transmite las mismas series mediante un proceso auxiliar y
  comprueba el retorno de parámetros y resultados.
- `worker_netlogo.py`: inicia pyNetLogo/JPype, carga realmente el modelo,
  ejecuta comandos, consulta reporters y exporta opcionalmente. Sin GUI cierra
  workspace/JVM; con GUI termina el proceso aislado después de guardar la
  respuesta para evitar el bloqueo observado en `Frame.dispose()`.
  Es un proceso privado; no se invoca directamente como interfaz pública.

El puente comprueba pérdida relativa de conversión a double con tolerancia
1e−12 y rechaza infinitos, subdesbordamiento a cero o tiempos que se fusionen.
Esa tolerancia pertenece a la visualización; no sustituye los datos Decimal del
dominio. No se crea un agente por habitante. Cada envío tiene su proceso/JVM
para que repetirlo no intente reiniciar una JVM dentro del proceso principal.

Configuración, API de uso y requisitos externos en
[README principal](../README.md#netlogo-desde-python) y
[netlogo/README.md](../netlogo/README.md). La evidencia real y las limitaciones
de las ventanas están en [VALIDACION.md](../VALIDACION.md).
