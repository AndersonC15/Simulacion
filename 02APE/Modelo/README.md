# Dominio de la comparación poblacional

Esta carpeta no captura entradas, imprime resultados ni dibuja. Trabaja con
Decimal y devuelve objetos de resultados para que el controlador y las
vistas decidan cómo presentarlos.

| Archivo | Responsabilidad |
|---|---|
| `datos.py` | Arreglo oficial, validación de observaciones y formato seguro con `;`. |
| `parametros.py` | Objeto inmutable `Parametros`, valores manuales predefinidos y restricciones comunes. |
| `analisis.py` | Varias semillas emparejadas por nivel de sigma y resúmenes de población final. |
| `estimacion.py` | Media de tasas relativas y desviación poblacional centrada de residuos; son estimaciones descriptivas. |
| `numeros.py` | Conversión directa a Decimal, aritmética exacta acotada y errores comprensibles. |
| `tiempo.py` | Mallas por índices y cociente racional; último paso Euler reducido. |
| `estrategias.py` | Contrato `EstrategiaSimulacion` y clases exponencial, discreta, estocástica y Euler. |
| `resultados.py` | `Serie` y `Experimento`, con tuplas y datos inmutables. |

Cada estrategia recibe `Parametros` y devuelve `Serie`. El exponencial usa
`exp(r*t)`; el discreto actualiza `P+rP`; el estocástico añade ruido y aplica
`max(0,...)`; Euler usa `P+h*rP`. El estocástico crea un generador NumPy local
con semilla; las pruebas pueden inyectar ruido controlado. Las reglas no
importan gráficos ni NetLogo.

Las operaciones finitas exactas tienen hasta 10000 dígitos y trampas de pérdida
activa; exp, estimación, raíz y ruido tienen fronteras aproximadas documentadas.
La [política completa](../README.md#precisión-estabilidad-y-límites) distingue
precisión de entrada y de cálculo. El [registro de validación](../VALIDACION.md)
contiene referencias numéricas y pruebas adversas.
