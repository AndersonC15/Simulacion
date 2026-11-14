#!/usr/bin/env python3
"""Genera el informe académico de APE 05 desde sus resultados verificados."""

from __future__ import annotations

import hashlib
from html import escape
from importlib.metadata import version
import json
from pathlib import Path
import re
import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, Preformatted,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

from comparar import CANTIDAD, MODULO, SEMILLAS, leer_csv, leer_resumen


BASE = Path(__file__).resolve().parents[1]
SALIDA = BASE / "APE05-CoelloAnderson-U2-Simulacion.pdf"
ANCHO = A4[0] - 108
ESTUDIANTE = "Anderson Mateo Coello Jaramillo"
FUENTES = {
    "ape_guia simulacion semana 5.pdf":
        "3275039991bc72a3a7d47036a36a3af6dfb3c0e60d3c28d93cc868a6e2e3fa86",
    "docs/recursos/diapositivas_semana_5.pdf":
        "5351707c290be49c16f3ab88388f66c9f450b3ee728cfc8c16281449c2c8e4f9",
    "docs/recursos/logo_unl.png":
        "4c8b3e56d6750c36e4c0205a4fc3ff8f8b7b06d25da734ac0f82820400651ffb",
}


def exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(mensaje)


def entero(valor: int) -> str:
    return f"{valor:,}".replace(",", " ")


def cargar_datos() -> tuple[dict, dict, dict]:
    for nombre, esperado in FUENTES.items():
        actual = hashlib.sha256((BASE / nombre).read_bytes()).hexdigest()
        exigir(actual == esperado, f"Cambió la fuente {nombre}; revisa el contenido del informe.")
    secuencias, resumenes = {}, {}
    for semilla in SEMILLAS:
        for carpeta, lenguaje in (("python", "Python"), ("java", "Java")):
            archivo = BASE / "resultados" / carpeta / f"semilla_{semilla}"
            filas = leer_csv(archivo.with_suffix(".csv"), semilla)
            resumenes[(carpeta, semilla)] = leer_resumen(
                archivo.with_suffix(".json"), lenguaje, semilla, filas
            )
            exigir(archivo.with_suffix(".png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
                   f"Falta una gráfica PNG válida: {archivo}")
            secuencias[(carpeta, semilla)] = filas
        exigir(secuencias[("python", semilla)] == secuencias[("java", semilla)],
               f"Los lenguajes no coinciden para la semilla {semilla}.")
    diferencias = sum(
        inicial[1] != alternativa[1]
        for inicial, alternativa in zip(
            secuencias[("python", SEMILLAS[0])], secuencias[("python", SEMILLAS[1])]
        )
    )
    exigir(diferencias == CANTIDAD, "Cambió el resultado de la comparación entre semillas.")
    registro = (BASE / "docs/verificacion_informe.log").read_text(encoding="utf-8")
    exigir(bool(re.search(r"Ran 7 tests\b", registro)) and "\nOK\n" in registro,
           "Falta el registro correcto de las siete pruebas Python.")
    exigir("Tests run: 7, Failures: 0, Errors: 0, Skipped: 0" in registro
           and "BUILD SUCCESS" in registro, "Falta el registro correcto de las siete pruebas Java.")
    for semilla in SEMILLAS:
        for lenguaje in ("python", "java"):
            exigir(f"{lenguaje}, semilla {semilla}, 10000 filas idénticas" in registro,
                   "Falta una ejecución verificada frente a los resultados conservados.")
    entorno = json.loads((BASE / "docs/entorno_informe.json").read_text(encoding="utf-8"))
    return secuencias, resumenes, entorno


def registrar_fuentes() -> None:
    opciones = (
        (Path("/usr/share/fonts/truetype/msttcorefonts"),
         ("Times_New_Roman.ttf", "Times_New_Roman_Bold.ttf", "Times_New_Roman_Italic.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu"),
         ("DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf", "DejaVuSerif-Italic.ttf")),
    )
    for carpeta, archivos in opciones:
        if all((carpeta / nombre).is_file() for nombre in archivos):
            for alias, nombre in zip(("Informe", "InformeBold", "InformeItalic"), archivos):
                pdfmetrics.registerFont(TTFont(alias, str(carpeta / nombre)))
            pdfmetrics.registerFontFamily("Informe", normal="Informe", bold="InformeBold",
                                          italic="InformeItalic", boldItalic="InformeBold")
            return
    raise FileNotFoundError("Instala Times New Roman o DejaVu Serif para generar el informe.")


class Informe:
    def __init__(self) -> None:
        self.contenido: list = []
        self.paginas_esperadas = 1
        self.estilos = {
            "cuerpo": ParagraphStyle("cuerpo", fontName="Informe", fontSize=10.7, leading=14,
                                     alignment=TA_JUSTIFY, spaceAfter=7),
            "h1": ParagraphStyle("h1", fontName="InformeBold", fontSize=13, leading=16,
                                 spaceBefore=3, spaceAfter=10, keepWithNext=True),
            "h2": ParagraphStyle("h2", fontName="InformeBold", fontSize=11.7, leading=14.5,
                                 spaceBefore=5, spaceAfter=7, keepWithNext=True),
            "titulo": ParagraphStyle("titulo", fontName="InformeBold", fontSize=18, leading=21,
                                     alignment=TA_CENTER, spaceAfter=15),
            "tabla": ParagraphStyle("tabla", fontName="Informe", fontSize=9.3, leading=11.5,
                                    alignment=TA_LEFT, splitLongWords=False),
            "identidad": ParagraphStyle("identidad", fontName="Informe", fontSize=10.2,
                                        leading=12.2, splitLongWords=False),
            "leyenda": ParagraphStyle("leyenda", fontName="InformeItalic", fontSize=9,
                                      leading=11.5, alignment=TA_LEFT, spaceAfter=9),
            "formula": ParagraphStyle("formula", fontName="Informe", fontSize=11, leading=17,
                                      alignment=TA_CENTER, spaceBefore=3, spaceAfter=9),
            "codigo": ParagraphStyle("codigo", fontName="Courier", fontSize=8, leading=11,
                                     backColor=colors.HexColor("#f3f3f3"), borderPadding=9,
                                     spaceBefore=4, spaceAfter=10),
        }

    def p(self, texto: str, estilo: str = "cuerpo") -> None:
        self.contenido.append(Paragraph(texto, self.estilos[estilo]))

    def pagina(self) -> None:
        self.contenido.append(PageBreak())
        self.paginas_esperadas += 1

    def tabla(self, cabeceras: list[str] | None, filas: list, anchos: list[float],
              identidad: bool = False) -> None:
        estilo = self.estilos["identidad" if identidad else "tabla"]
        valores = ([cabeceras] if cabeceras else []) + filas
        contenido = [[Paragraph(str(celda), estilo) for celda in fila] for fila in valores]
        exigir(abs(sum(anchos) - ANCHO) < .1, "La tabla debe caber dentro de los márgenes.")
        tabla = Table(contenido, colWidths=anchos, repeatRows=int(cabeceras is not None),
                      hAlign="LEFT")
        reglas = [("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#444444")),
                  ("VALIGN", (0, 0), (-1, -1), "TOP"),
                  ("LEFTPADDING", (0, 0), (-1, -1), 5),
                  ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if cabeceras:
            reglas.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")))
        tabla.setStyle(TableStyle(reglas))
        self.contenido.extend((tabla, Spacer(1, 9)))

    def figura(self, ruta: Path, leyenda: str) -> None:
        imagen = Image(str(ruta))
        factor = min(ANCHO / imagen.imageWidth, 485 / imagen.imageHeight)
        imagen.drawWidth = imagen.imageWidth * factor
        imagen.drawHeight = imagen.imageHeight * factor
        imagen.hAlign = "CENTER"
        self.contenido.append(KeepTogether([
            imagen, Spacer(1, 5), Paragraph(leyenda, self.estilos["leyenda"]),
        ]))

    def codigo(self, texto: str) -> None:
        self.contenido.append(Preformatted(texto, self.estilos["codigo"]))

    def guardar(self, destino: Path) -> None:
        logo = BASE / "docs/recursos/logo_unl.png"

        def marco(canvas, documento):
            canvas.saveState()
            canvas.drawImage(str(logo), 54, A4[1] - 69, width=146, height=54.25,
                             preserveAspectRatio=True, mask="auto")
            canvas.setFont("Informe", 10.5)
            canvas.drawRightString(A4[0] - 54, A4[1] - 41, "FEIRNNR - Carrera de Computación")
            canvas.setLineWidth(.4)
            canvas.line(54, A4[1] - 82, A4[0] - 54, A4[1] - 82)
            canvas.setFont("Informe", 9)
            canvas.drawString(54, 28, "APE 05 · Simulación")
            canvas.drawRightString(A4[0] - 54, 28, str(documento.page))
            canvas.restoreState()

        documento = SimpleDocTemplate(
            str(destino), pagesize=A4, leftMargin=54, rightMargin=54,
            topMargin=105, bottomMargin=48,
            title="APE 05 — Implementación y análisis del Generador Congruencial Lineal en Python y Java",
            author=ESTUDIANTE,
            subject="Reporte técnico de actividades práctico-experimentales; Simulación, U2",
            creator="Generador local del informe APE 05 (ReportLab)",
        )
        documento.build(self.contenido, onFirstPage=marco, onLaterPages=marco)
        exigir(documento.page == self.paginas_esperadas,
               f"Revisa la maquetación: se esperaban {self.paginas_esperadas} páginas "
               f"y se generaron {documento.page}.")


def generar(destino: Path) -> None:
    secuencias, resumenes, entorno = cargar_datos()
    registrar_fuentes()
    informe = Informe()
    p, tabla = informe.p, informe.tabla

    p("Reporte Técnico de Actividades<br/>Práctico-Experimentales Nro. 005", "titulo")
    p("1. Datos de Identificación del Estudiante y la Práctica", "h1")
    identificacion = [
        ("Nombre del estudiante", ESTUDIANTE),
        ("Asignatura", "Simulación"), ("Ciclo", "5"),
        ("Unidad", "U2: Generación de números pseudoaleatorios y generación de variables aleatorias"),
        ("Resultado de aprendizaje de la unidad", "R2. Interpreta los resultados de una Simulación, bajo "
         "los principios de solidaridad, transparencia, responsabilidad y honestidad."),
        ("Práctica Nro.", "005"),
        ("Título de la Práctica", "Implementación y análisis del Generador Congruencial Lineal en Python y Java"),
        ("Nombre del Docente", "José O. Guamán Q."),
        ("Fecha de la práctica", "29 de octubre de 2026<br/>30 de octubre de 2026"),
        ("Horario", "Jueves 10h30 a 11h30<br/>Viernes 07h30 a 09h30"),
        ("Lugar", "Aula"), ("Tiempo planificado en el Sílabo", "3 horas"),
    ]
    tabla(None, [[f"<b>{etiqueta}</b>", valor] for etiqueta, valor in identificacion],
          [187, ANCHO - 187], identidad=True)
    p("2. Objetivo(s) de la Práctica", "h1")
    p("Comprender el funcionamiento de un generador pseudoaleatorio mediante la implementación del "
      "método LCG [1].")
    for indice, objetivo in enumerate((
        "Implementar un generador LCG en Python.",
        "Implementar el mismo algoritmo en Java.",
        "Comparar las secuencias generadas y analizar sus propiedades.",
    ), 1):
        p(f"{indice}. {objetivo}")

    informe.pagina()
    p("3. Materiales y reactivos", "h1")
    p("Utilicé un computador, Python y Java/JDK, conforme a la guía. Como fuentes académicas empleé la "
      "guía de la práctica 05 [1] y las diapositivas de la semana 5 [2]. Trabajé con las implementaciones y "
      "los archivos de resultados conservados en la carpeta 05APE [3].")
    p("4. Equipos y herramientas", "h1")
    version_java = re.search(r'version "([^"]+)"', entorno["java"])
    version_maven = re.search(r"Apache Maven ([\d.]+)", entorno["maven"])
    exigir(version_java is not None and version_maven is not None, "Versiones de herramientas ilegibles.")
    tabla(["Herramienta", "Uso comprobado en la verificación del informe"], [
        ["Sistema operativo", escape(entorno["sistema"])],
        ["Python", f"{escape(entorno['python'])}; entorno virtual local .venv"],
        ["Java/JDK y Maven", f"JDK {escape(version_java.group(1))}; Maven {version_maven.group(1)}. "
         "El proyecto compila con release 21."],
        ["Gráficas", f"Matplotlib {escape(entorno['matplotlib'])} en Python; Java2D en Java."],
        ["Pruebas", "unittest en Python y JUnit 5.12.2 en Java, según pom.xml."],
        ["Documento", f"ReportLab {version('reportlab')}; tipografía y encabezado institucionales."],
    ], [125, ANCHO - 125])
    p("Las versiones anteriores corresponden a la verificación registrada en docs/entorno_informe.json. "
      "La fecha académica de la práctica se conserva según la guía; no se atribuyen estas versiones a esa fecha.",
      "leyenda")
    p("5. Procedimiento / Metodología Ejecutada", "h1")
    p("5.1. Recurrencia y parámetros de la guía", "h2")
    p("Inicialicé el estado con la semilla X<sub>0</sub> una sola vez. Cada nuevo entero alimenta la siguiente "
      "iteración; después lo dividí entre m para obtener su valor normalizado [1, 2].")
    p("X<sub>n+1</sub> = (a · X<sub>n</sub> + c) mod m &nbsp;&nbsp; "
      "U<sub>n</sub> = X<sub>n</sub> / m", "formula")
    tabla(["Parámetro", "Valor", "Significado"], [
        ["a", "1664525", "Multiplicador"],
        ["c", "1013904223", "Incremento"],
        ["m", "2³² = 4294967296", "Módulo; determina el espacio de estados"],
        ["X<sub>0</sub>", "12345", "Semilla inicial indicada en la guía"],
        ["Cantidad", "10 000", "Valores generados por lenguaje y semilla"],
    ], [65, 150, ANCHO - 215])
    p("El operador mod calcula el residuo. Los estados cumplen 0 ≤ X<sub>n</sub> &lt; m y los normalizados "
      "cumplen 0 ≤ U<sub>n</sub> &lt; 1. La primera salida corresponde a X<sub>1</sub>, no a la semilla.")

    informe.pagina()
    p("5.2. Desarrollo de los ocho pasos solicitados", "h2")
    pasos = (
        ("Selección de parámetros", "Configuré a, c, m y X<sub>0</sub> con los valores de la guía, sin sustituirlos por "
         "otro generador de las diapositivas."),
        ("Generación en Python", "Generé 10 000 estados y sus normalizados, conservando el estado entre iteraciones."),
        ("Implementación en Java", "Programé la misma recurrencia. Utilicé BigInteger para el cálculo entero y "
         "división real para la normalización; Java genera sus archivos sin invocar Python."),
        ("Comparación inicial", "Construí la tabla de las primeras 20 observaciones. Además, el comparador "
         "verifica los 10 000 pares completos de cada semilla."),
        ("Representación gráfica", "Grafiqué los 10 000 valores. Añadí un detalle de los primeros 200 y los "
         "pares consecutivos como complementos de la inspección visual."),
        ("Análisis del período", "Comprobé las condiciones de Hull–Dobell y revisé si había repetición en "
         "la muestra, distinguiendo el período teórico del ciclo observado."),
        ("Cambio de semilla", "Repetí el procedimiento con 54321, manteniendo a, c y m. Ese segundo valor "
         "es una elección del experimento: la guía solo indica cambiar la semilla."),
        ("Comparación final", "Contrasté Python con Java para ambas semillas y comparé las observaciones "
         "de las dos semillas en posiciones iguales."),
    )
    for indice, (titulo, detalle) in enumerate(pasos, 1):
        p(f"<b>{indice}. {titulo}.</b> {detalle}")
    p("5.3. Organización de las implementaciones", "h2")
    tabla(["Componente", "Responsabilidad en el APE 05"], [
        ["Modelo", "Parámetros, estado del LCG, resultados y análisis del período."],
        ["Vista", "Presentación en consola y exportación CSV, JSON y PNG."],
        ["Controlador", "Validación de la cantidad y coordinación del experimento."],
        ["Strategy", "El controlador recibe el contrato GeneradorPseudoaleatorio y su implementación "
         "GeneradorLCG, separados de la presentación."],
    ], [95, ANCHO - 95])
    p("Esta separación permite verificar el cálculo independientemente de los archivos y las gráficas. "
      "La estructura corresponde al código existente del APE 05 [3].")

    for posicion, semilla in enumerate(SEMILLAS):
        informe.pagina()
        if posicion == 0:
            p("6. Resultados Obtenidos", "h1")
        p(f"6.{posicion + 1}. Primeras 20 observaciones: semilla {semilla}", "h2")
        p("Comparé cada estado entero y su normalizado entre Python y Java. Los normalizados de esta "
          "tabla se muestran con 12 decimales; la verificación utiliza los valores recuperados de los CSV, "
          "antes de ese redondeo de presentación.")
        filas = []
        for fila_python, fila_java in zip(
            secuencias[("python", semilla)][:20], secuencias[("java", semilla)][:20]
        ):
            filas.append([
                str(fila_python[0]), str(fila_python[1]), str(fila_java[1]),
                f"{fila_python[2]:.12f}", f"{fila_java[2]:.12f}", "Sí",
            ])
        tabla(["n", "X<sub>n</sub> Python", "X<sub>n</sub> Java", "U<sub>n</sub> Python",
               "U<sub>n</sub> Java", "Iguales"], filas,
              [25, 83, 83, 126, 126, ANCHO - 443])
        p(f"Tabla {posicion + 1}. Comparación de las primeras 20 observaciones con semilla {semilla}. "
          f"Fuentes: resultados/python/semilla_{semilla}.csv y su equivalente en resultados/java.", "leyenda")
        p(f"La comprobación completa confirmó <b>{entero(CANTIDAD)} pares idénticos</b> para esta semilla, "
          "tanto en los estados como en los valores normalizados. No se detectaron estados repetidos "
          "dentro de esta muestra.")
        if posicion == 0:
            p("El primer cálculo permite revisar la inicialización y el orden de operaciones:")
            p("X<sub>1</sub> = (1664525 · 12345 + 1013904223) mod 4294967296 = 87628868", "formula")
            p("U<sub>1</sub> = 87628868 / 4294967296 ≈ 0.020402685739", "formula")
        else:
            p("Al cambiar la semilla, las 10 000 observaciones difirieron de las obtenidas con 12345 en "
              "la misma posición. Python y Java mantuvieron la coincidencia entre sí con la nueva semilla.")

    for indice, (semilla, lenguaje) in enumerate(
        ((12345, "python"), (12345, "java"), (54321, "python"), (54321, "java")), 1
    ):
        informe.pagina()
        nombre = "Python" if lenguaje == "python" else "Java"
        if indice == 1:
            p("6.3. Gráficas de las secuencias", "h1")
        p(f"{nombre}: semilla {semilla}", "h2")
        p("El panel superior muestra los 10 000 normalizados; el central, las primeras 200 observaciones; "
          "el inferior, los 9 999 pares consecutivos (U<sub>n</sub>, U<sub>n+1</sub>). "
          "Los dos últimos paneles complementan la gráfica de la secuencia solicitada.")
        informe.figura(
            BASE / "resultados" / lenguaje / f"semilla_{semilla}.png",
            f"Figura {indice}. Salida original de {nombre}, semilla {semilla}. "
            f"Fuente: resultados/{lenguaje}/semilla_{semilla}.png.",
        )
        p("Los valores permanecen en [0,1). La inspección visual describe su comportamiento; "
          "por sí sola no demuestra uniformidad ni independencia. Las diferencias de estilo entre las "
          "gráficas de ambos lenguajes no cambian los datos comparados.")

    informe.pagina()
    p("6.4. Resumen y efecto de cambiar la semilla", "h2")
    filas = []
    for semilla in SEMILLAS:
        estadisticas = resumenes[("python", semilla)]["estadisticas_descriptivas"]
        filas.append([str(semilla), entero(CANTIDAD),
                      f"{estadisticas['minimo']:.10f}", f"{estadisticas['maximo']:.10f}",
                      f"{estadisticas['media']:.10f}", f"{estadisticas['varianza_poblacional']:.10f}"])
    tabla(["Semilla", "N", "Mínimo", "Máximo", "Media", "Varianza"], filas,
          [53, 49, 96, 96, 96, ANCHO - 390])
    p("Tabla 3. Estadísticas descriptivas de Python; los resúmenes Java coinciden dentro de la tolerancia "
      "del comparador (relativa 10<sup>−12</sup> y absoluta 10<sup>−14</sup>). "
      "La varianza es poblacional, con divisor N. "
      "Fuentes: resultados/python/semilla_12345.json y semilla_54321.json.", "leyenda")
    p("Las medias son cercanas a 0.5. Estas medidas resumen las muestras y no constituyen una prueba "
      "estadística de uniformidad. La coincidencia de estados y normalizados entre lenguajes se exigió "
      "con igualdad exacta, sin aplicar esas tolerancias.")
    p("6.5. Análisis del período", "h2")
    p("Apliqué las tres condiciones de Hull–Dobell presentadas en las diapositivas [2, p. 10]:")
    tabla(["Condición", "Comprobación con los parámetros de la guía"], [
        ["gcd(c, m) = 1", "1013904223 es impar y m = 2³²; por tanto, son coprimos."],
        ["Cada primo de m divide a a − 1", "El único factor primo de m es 2; "
         "a − 1 = 1664524 es divisible por 2."],
        ["Si 4 divide a m, divide a a − 1", "1664524 = 4 · 416131; se cumple la condición."],
    ], [175, ANCHO - 175])
    p("Por tanto, el período teórico es τ = m = <b>4 294 967 296</b> para ambas semillas. "
      "La justificación es matemática: no recorrí los más de cuatro mil millones de estados.")
    p("En cada experimento revisé la semilla X<sub>0</sub> y las 10 000 salidas sin detectar una repetición. "
      "El ciclo completo no se observó en esa muestra; no corresponde afirmar que el período sea 10 000.")
    p("Con estos parámetros de período completo, las dos semillas pertenecen al mismo ciclo y eligen "
      "distintos puntos de inicio. Cambiar la semilla modifica los valores en posiciones iguales, "
      "pero no mejora por sí mismo el generador ni garantiza independencia entre las secuencias.")

    informe.pagina()
    p("7. Preguntas de Control", "h1")
    preguntas = (
        ("¿Qué significa pseudoaleatorio?", "Significa que los valores se obtienen mediante reglas "
         "deterministas que buscan imitar propiedades del azar. En mi implementación, conocer la semilla "
         "y los parámetros permite reproducir toda la secuencia. La apariencia irregular no demuestra "
         "aleatoriedad verdadera."),
        ("¿Qué función cumple la semilla?", "Es el estado inicial X<sub>0</sub> desde el que comienza la recurrencia. "
         "La asigné una sola vez antes de generar los valores. Con la misma semilla y los mismos parámetros, "
         "Python y Java produjeron la misma secuencia; al pasar de 12345 a 54321 cambiaron las observaciones "
         "comparadas en la misma posición."),
        ("¿Qué significa período?", "Es la longitud del ciclo de estados que vuelve a repetirse. "
         "Para el LCG de esta práctica, de período completo, es el menor entero positivo τ tal que "
         "X<sub>τ</sub> = X<sub>0</sub> y vale 2³². Distinguí ese resultado teórico de las "
         "10 000 salidas observadas."),
        ("¿Qué ocurre si se utilizan parámetros inadecuados?", "Pueden aparecer ciclos cortos, "
         "patrones y correlaciones que afecten una simulación. No cumplir las condiciones de Hull–Dobell "
         "descarta el período máximo del LCG mixto, pero no determina automáticamente cuánto dura el "
         "ciclo restante. Incluso un período completo no elimina todas las limitaciones del LCG [2]."),
        ("¿Qué ventaja tiene implementar el mismo algoritmo en dos lenguajes?", "Permite contrastar "
         "implementaciones y detectar errores de índices, actualización del estado, normalización o tipos "
         "numéricos. En mi trabajo comprobé 20 000 pares Python/Java, considerando ambas semillas. "
         "La coincidencia verifica reproducibilidad e implementación; por sí sola no demuestra calidad estadística."),
    )
    for indice, (pregunta, respuesta) in enumerate(preguntas, 1):
        p(f"{indice}. {pregunta}", "h2")
        p(respuesta)

    informe.pagina()
    p("8. Conclusiones", "h1")
    conclusiones = (
        "Implementé el LCG en Python y Java con los parámetros indicados en la guía. Comprobé la "
        "igualdad exacta de 10 000 estados y normalizados por semilla: 20 000 pares entre lenguajes en total. "
        "Los mismos parámetros y la misma semilla reprodujeron la misma secuencia determinista.",
        "Presenté las primeras 20 observaciones de cada semilla y las gráficas de ambas implementaciones. "
        "Las tablas muestran una parte de la secuencia; la verificación abarca todos los valores almacenados.",
        "Justifiqué el período completo de 2³² mediante Hull–Dobell. La ausencia de repeticiones en "
        "10 000 salidas es un resultado de la muestra y no una medición del período completo.",
        "Al cambiar la semilla de 12345 a 54321, cambiaron las observaciones en las 10 000 posiciones "
        "comparadas y se mantuvo la coincidencia Python/Java. Ambas semillas seleccionan puntos "
        "de inicio del mismo ciclo.",
        "Comprendí que reproducibilidad, período y calidad estadística son propiedades diferentes. "
        "Las gráficas y las estadísticas descriptivas no demuestran independencia. Las limitaciones "
        "del LCG explicadas en clase impiden deducir idoneidad universal a partir de estos resultados.",
    )
    for indice, conclusion in enumerate(conclusiones, 1):
        p(f"{indice}. {conclusion}")
    p("9. Bibliografía y fuentes de evidencia", "h1")
    p("[1] Guamán Q., José O. <i>Guía de Actividades Práctico-Experimentales: práctica Nro. 05, "
      "Implementación y análisis del Generador Congruencial Lineal en Python y Java.</i> Simulación, "
      "ciclo 5, U2; 29 y 30 de octubre de 2026. Archivo: ape_guia simulacion semana 5.pdf, pp. 1–2.")
    p("[2] <i>Simulación, Semana 5.</i> Diapositivas de clase, copia local "
      "docs/recursos/diapositivas_semana_5.pdf; pp. 6–10, 14–15 y 19–20. "
      "Recurrencia, período, Hull–Dobell, limitaciones y errores de implementación.")
    p("[3] <i>Proyecto 05APE.</i> Código Python y Java; resultados/python y resultados/java, "
      "CSV y JSON de ambas semillas; gráficas PNG; scripts/comparar.py y "
      "docs/verificacion_informe.log. Evidencia de los resultados presentados.")
    p("La guía original dice «Nro. 004» en el encabezado y «Práctica Nro. 05» en los datos generales. "
      "Este reporte utiliza 005 para identificar la práctica realizada; se conserva el PDF fuente sin cambios.",
      "leyenda")

    informe.pagina()
    p("10. Anexos y reproducibilidad", "h1")
    p("10.1. Ejecución del proyecto", "h2")
    p("Desde la carpeta 05APE, los comandos de preparación, ejecución y verificación son:")
    informe.codigo("bash scripts/preparar.sh\nbash scripts/ejecutar.sh\nbash scripts/verificar.sh")
    p("La ejecución utiliza las semillas 12345 y 54321 en ambos lenguajes, guarda los archivos y "
      "reconstruye el informe técnico de resultados. Al repetirla se reemplazan las salidas con los mismos nombres.")
    p("10.2. Archivos de evidencia", "h2")
    tabla(["Ubicación dentro de 05APE", "Contenido"], [
        ["resultados/python y resultados/java", "Por semilla: CSV con n, x, u; JSON de parámetros, "
         "período y estadísticas; PNG con tres paneles."],
        ["resultados/comparacion_20_semilla_12345.csv<br/>"
         "resultados/comparacion_20_semilla_54321.csv", "Tablas de las primeras 20 observaciones."],
        ["resultados/informe.md", "Informe técnico previo, con tablas y fundamento."],
        ["docs/verificacion_informe.log", "Siete pruebas Python, siete Java sin fallos ni omisiones, "
         "y cuatro ejecuciones nuevas coincidentes con los archivos conservados."],
        ["docs/entorno_informe.json", "Herramientas utilizadas al verificar los resultados para este reporte."],
    ], [270, ANCHO - 270])
    p("10.3. Precisión numérica y lectura de las salidas", "h2")
    p("El 32 de m = 2³² determina un espacio de 2³² estados, representables con 32 bits. "
      "No indica la cantidad de observaciones ni obliga a imprimir 32 decimales. "
      "Al normalizar X<sub>n</sub>/2³², la expansión decimal exacta puede necesitar hasta 32 posiciones. "
      "La consola la muestra completa; este informe redondea solo para facilitar la lectura.")
    p("Los normalizados de esta práctica son representables exactamente en float de Python y double de Java. "
      "Los CSV utilizan representaciones que permiten recuperar esos valores; el comparador coteja números "
      "y no exige que las cadenas decimales tengan idéntico formato.")
    p("10.4. Procedencia del formato y de los datos personales", "h2")
    p("Mi nombre y el formato institucional se verificaron en APE06-CoelloAnderson-U2-Simulacion.pdf. "
      "Las fechas, el título, los objetivos y el contenido académico corresponden a la guía 05. "
      "La procedencia del encabezado y las huellas de las fuentes constan en docs/recursos/README.md "
      "y docs/fuentes.md.")
    informe.guardar(destino)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ape05-informe-") as carpeta:
        temporal = Path(carpeta) / SALIDA.name
        generar(temporal)
        SALIDA.write_bytes(temporal.read_bytes())
    print(f"Informe generado: {SALIDA}")


if __name__ == "__main__":
    main()
