# Práctica 01 — Construcción y simulación de un modelo matemático

Implementación en Python del modelo de índice de lluvia de la guía de Simulación:

`I = 0.5H + 0.3N + 0.2Tf`

El programa llena la tabla de los nueve horarios, clasifica cada índice, permite
probar un caso manual, compara el modelo original con uno ajustado y presenta
las gráficas. Se aplicó el patrón **Modelo–Vista–Controlador (MVC)**.

## Estructura

```text
01APE/
├── Modelo/             # Datos, reglas, fórmulas y parámetros
├── Controlador/        # Comunicación entre modelo y vistas
├── Vista/graficas.py   # Vista gráfica
├── main.py             # Vista principal de consola y punto de entrada
├── requirements.txt    # Dependencias de Python
├── PROMPT.md            # Prompt utilizado con IA
└── ape_guia simulacion semana 1.pdf
```

Cada carpeta del patrón contiene su propio README con su responsabilidad.

## Requisitos y ejecución

Se necesita Python 3.10 o posterior. No se instala con `pip` fuera de un entorno
virtual. Desde esta carpeta, ejecutar:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows, la activación es `.venv\Scripts\activate`. La opción 1 muestra la
tabla original, la 2 la ajustada y la 3 genera dos archivos PNG dentro de
`graficas_generadas/`. Si existe un backend interactivo, también abre ventanas.

Para regenerar el archivo de dependencias desde el entorno activo:

```bash
python -m pip freeze > requirements.txt
```

La carpeta `.venv` está excluida mediante `.gitignore` y no debe subirse.

## Modelo y ajuste

`H` y `N` son los porcentajes de humedad y nubosidad divididos para 100. `Tf`
se obtiene de la tabla de la guía. Para temperaturas intermedias (15 °C y
17 °C) se usa interpolación lineal; para valores de hasta 10 °C se mantiene
1.00 y desde 28 °C se mantiene 0.10.

El ajuste propuesto es:

`I_ajustado = 0.4H + 0.4N + 0.2Tf`

Se transfirió 0.10 del peso de humedad a nubosidad para estudiar una mayor
influencia de la cobertura nubosa, señal directa asociada a lluvia. Se conserva
el aporte térmico y los parámetros suman `0.4 + 0.4 + 0.2 = 1.0`. La clase
`ParametrosModelo` valida esa suma al crear cualquier configuración.

## Uso de inteligencia artificial

Se utilizó IA como apoyo para reorganizar el código inicial con MVC, corregir
imports, implementar las reglas de la guía, documentar el proyecto y preparar
las instrucciones de ejecución. La fórmula original, la tabla de datos, los
umbrales, la estructura base de la gráfica y los requisitos provienen de la
guía y de las indicaciones del docente. El prompt se conserva en `PROMPT.md`
para transparentar el proceso. El estudiante debe revisar, comprender y poder
explicar cada decisión antes de entregar.

## Comprobaciones importantes

- El ejemplo de la guía (90 %, 80 %, 18 °C) produce `I = 0.81`.
- Los límites de clasificación siguen exactamente la tabla de reglas.
- Los pesos originales y ajustados suman 1.0.
- Se generan tanto la tabla original como la tabla ajustada.
- El repositorio contiene código y archivos necesarios, no el entorno virtual.

## Observación sobre la guía

Los resultados esperados y preguntas de control mencionan `r`, `P₀` y un
modelo exponencial, aunque el procedimiento solicitado desarrolla un índice de
lluvia. Esta solución implementa estrictamente el procedimiento, los datos y
las reglas del índice de lluvia presentados en la práctica.
