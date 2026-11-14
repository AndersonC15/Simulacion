#!/usr/bin/env python3
"""Construye el informe académico con cifras auditadas del APE 07."""

from html import escape, unescape
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import re
import tempfile

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

from ape07.comparacion import comparar, exigir, leer_csv
from ape07.modelo import TAMANOS_GUIA


BASE = Path(__file__).resolve().parents[1]
SALIDA = BASE / "APE07-CoelloAnderson-U2-Simulacion.pdf"
ANCHO = A4[0] - 108
ESTUDIANTE = "Anderson Mateo Coello Jaramillo"
HUELLA_GUIA = "649135d1d507ca217afb48b18f867169ba7ea254be0efa57446d484b2ce4137a"


def entero(valor) -> str:
    return f"{int(valor):,}".replace(",", " ")


def texto_simple(texto: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", texto.replace("<br/>", "\n")))


def fuentes() -> None:
    for carpeta, nombres in (
        (Path("/usr/share/fonts/truetype/msttcorefonts"),
         ("Times_New_Roman.ttf", "Times_New_Roman_Bold.ttf", "Times_New_Roman_Italic.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu"),
         ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf")),
    ):
        if all((carpeta / nombre).is_file() for nombre in nombres):
            for alias, nombre in zip(("Informe", "InformeBold", "InformeItalic"), nombres):
                pdfmetrics.registerFont(TTFont(alias, str(carpeta / nombre)))
            pdfmetrics.registerFontFamily("Informe", normal="Informe", bold="InformeBold",
                                          italic="InformeItalic", boldItalic="InformeBold")
            return
    raise FileNotFoundError("Se requiere Times New Roman o DejaVu Serif instalada.")


class Informe:
    def __init__(self) -> None:
        self.contenido = []
        self.markdown = []
        self.paginas = 1
        self.estilos = {
            "cuerpo": ParagraphStyle("cuerpo", fontName="Informe", fontSize=10.5, leading=13.5,
                                     alignment=TA_JUSTIFY, spaceAfter=7),
            "h1": ParagraphStyle("h1", fontName="InformeBold", fontSize=13, leading=16,
                                 spaceAfter=9, spaceBefore=3, keepWithNext=True),
            "h2": ParagraphStyle("h2", fontName="InformeBold", fontSize=11.5, leading=14,
                                 spaceAfter=7, spaceBefore=4, keepWithNext=True),
            "titulo": ParagraphStyle("titulo", fontName="InformeBold", fontSize=18, leading=21,
                                     alignment=TA_CENTER, spaceAfter=15),
            "tabla": ParagraphStyle("tabla", fontName="Informe", fontSize=9.2, leading=11.5),
            "identidad": ParagraphStyle("identidad", fontName="Informe", fontSize=10.2, leading=12.2),
            "leyenda": ParagraphStyle("leyenda", fontName="InformeItalic", fontSize=9, leading=11.5, spaceAfter=8),
            "formula": ParagraphStyle("formula", fontName="Informe", fontSize=12, leading=18,
                                      alignment=TA_CENTER, spaceAfter=9),
            "codigo": ParagraphStyle("codigo", fontName="Courier", fontSize=8, leading=11, spaceAfter=10),
        }

    def p(self, texto, estilo="cuerpo") -> None:
        self.contenido.append(Paragraph(texto, self.estilos[estilo]))
        prefijo = "## " if estilo in ("h1", "h2") else ""
        self.markdown.append(prefijo + texto_simple(texto) + "\n")

    def pagina(self) -> None:
        self.contenido.append(PageBreak())
        self.paginas += 1

    def tabla(self, cabeceras, filas, anchos, identidad=False) -> None:
        exigir(abs(sum(anchos) - ANCHO) < .1, "Ancho de tabla inválido.")
        datos = ([cabeceras] if cabeceras else []) + filas
        estilo = self.estilos["identidad" if identidad else "tabla"]
        tabla = Table([[Paragraph(str(celda), estilo) for celda in fila] for fila in datos],
                      colWidths=anchos, repeatRows=int(bool(cabeceras)), hAlign="LEFT")
        reglas = [("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#444444")),
                  ("VALIGN", (0, 0), (-1, -1), "TOP"),
                  ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                  ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if cabeceras:
            reglas.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")))
        tabla.setStyle(TableStyle(reglas))
        self.contenido.extend((tabla, Spacer(1, 9)))
        for indice, fila in enumerate(datos):
            self.markdown.append("| " + " | ".join(texto_simple(str(celda)).replace("\n", " / ") for celda in fila) + " |")
            if indice == 0:
                self.markdown.append("| " + " | ".join("---" for _ in fila) + " |")
        self.markdown.append("")

    def figura(self, nombre, leyenda, alto=255) -> None:
        ruta = BASE / "resultados/comparacion" / nombre
        imagen = Image(str(ruta))
        factor = min(ANCHO / imagen.imageWidth, alto / imagen.imageHeight)
        imagen.drawWidth = imagen.imageWidth * factor
        imagen.drawHeight = imagen.imageHeight * factor
        self.contenido.append(KeepTogether([imagen, Spacer(1, 5), Paragraph(leyenda, self.estilos["leyenda"])]))
        self.markdown.append(f"![{leyenda}](resultados/comparacion/{nombre})\n")

    def codigo(self, texto) -> None:
        self.contenido.append(Preformatted(texto, self.estilos["codigo"]))
        self.markdown.append("```text\n" + texto + "\n```\n")

    def guardar(self, destino) -> None:
        def marco(canvas, documento):
            canvas.saveState()
            canvas.drawImage(str(BASE / "docs/recursos/logo_unl.png"), 54, A4[1] - 69,
                             width=146, height=54.25, preserveAspectRatio=True, mask="auto")
            canvas.setFont("Informe", 10.5)
            canvas.drawRightString(A4[0] - 54, A4[1] - 41, "FEIRNNR - Carrera de Computación")
            canvas.setLineWidth(.4)
            canvas.line(54, A4[1] - 82, A4[0] - 54, A4[1] - 82)
            canvas.setFont("Informe", 9)
            canvas.drawString(54, 28, "APE 07 · Simulación")
            canvas.drawRightString(A4[0] - 54, 28, str(documento.page))
            canvas.restoreState()
        documento = SimpleDocTemplate(str(destino), pagesize=A4, leftMargin=54, rightMargin=54,
                                       topMargin=105, bottomMargin=48, author=ESTUDIANTE,
                                       title="APE 07 — Estimación de resultados mediante el método de Monte Carlo",
                                       subject="Simulación, U2; práctica 007", creator="Informe local APE 07 (ReportLab)")
        documento.build(self.contenido, onFirstPage=marco, onLaterPages=marco)
        exigir(documento.page == self.paginas,
               f"Revisar maquetación: {documento.page} páginas en lugar de {self.paginas}.")


def generar(destino: Path) -> Informe:
    exigir(hashlib.sha256((BASE / "ape_guia simulacion semana 7-signed.pdf").read_bytes()).hexdigest() == HUELLA_GUIA,
           "La guía firmada cambió; revisar el informe.")
    with tempfile.TemporaryDirectory(prefix="ape07-auditoria-") as carpeta:
        tabla_datos = comparar(BASE / "resultados/python", BASE / "resultados/java", Path(carpeta))
    entorno = json.loads((BASE / "resultados/python/entorno.json").read_text())
    entorno_java = json.loads((BASE / "resultados/java/entorno.json").read_text())
    exigir(tuple(entorno["tamanos"]) == TAMANOS_GUIA and entorno["parametros"]["semilla"] == 123457
           and entorno["repeticiones"] == 5, "El reporte académico exige los cuatro tamaños, semilla 123457 y cinco mediciones.")
    qa = (BASE / "resultados/revision/qa.log").read_text()
    junit = (BASE / "resultados/revision/java.log").read_text()
    exigir("Ran 10 tests" in qa and "\nOK\n" in qa and "FAILED" not in qa, "No constan las diez campañas QA correctas.")
    exigir("Tests run: 10, Failures: 0, Errors: 0, Skipped: 0" in junit and "BUILD SUCCESS" in junit,
           "No consta la ejecución correcta de JUnit.")
    mejor = tabla_datos.loc[tabla_datos["error_absoluto"].idxmin()]
    ganadores = ["Python" if fila.tiempo_python_s < fila.tiempo_java_s else "Java"
                 for fila in tabla_datos.itertuples()]
    comparacion_tiempo = (f"{ganadores[0]} registró menor mediana en los cuatro tamaños." if len(set(ganadores)) == 1
                          else "El lenguaje con menor mediana varió según el tamaño, como muestra la tabla.")
    fuentes()
    informe = Informe()
    p, tabla = informe.p, informe.tabla

    p("Reporte Técnico de Actividades<br/>Práctico-Experimentales Nro. 007", "titulo")
    p("1. Datos de Identificación del Estudiante y la Práctica", "h1")
    identidad = [
        ("Nombre del estudiante", ESTUDIANTE), ("Asignatura", "Simulación"), ("Ciclo", "5"),
        ("Unidad", "U2: Generación de números pseudoaleatorios y generación de variables aleatorias"),
        ("Resultado de aprendizaje de la unidad", "R2. Interpreta los resultados de una Simulación, bajo los "
         "principios de solidaridad, transparencia, responsabilidad y honestidad."),
        ("Práctica Nro.", "007"),
        ("Título de la Práctica", "Estimación de resultados mediante el método de Monte Carlo"),
        ("Nombre del Docente", "José O. Guamán Q."),
        ("Fecha de la práctica", "12 de noviembre de 2026<br/>13 de noviembre de 2026"),
        ("Horario", "Jueves 10h30 a 11h30<br/>Viernes 07h30 a 09h30"),
        ("Lugar", "Aula"), ("Tiempo planificado en el Sílabo", "3 horas"),
    ]
    tabla(None, [[f"<b>{etiqueta}</b>", valor] for etiqueta, valor in identidad], [187, ANCHO - 187], True)
    p("2. Objetivo(s) de la Práctica", "h1")
    p("Aplicar el método de Monte Carlo para obtener aproximaciones numéricas mediante experimentos aleatorios [1].")
    for indice, objetivo in enumerate(("Implementar un experimento Monte Carlo.",
                                       "Analizar la influencia del tamaño de muestra sobre el error.",
                                       "Comparar resultados obtenidos en Python y Java."), 1):
        p(f"{indice}. {objetivo}")

    informe.pagina()
    p("3. Materiales y reactivos", "h1")
    p("Utilicé un computador, Python, Java/JDK, un entorno de desarrollo y un generador pseudoaleatorio. "
      "La fuente principal fue la guía firmada de la práctica 07 [1]; conservé su documento original.")
    p("4. Equipos y herramientas", "h1")
    tabla(["Herramienta", "Uso y versión registrados"], [
        ["Sistema", escape(entorno["sistema"])],
        ["Python", escape(entorno["version"]) + "; entorno .venv local de 07APE"],
        ["Java", escape(entorno_java["version"]) + "; JDK y compilación Maven con release 21"],
        ["Cálculo y tablas", f"NumPy {version('numpy')}; Pandas {version('pandas')}"],
        ["Visualización y documento", f"Matplotlib {version('matplotlib')}; ReportLab {version('reportlab')}"],
        ["Verificación", "unittest, diez campañas QA; JUnit 5.12.2, diez pruebas del modelo Java"],
    ], [115, ANCHO - 115])
    p("5. Procedimiento / Metodología Ejecutada", "h1")
    p("5.1. Modelo matemático", "h2")
    p("Generé puntos en el cuadrado [-1,1)², de área 4, y conté los que satisfacen x² + y² ≤ 1, "
      "incluyendo la frontera del círculo de radio 1. Su área es π; la proporción interior aproxima π/4 [1].")
    p("x = 2U<sub>1</sub> − 1; y = 2U<sub>2</sub> − 1<br/>"
      "π estimado = 4N<sub>c</sub>/N &nbsp;&nbsp; Error = |π estimado − π|", "formula")
    p("N cuenta puntos, no números del generador: cada punto consume dos valores consecutivos. "
      "Trabajé con N = 1000, 10000, 100000 y 1000000, exactamente los tamaños de la guía.")
    p("5.2. Generación y reproducibilidad", "h2")
    p("Elegí el LCG MINSTD utilizado como referencia en el proyecto anterior: a=16807, c=0, "
      "m=2147483647 y semilla=123457. La guía 07 no impone estos valores. Inicialicé una sola vez "
      "por experimento y normalicé mediante división real; no sustituí el LCG por random o Math.random().")
    p("Los cuatro tamaños utilizan prefijos de la misma secuencia. No los considero muestras independientes. "
      "La exportación binaria permite contrastar los 2000000 estados que forman el millón de puntos.")

    informe.pagina()
    p("5.3. Arquitectura MVC y patrón Strategy", "h2")
    tabla(["Componente", "Responsabilidad"], [
        ["Modelo", "Parámetros, LCG, estimación de π y medición de tiempos; sin archivos ni gráficas."],
        ["Vista", "Presentación en consola y exportación CSV, JSON y secuencia binaria."],
        ["Controlador", "Valida tamaños y coordina modelo/vista en ambos lenguajes."],
        ["Strategy", "EstimadorPi recibe FuenteUniforme. En producción usa GeneradorLCG y en pruebas "
         "fuentes controladas para verificar casos geométricos exactos."],
    ], [100, ANCHO - 100])
    p("Elegí Strategy porque permite cambiar y probar la fuente sin modificar el criterio del círculo. "
      "La inyección de dependencias y los objetos de resultado separan responsabilidades sin añadir un framework.")
    p("5.4. Protocolo de ejecución y medición", "h2")
    for indice, paso in enumerate((
        "Ejecuté el mismo experimento en Python y Java con idénticos parámetros y operaciones.",
        "Realicé tres calentamientos de hasta 10000 puntos y cinco mediciones por tamaño; "
        "cada medición reinició la semilla.",
        "Medí generación y clasificación de puntos con perf_counter y System.nanoTime. "
        "Excluí compilación, calentamientos, archivos, gráficas y comparación.",
        "Publiqué las medianas y conservé los cinco tiempos individuales por caso: veinte por lenguaje.",
        "Comprobé cada estado contra la recurrencia; reconstruí puntos y conteos para los cuatro N. "
        "Verifiqué además hashes, tablas iniciales, estimaciones, errores, medianas y mínimos.",
    ), 1):
        p(f"{indice}. {paso}")
    p("5.5. Ejecución reproducible", "h2")
    p("Desde 07APE, preparé el entorno, ejecuté los experimentos y comprobé la entrega:")
    informe.codigo("bash scripts/preparar.sh\nbash scripts/ejecutar.sh\nbash scripts/verificar.sh\n"
                   ".venv/bin/python scripts/generar_informe.py\n.venv/bin/python scripts/generar_video.py")
    p("Las repeticiones miden rendimiento del mismo experimento; no representan cinco réplicas "
      "estadísticas independientes. Repetir la ejecución reemplaza los resultados con los mismos nombres.", "leyenda")

    informe.pagina()
    p("6. Resultados Obtenidos", "h1")
    p("6.1. Tabla solicitada en la guía", "h2")
    tabla(["N", "π estimado", "Error absoluto", "Tiempo Python (s)", "Tiempo Java (s)"], [
        [entero(fila.N), f"{fila.pi_estimado:.8f}", f"{fila.error_absoluto:.8f}",
         f"{fila.tiempo_python_s:.8f}", f"{fila.tiempo_java_s:.8f}"] for fila in tabla_datos.itertuples()
    ], [70, 95, 100, 112, ANCHO - 377])
    p("Tabla 1. Medianas de cinco mediciones. Fuente: resultados/comparacion/tabla_guia.csv; "
      "los tiempos individuales constan en resultados/python/tiempos.csv y resultados/java/tiempos.csv.", "leyenda")
    tabla(["N", "N<sub>c</sub> Python", "N<sub>c</sub> Java", "Coincidencia"], [
        [entero(fila.N), entero(fila.dentro), entero(fila.dentro), "Exacta"] for fila in tabla_datos.itertuples()
    ], [90, 135, 135, ANCHO - 360])
    p("Tabla 2. Conteos reconstruidos a partir de los estados originales. Se comparó un millón de puntos "
      "y dos millones de estados; no únicamente los primeros valores visibles.", "leyenda")
    p("6.2. Comparación de los primeros diez puntos", "h2")
    primeros = leer_csv(BASE / "resultados/comparacion/primeros20_comparados.csv")
    tabla(["Punto", "x Python", "x Java", "y Python", "y Java", "Interior"], [
        [fila["punto"], f"{float(fila['x_python']):.6f}", f"{float(fila['x_java']):.6f}",
         f"{float(fila['y_python']):.6f}", f"{float(fila['y_java']):.6f}", "Sí" if fila["dentro"] == "1" else "No"]
        for fila in primeros[:10]
    ], [40, 95, 95, 95, 95, ANCHO - 420])
    p("Tabla 3. Coordenadas redondeadas solo para lectura. Los CSV conservan las veinte observaciones "
      "iniciales y el binario todos los estados. En este módulo las divisiones no son generalmente exactas "
      "en binario, pero ambos lenguajes ejecutan las mismas operaciones binary64.", "leyenda")

    informe.pagina()
    p("6.3. Visualización y análisis del tamaño de muestra", "h2")
    informe.figura("puntos_convergencia.png", "Figura 1. Primeros 5000 puntos reales y evolución del estimador "
                   "calculada con prefijos de la misma secuencia. El círculo tiene radio 1.")
    preguntas = (
        ("¿Cómo cambia la estimación de π cuando aumenta el número de puntos?",
         "Obtuve 3.06, 3.14, 3.14432 y 3.143876. La aproximación oscila alrededor del valor de referencia. "
         "El mayor tamaño mejora respecto a 1000 puntos, pero no es el mejor de los cuatro casos."),
        ("¿Qué relación existe entre el tamaño de muestra y el error absoluto?",
         "En el modelo ideal de puntos uniformes independientes, la desviación estándar escala como 1/√N. "
         "Es una tendencia del muestreo; el error absoluto de una trayectoria puede aumentar entre dos tamaños. "
         "Aquí aumentó al pasar de 10000 a 100000 puntos."),
        ("¿En cuál de los tamaños de muestra se obtuvo una mejor aproximación de π?",
         f"La menor diferencia observada correspondió a N={entero(mejor['N'])}, con "
         f"π estimado={mejor['pi_estimado']:.8f} y error={mejor['error_absoluto']:.8f}. "
         "La conclusión se limita a esta semilla y los tamaños evaluados."),
    )
    for indice, (pregunta, respuesta) in enumerate(preguntas, 1):
        p(f"{indice}. {pregunta}", "h2")
        p(respuesta)

    informe.pagina()
    p("6.4. Error, tiempos y discusión", "h2")
    informe.figura("error_tiempos.png", "Figura 2. Error absoluto y medianas reales. La curva 1/√N, "
                   "anclada al primer error, muestra una forma de referencia; no es una cota garantizada.", 220)
    preguntas = (
        ("¿Qué lenguaje presentó menor tiempo de ejecución?", comparacion_tiempo +
         " El resultado corresponde a estas implementaciones, relojes y entorno; no establece una superioridad universal."),
        ("¿Por qué los resultados obtenidos en Python y Java pueden ser diferentes?",
         "Pueden cambiar si difieren el generador, la semilla, el orden de consumo, la normalización o "
         "las operaciones numéricas. En mi implementación coincidieron los estados, los puntos, los conteos "
         "y π; los tiempos fueron diferentes."),
        ("¿Qué importancia tiene la generación de números pseudoaleatorios en el método Monte Carlo?",
         "La distribución y las dependencias de los puntos afectan la estimación. Usar una fuente reproducible "
         "permite contrastar programas; obtener la misma secuencia no demuestra calidad estadística ni independencia."),
        ("¿El aumento del número de puntos garantiza que cada ejecución obtenga un resultado más cercano al valor real?",
         "No. La reducción del error es una tendencia de muestreo, no una garantía para cada ejecución. "
         "Los resultados de 10000 y 100000 puntos muestran esa diferencia."),
        ("¿Qué aplicaciones reales puede tener el método Monte Carlo en ingeniería, economía, informática y ciencias?",
         "Puede emplearse en análisis de confiabilidad, evaluación de riesgo, integración numérica y "
         "estudio de sistemas con incertidumbre. Son aplicaciones posibles; en esta práctica implementé la estimación de π."),
    )
    for indice, (pregunta, respuesta) in enumerate(preguntas, 4):
        p(f"{indice}. {pregunta}", "h2")
        p(respuesta)

    informe.pagina()
    p("7. Preguntas de Control", "h1")
    preguntas = (
        ("¿Qué es Monte Carlo?", "Es un método que aproxima cantidades mediante muestreo y experimentos "
         "aleatorios o pseudoaleatorios. Aquí aproximé π usando la proporción de puntos dentro del círculo."),
        ("¿Por qué el error disminuye al aumentar las muestras?", "Bajo los supuestos de muestreo ideal, "
         "la proporción observada se estabiliza y su variabilidad disminuye como 1/√N. Esto no obliga al "
         "error absoluto de cada prefijo a disminuir y no demuestra que el LCG produzca puntos independientes."),
        ("¿Qué relación existe entre precisión y costo computacional?", "Procesar más puntos requiere más "
         "operaciones. El cálculo tiene costo O(N); para reducir aproximadamente a la mitad la desviación "
         "estándar ideal se necesitan cuatro veces los puntos. La exportación completa también ocupa O(N)."),
        ("¿Qué diferencias se observaron entre Python y Java?", "Los resultados numéricos coincidieron "
         "exactamente. " + comparacion_tiempo + " Medí solo generación y clasificación, excluyendo archivos y gráficas."),
        ("¿En qué otros problemas puede utilizarse Monte Carlo?", "En integración y estimación de probabilidades, "
         "propagación de incertidumbre, confiabilidad y evaluación de escenarios. Cada aplicación requiere un modelo "
         "y supuestos adecuados; no se ejecutaron esos modelos adicionales en este APE."),
    )
    for indice, (pregunta, respuesta) in enumerate(preguntas, 1):
        p(f"{indice}. {pregunta}", "h2")
        p(respuesta)
    p("8. Conclusiones", "h1")
    for indice, conclusion in enumerate((
        "Implementé la estimación Monte Carlo con círculo inscrito en Python y Java. Verifiqué la igualdad "
        "de dos millones de estados y un millón de puntos, junto con los cuatro conteos y estimaciones.",
        f"La mejor aproximación de esta ejecución se obtuvo con {entero(mejor['N'])} puntos. "
        "El error no disminuyó de forma monótona, de acuerdo con la naturaleza del estimador.",
        comparacion_tiempo + " Los datos originales y el protocolo permiten interpretar esa medición con sus límites.",
    ), 1):
        p(f"{indice}. {conclusion}")

    informe.pagina()
    p("9. Verificación y diez campañas de QA", "h1")
    tabla(["Nro.", "Campaña realizada", "Resultado"], [
        ["01", "Vector conocido, semillas extremas y rango de 10000 valores", "Aprobada"],
        ["02", "Centro, frontera, esquina y consumo exacto de 2N valores", "Aprobada"],
        ["03", "Semillas, tamaños y fuentes inválidas; NaN e infinito", "Aprobada"],
        ["04", "Reproducibilidad de 20000 estados con tres semillas", "Aprobada"],
        ["05", "Catorce entradas CLI adversarias en ambos lenguajes", "Aprobada"],
        ["06", "Integración real, N=1 y rutas con espacios", "Aprobada"],
        ["07", "Estado alterado con hash actualizado y archivo truncado", "Aprobada"],
        ["08", "π, conteos, medianas, tiempos y coordenadas adulterados", "Aprobada"],
        ["09", "Ruta de salida inválida y medianas pares/impares", "Aprobada"],
        ["10", "Millón de puntos con semilla límite y comparación completa", "Aprobada"],
    ], [35, 367, ANCHO - 402])
    p("Tabla 4. Diez campañas unittest con subcasos adversarios. Java añade diez pruebas JUnit "
      "del modelo. Ninguna integración se contó como omitida. Evidencia: resultados/revision/qa.log y java.log.", "leyenda")
    informe.codigo("Python: Ran 10 tests; OK\nJava: Tests run: 10, Failures: 0, Errors: 0, Skipped: 0\n"
                   "Comparación: 2000000 estados; 1000000 puntos; igualdad exacta")
    p("9.1. Cuatro análisis realizados", "h2")
    for indice, detalle in enumerate((
        "Lectura de la guía firmada, requisitos, preguntas y contradicciones de la rúbrica.",
        "Validación del modelo geométrico, consumo de números, arquitectura y protocolo de tiempos.",
        "Pruebas adversarias e integración real, incluyendo adulteración de resultados y carga máxima.",
        "Revisión final de datos, documento, gráficas, video y trazabilidad de archivos.",
    ), 1):
        p(f"{indice}. {detalle}")
    p("Los documentos ANALISIS_01 a ANALISIS_04 de docs conservan el alcance y las evidencias de cada revisión.")

    informe.pagina()
    p("10. Bibliografía, anexos y alcance de la entrega", "h1")
    p("[1] Guamán Q., José O. <i>Guía de Actividades Práctico-Experimentales Nro. 007: "
      "Estimación de resultados mediante el método de Monte Carlo.</i> Simulación, ciclo 5, U2; "
      "12 y 13 de noviembre de 2026. Archivo: ape_guia simulacion semana 7-signed.pdf, pp. 1–4.")
    p("[2] Material de la asignatura. <i>Semana 6: Pruebas estadísticas de uniformidad e independencia.</i> "
      "Referencia bibliográfica indicada por la guía 07. Se consultaron las páginas 19–20 como contexto "
      "de interpretación y limitaciones; no sustituyen el modelo Monte Carlo de la guía firmada.")
    p("[3] Proyecto 07APE: código Python/Java, tablas y secuencias originales, registros QA y "
      "cuatro análisis documentados. Parámetros MINSTD contrastados con el material de referencia "
      "utilizado en APE 06; su elección y la semilla se declaran como decisiones del experimento.")
    p("10.1. Archivos para revisar y demostrar", "h2")
    tabla(["Archivo o carpeta", "Contenido"], [
        ["APE07-CoelloAnderson-U2-Simulacion.pdf", "Informe académico; versión editable Markdown con igual nombre."],
        ["resultados/comparacion/tabla_guia.csv", "Cuatro filas con π, error y tiempos de ambos lenguajes."],
        ["resultados/python y resultados/java", "Secuencias completas, primeras observaciones, resúmenes y tiempos originales."],
        ["resultados/comparacion", "Gráficas, convergencia, comparación inicial y verificacion.json."],
        ["evidencias/APE07-demostracion.mp4", "Video generado desde los resultados reales; sin narración personal."],
        ["docs/DEFENSA.md", "Guion de explicación y comandos para la demostración en vivo."],
    ], [280, ANCHO - 280])
    p("10.2. Alcance confirmado y defensa oral", "h2")
    p("Los objetivos y todo el procedimiento de la guía corresponden a Monte Carlo para π, pero la "
      "rúbrica menciona «modelo M/M/1». El docente confirmó que la práctica corresponde a Monte Carlo, "
      "según lo comunicado por el estudiante el 12 de noviembre de 2026. La implementación de π "
      "sigue ese alcance confirmado; la discrepancia del documento original queda registrada.")
    p("La rúbrica distribuye 4 puntos en defensa/demostración, 3 en implementación y 3 en documento/evidencias, "
      "incluido video. El archivo de video muestra resultados verificados y sirve como evidencia complementaria; "
      "la defensa oral y el dominio personal del código deben demostrarse ante el docente.")
    p("El documento firmado permanece intacto. La identidad y el formato institucional se verificaron "
      "con el reporte APE 06; el contenido, los resultados y las fechas pertenecen a esta práctica 07.", "leyenda")
    informe.guardar(destino)
    return informe


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ape07-informe-") as carpeta:
        temporal = Path(carpeta) / SALIDA.name
        informe = generar(temporal)
        SALIDA.write_bytes(temporal.read_bytes())
        SALIDA.with_suffix(".md").write_text("\n".join(informe.markdown), encoding="utf-8")
    print(f"Informe generado: {SALIDA}")


if __name__ == "__main__":
    main()
