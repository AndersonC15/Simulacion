# Modelo

`datos.py` contiene exactamente las nueve mediciones de la guía.
`modelo.py` define `RegistroMeteorologico`, `ParametrosModelo`,
`ResultadoLluvia` y `ModeloLluvia`, junto con las operaciones de normalización,
interpolación y clasificación. Los registros y parámetros se validan al
construirse y son inmutables.

`precision.py` convierte texto a Decimal sin float y deriva la precisión de
cada suma y producto. Las trampas Inexact y Rounded detectan redondeos. Los
pesos deben sumar exactamente uno. Los límites de captura (256 caracteres,
120 dígitos de coeficiente, exponentes entre −120 y 120) se aplican a las
mediciones y pesos; los resultados internos pueden necesitar más posiciones.
La temperatura de entrada se limita a [−50,60] °C por decisión de la aplicación.

El modelo no depende de consola, controlador, NumPy ni Matplotlib. No usa
input, print o gráficos. Las fórmulas, intervalos y justificación de precisión
se explican en el [README principal](../README.md).
