# Validación de documentación y manifiestos — 24 de octubre de 2026

Este registro corresponde al alcance de documentación del portafolio. La
implementación y las cinco revisiones de APE02 están en
[02APE/VALIDACION.md](02APE/VALIDACION.md). No se cambiaron los algoritmos de
APE01, APE03 ni APE04. Tampoco se eliminaron ZIP, copias o resultados del usuario.

## Dependencias Python

Se inspeccionaron los imports actuales. APE01 usa Matplotlib para gráficos y
Pillow en las pruebas de PNG; NumPy es dependencia de Matplotlib, no un cálculo
adicional del índice. APE03 usa SimPy, NumPy y Matplotlib. Cada manifiesto se
obtuvo con `python -m pip freeze` en un entorno virtual limpio propio, sin
paquetes ajenos del entorno global. La diferencia de NumPy entre APE01
(2.5.3, versión ya fijada) y APE03 (2.5.4, versión comprobada) se conserva.

Se crearon otros dos entornos vacíos y se instaló cada `requirements.txt`
final mediante su intérprete, sin instalación global. Resultado: instalación
correcta, `python -m pip check` sin dependencias rotas e imports correctos.
El `pip freeze` posterior coincidió con cada manifiesto. Python utilizado:
3.14.4. Los metadatos de NumPy y contourpy exigen Python ≥3.12; ese es el mínimo
de los manifiestos actuales. No se ejecutaron estas prácticas en Python 3.12.

Los primeros intentos pip en el sandbox fallaron por DNS; se repitieron con
acceso de red autorizado y terminaron correctamente. La caché de configuración
Matplotlib del usuario no era escribible en el sandbox; Matplotlib utilizó
su caché temporal y las ejecuciones con Agg finalizaron.

## Comprobaciones en copias temporales

Los comandos siguientes se ejecutaron desde la raíz de cada práctica copiada.
Las rutas de sus intérpretes apuntaban a entornos virtuales temporales.

| Proyecto | Comando o comprobación | Resultado |
|---|---|---|
| APE01 | `python -m unittest discover -s tests -v` | 30 métodos de prueba; OK en 8.135 s. Incluyen sus subcasos existentes. |
| APE01 | `python -m compileall -q main.py Modelo Vista Controlador tests` | Sin errores de sintaxis. |
| APE01 | Menú 1, 2, 3, 0 con `MPLBACKEND=Agg` | Tablas y PNG generados; salida limpia. |
| APE03 | `MPLBACKEND=Agg python -m src.main` | Tres escenarios ejecutados, tablas y PNG generados, proceso finalizado. |
| APE03 | `python -m compileall -q src` | Sin errores de sintaxis. No existe una suite de pruebas de esta práctica. |
| APE04 | `mvn clean package`, JAR, scripts y pruebas | Ver [VALIDACION_MAVEN.md](04APE-Grupal/APE04_Java_NetLogo/VALIDACION_MAVEN.md). |
| Practica4 | `javac -encoding UTF-8 --release 17 ...` y `java -cp out sir.Main --semilla 42 --sin-grafica` | Compilación y ejecución correctas; CSV/PNG generados en la copia, final 4/0/96. |

La ejecución de APE03 es una comprobación de instalación y funcionamiento;
no elimina sus limitaciones matemáticas ni equivale a pruebas unitarias.
La guía local pide λ=2.9 para el tercer escenario y el código actual contiene
2.99999. El README ahora distingue ambos y conserva el código dentro del
alcance autorizado. No se atribuye ese valor al docente.

## Revisión documental y límites

Se contrastaron rutas, puntos de entrada, imports y funciones con los README.
Se conservaron los textos existentes correctos, se corrigieron instrucciones
heredadas de carpetas ZIP y se documentaron fuentes `src/sir`, entrada
`sir.Main`, Maven, salidas y pruebas independientes. Se añadieron README de
carpetas relevantes y exclusiones para entornos, cachés y compilación. Ignorar
una salida regenerable no retira sus ejemplos ya versionados.

Las verificaciones gráficas aquí registradas usaron Agg o modo headless.
Esta actualización no prueba de nuevo las ventanas de APE01/03/04 ni las
recetas Windows/macOS. No hay una calificación, un porcentaje de IA ni una
validación científica nueva de las prácticas anteriores.

La comprobación final de los cambios preparados, el commit separado y el
push se registran en la entrega de esta sesión; no se anticipan como hechos
en este documento.
