# Modelo

Esta carpeta contiene la lógica matemática y los datos de entrada.

- `datos.py`: nueve registros horarios entregados en la guía.
- `modelo.py`: normalización, tabla del factor térmico, cálculo y clasificación
  del índice, además de los parámetros original y ajustado.

El modelo no imprime ni dibuja resultados. `ParametrosModelo` rechaza pesos
negativos o cuya suma no sea 1.0.
