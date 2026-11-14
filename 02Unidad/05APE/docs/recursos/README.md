# Recursos del informe APE 05

`logo_unl.png` es una copia sin modificaciones del recurso del informe
`06APE/APE06-CoelloAnderson-U2-Simulacion.pdf`. Se conserva su transparencia
y proporción. Su procedencia previa consta en `06APE/docs/recursos/README.md`.
SHA-256: `4c8b3e56d6750c36e4c0205a4fc3ff8f8b7b06d25da734ac0f82820400651ffb`.

Del informe APE 06 se verificaron el nombre **Anderson Mateo Coello Jaramillo**,
la estructura institucional, la tipografía, los márgenes, el encabezado y el pie.
El PDF de referencia tiene SHA-256
`f1900905a481c59c717b70d74f17a4a0966b8b91ecfc0618a4b569521109abde`.

Los datos de asignatura, ciclo, unidad, resultado de aprendizaje, docente,
fechas, horario, lugar, objetivos, parámetros y procedimiento del informe APE 05
proceden de `ape_guia simulacion semana 5.pdf`. La asignatura es **Simulación**.
La guía identifica la práctica como **05**, aunque su encabezado dice **004**;
el informe se identifica como **005** y documenta esa discrepancia sin alterar
el original. Las fechas de práctica son 29 y 30 de octubre de 2026, no las del
APE 06 ni la fecha de generación del informe.

Las tablas, gráficas y conclusiones se obtienen exclusivamente del código y de
los resultados de `05APE`. El fundamento complementario procede únicamente
de `diapositivas_semana_5.pdf`, cuya procedencia está en `../fuentes.md`.
La semilla adicional `54321` es una elección del experimento existente; la guía
solo solicita cambiar la semilla. Las estadísticas descriptivas y las gráficas
de pares son complementos del proyecto, no requisitos atribuidos a la guía.

`../verificacion_informe.log` registra las pruebas y cuatro ejecuciones nuevas
del APE 05 en carpetas temporales. Sus 10 000 filas por caso coincidieron con
los resultados conservados. `../entorno_informe.json` registra las herramientas
de esa verificación; no describe retrospectivamente el entorno de noviembre 8.

El generador `scripts/generar_informe.py` valida las secuencias completas,
sus resúmenes y las gráficas antes de producir el PDF. No ejecuta experimentos
ni modifica los CSV, JSON, PNG o el informe técnico existente en `resultados`.
