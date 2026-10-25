# Portafolio de Simulación

Actividades Prácticas Experimentales (APE) de la asignatura de Simulación.
Cada práctica conserva sus instrucciones, código y entorno de ejecución.

| Práctica | Contenido comprobado en el código | Instrucciones |
|---|---|---|
| [01APE](01APE/) | Índice de lluvia a partir de humedad, nubosidad y temperatura; comparación de pesos y gráficas. | [README](01APE/README.md) |
| [02APE](02APE/) | Comparación del crecimiento poblacional exponencial, discreto, estocástico y continuo aproximado con Euler; Python, NumPy y Matplotlib. | [README](02APE/README.md) |
| [03APE-Grupal](03APE-Grupal/) | Líneas de espera M/M/1 con SimPy, métricas teóricas y simuladas, animación y gráficas. | [README](03APE-Grupal/README.md) |
| [04APE-Grupal](04APE-Grupal/) | SIR estocástico en Java; exportación CSV y visualización de las series en NetLogo. | [README](04APE-Grupal/APE04_Java_NetLogo/README.md) |

## Descargar y ejecutar

```bash
git clone https://github.com/AndersonC15/Simulacion.git
cd Simulacion
```

Para las prácticas Python, entra a la carpeta indicada, crea allí un entorno
virtual e instala su propio `requirements.txt`. No se comparte un manifiesto
entre prácticas: APE01 usa Matplotlib; APE02 utiliza NumPy y Matplotlib para
los modelos poblacionales; APE03 necesita SimPy, NumPy y Matplotlib. Consulta las versiones de
Python y los comandos exactos en cada README.

APE04 requiere JDK 17 o posterior. Se conservan los scripts Bash y se incorpora
Maven para generar un JAR ejecutable. NetLogo es una instalación externa y no
una dependencia Maven ni pip. Las pruebas de NetLogo requieren esa instalación.

## Copias y resultados

[Practica4](Practica4/README.md) conserva otra implementación SIR Java que ya
estaba en el repositorio; no se reorganiza ni sustituye por APE04. Los ZIP y
otras copias se conservan. La práctica Java documentada del portafolio está en
`04APE-Grupal/APE04_Java_NetLogo`, no en una carpeta extraída con otro nombre.

Cada práctica indica dónde escribe sus salidas. Ejecutar de nuevo puede
reemplazar imágenes o CSV del ejemplo. Para validar proyectos anteriores se
utilizaron copias temporales y se conservaron los resultados versionados.

## Documentación y apoyo de IA

Los README describen las capacidades y limitaciones observadas en el código.
Los documentos de validación distinguen las pruebas ejecutadas de las
comprobaciones pendientes; [VALIDACION_PORTAFOLIO.md](VALIDACION_PORTAFOLIO.md)
registra las de esta actualización. En esta actualización se utilizó Codex para
inspeccionar el portafolio, corregir rutas y documentación, completar
manifiestos y comprobar Maven y ejecuciones en copias temporales. Esta
aclaración se limita al trabajo de esta sesión; no atribuye autoría histórica
ni un porcentaje de IA al resto del repositorio.
