# APE 01 — Construcción y simulación de un modelo matemático

Práctica de Simulación que implementa en Python un índice de lluvia a partir de
humedad, nubosidad y temperatura: `I = 0.50H + 0.30N + 0.20Tf`.

El programa procesa los nueve horarios de la guía, clasifica cada resultado,
permite evaluar un caso manual, compara el modelo original con uno ajustado y
genera gráficas. La solución aplica el patrón **Modelo–Vista–Controlador
(MVC)**.

## Funcionalidades

- Normalización de humedad (`H`) y nubosidad (`N`).
- Cálculo de `Tf` desde la tabla térmica, con interpolación lineal.
- Clasificación en sin lluvia, baja posibilidad, lluvia probable o lluvia.
- Tablas del modelo original y del ajustado.
- Evaluación de datos ingresados por el usuario.
- Generación de gráficas de variables y comparación de modelos.

## Organización del repositorio

Este directorio corresponde a `01APE`. En el repositorio general, cada práctica
debe mantenerse en su propia carpeta y con su propio `README.md`, para que pueda
descargarse y ejecutarse de manera independiente.

```text
01APE/
├── Modelo/
│   ├── README.md       # Responsabilidad de la capa Modelo
│   ├── datos.py        # Datos proporcionados por la guía
│   └── modelo.py       # Fórmulas, reglas y parámetros predefinidos
├── Controlador/
│   ├── README.md       # Responsabilidad de la capa Controlador
│   └── controlador.py  # Coordina entradas, cálculos y resultados
├── Vista/
│   ├── README.md       # Responsabilidad de la capa Vista
│   └── graficas.py     # Presentación gráfica
├── graficas_generadas/ # Resultados gráficos
├── main.py             # Vista de consola y punto de entrada
├── PROMPT.md           # Prompt y alcance del apoyo de IA
├── requirements.txt    # Dependencias reproducibles
└── ape_guia simulacion semana 1.pdf
```

Los archivos `__init__.py` permiten importar las carpetas como paquetes. El
entorno virtual, cachés y archivos del editor están excluidos por `.gitignore`;
no deben subirse al repositorio.

## Patrón de diseño MVC

| Componente | Archivos | Responsabilidad |
|---|---|---|
| Modelo | `Modelo/datos.py`, `Modelo/modelo.py` | Conserva datos, parámetros, fórmula y reglas. |
| Vista | `main.py`, `Vista/graficas.py` | Recibe entradas y presenta tablas y gráficas. |
| Controlador | `Controlador/controlador.py` | Solicita cálculos al modelo y prepara la respuesta para la vista. |

El flujo es `usuario → main.py → Controlador → Modelo → Controlador → Vista`.
El modelo no imprime ni dibuja, y la vista no contiene la fórmula del índice.

## Requisitos

- Python 3.10 o posterior.
- `pip`, invocado mediante el intérprete con `python -m pip`.

Las dependencias se declaran en **`requirements.txt`**, no en
`requirements.py`. En este proyecto son NumPy y Matplotlib.

## Instalación y ejecución

Después de clonar o descargar el repositorio, abrir una terminal en `01APE`.

### Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

No se debe ejecutar `pip install` fuera del entorno virtual. La opción 1
muestra la tabla original; la 2, la ajustada; la 3 guarda las gráficas en
`graficas_generadas/`; y la 4 permite probar un caso manual. Para salir del
entorno al finalizar, ejecutar `deactivate`.

## Regeneración de dependencias

Si se instala o actualiza una dependencia, activar primero `.venv` y ejecutar:

```bash
python -m pip freeze > requirements.txt
```

Después se debe revisar el archivo y conservar únicamente las dependencias
necesarias. La carpeta `.venv` nunca se incluye en Git.

## Pseudocódigo implementado

```text
PARA cada registro horario
    H  ← humedad / 100
    N  ← nubosidad / 100
    Tf ← buscar o interpolar el factor de temperatura
    I  ← pesoH·H + pesoN·N + pesoT·Tf
    estado ← clasificar I según los umbrales
    devolver el registro procesado a la vista
FIN PARA
```

`procesar_tabla` implementa el recorrido; `normalizar_porcentaje`,
`calcular_factor_temperatura`, `calcular_indice` y `clasificar_indice`
implementan cada operación. No queda pseudocódigo pendiente de programación.

## Modelo original y ajuste

El modelo usa `H = humedad / 100`, `N = nubosidad / 100` y el factor `Tf` de la
tabla de la guía. Para temperaturas entre dos valores se aplica interpolación
lineal; hasta 10 °C se usa `1.00` y desde 28 °C se usa `0.10`.

Los parámetros están fijados en `Modelo/modelo.py`:

```python
ORIGINAL = ParametrosModelo(0.50, 0.30, 0.20, "Modelo original")
AJUSTADO = ParametrosModelo(0.40, 0.40, 0.20, "Modelo ajustado")
```

El ajuste transfiere `0.10` del peso de humedad a nubosidad para estudiar una
mayor influencia de la cobertura nubosa como señal asociada a lluvia. Conserva
el peso térmico y la suma `1.00`. `ParametrosModelo` rechaza pesos negativos o
configuraciones cuya suma no sea `1.00`; los valores quedan predefinidos y
validados dentro del modelo.

## Uso de inteligencia artificial

La IA se utilizó únicamente como apoyo para:

- revisar la organización según MVC;
- corregir problemas técnicos de imports y ejecución;
- apoyar la implementación de reglas descritas en la guía;
- mejorar comentarios, documentación e instrucciones; y
- comprobar que el proyecto pueda ejecutarse siguiendo este README.

La fórmula, los datos, los umbrales, el pseudocódigo, el criterio del ajuste y
las decisiones académicas pertenecen a la práctica y deben ser comprendidos,
revisados y explicados por el estudiante. `PROMPT.md` conserva el prompt usado
para transparentar el proceso.

El límite institucional de **máximo 20 % de uso de IA** no puede demostrarse
con una métrica automática confiable sobre el código. Para respetarlo, el
estudiante debe mantener la autoría de la solución, validar cada aporte,
registrar cualquier uso adicional y ajustar esta declaración para que refleje
con exactitud su proceso real antes de entregar.

## Verificación rápida

Ejecutar `python main.py` y comprobar que:

1. Las opciones 1 y 2 imprimen nueve registros.
2. El caso de la guía (90 % de humedad, 80 % de nubosidad y 18 °C) produce
   `I = 0.81` con el modelo original.
3. La opción 3 crea `variables_modelo.png` y `comparacion_modelos.png`.
4. Los modelos original y ajustado conservan pesos cuya suma es `1.00`.

## Nota sobre la guía

Los resultados esperados y las preguntas de control mencionan `r`, `P₀` y un
modelo exponencial, mientras que el procedimiento desarrolla un índice de
lluvia. Este proyecto implementa el procedimiento, los datos y las reglas del
índice de lluvia indicados en la práctica.
