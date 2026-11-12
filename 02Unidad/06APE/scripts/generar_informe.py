#!/usr/bin/env python3
"""Genera el informe institucional de APE 06 a partir de sus archivos reales.

Ejecutar con python/.venv/bin/python scripts/generar_informe.py.
No ejecuta de nuevo los benchmarks ni cambia los resultados experimentales.
"""

from __future__ import annotations

import csv
from datetime import datetime
from html import escape
from importlib.metadata import version
import json
import math
from pathlib import Path
import re
import statistics
import tempfile
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from ape06.infraestructura.comparacion import comparar_todo
from ape06.vista.informe import VistaInforme


BASE = Path(__file__).resolve().parents[1]
RESULTADOS = BASE / "resultados"
SALIDA = BASE / "APE06-CoelloAnderson-U2-Simulacion.pdf"
ORDEN = ("minstd", "glibc", "zx81")
NOMBRES = {"minstd": "MINSTD", "glibc": "glibc", "zx81": "ZX81"}
TAMANOS = (1000, 10000, 100000, 1000000)
ANCHO = A4[0] - 108


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(mensaje)


def entero(valor: int) -> str:
    return f"{valor:,}".replace(",", " ")


def decimal(valor: float, cifras: int = 7) -> str:
    return f"{valor:.{cifras}f}"


def cargar_datos(temporal: Path) -> tuple[dict, list, dict, dict]:
    analisis, benchmark = comparar_todo(RESULTADOS / "python", RESULTADOS / "java", temporal)
    datos = {a["parametros"]["nombre"]: a for a in analisis}
    exigir(set(datos) == set(ORDEN), "El informe requiere MINSTD, glibc y ZX81.")
    for a in datos.values():
        exigir(a["n"] == 10000, "La guía exige muestras de 10 000 números.")
        exigir(all(p["alfa"] == .05 for p in a["pruebas"]), "La guía exige alfa=0.05.")
    parametros_documentados = {
        "minstd": (123457, 16807, 0, 2147483647),
        "glibc": (1, 1103515245, 12345, 4294967296),
        "zx81": (1, 75, 74, 131073),
    }
    for nombre, valores in parametros_documentados.items():
        exigir(tuple(datos[nombre]["parametros"][k] for k in ("semilla", "a", "c", "m")) == valores,
               f"Cambió la configuración {nombre}: revisa el análisis académico antes de regenerar el PDF.")
    exigir({(b["generador"], b["n"]) for b in benchmark} ==
           {(n, t) for n in ORDEN for t in TAMANOS}, "Faltan tamaños de la tabla de la guía.")
    for lenguaje in ("python", "java"):
        carpeta = RESULTADOS / lenguaje
        tiempos = leer_csv(carpeta / "tiempos.csv")
        exigir(len(tiempos) == 60, "Se esperan 60 mediciones por lenguaje.")
        for fila in leer_csv(carpeta / "benchmark.csv"):
            muestras = [float(t["segundos"]) for t in tiempos
                        if (t["generador"], t["n"]) == (fila["generador"], fila["n"])]
            exigir(len(muestras) == int(fila["repeticiones"]) == 5, "Se requieren cinco repeticiones.")
            exigir(all(math.isfinite(t) and t > 0 for t in muestras), "Medición de tiempo inválida.")
            exigir(statistics.median(muestras) == float(fila["tiempo_mediana_s"]), "Mediana incoherente.")
            exigir(min(muestras) == float(fila["tiempo_minimo_s"]), "Tiempo mínimo incoherente.")
        for nombre in ORDEN:
            frecuencias = leer_csv(carpeta / nombre / "frecuencias.csv")
            exigir(len(frecuencias) == 10, "Se requieren diez intervalos.")
            esperadas = next(p for p in datos[nombre]["pruebas"] if p["nombre"] == "chi_cuadrado")
            exigir([int(f["observada"]) for f in frecuencias] ==
                   [f["observada"] for f in esperadas["intervalos"]], "Frecuencias inconsistentes.")
            exigir(len(leer_csv(carpeta / nombre / "ks_ordenados.csv")) == 10000, "Tabla KS incompleta.")
    pytest = (RESULTADOS / "revision/pytest.log").read_text(encoding="utf-8")
    maven = (RESULTADOS / "revision/maven.log").read_text(encoding="utf-8")
    exigir(bool(re.search(r"\b32 passed\b", pytest)) and not re.search(r"\b(?:failed|skipped)\b", pytest),
           "Se necesita un registro de las 32 pruebas Python sin fallos ni omisiones.")
    resumen_java = re.search(r"Tests run: 19, Failures: 0, Errors: 0, Skipped: 0", maven)
    exigir(resumen_java is not None and "BUILD SUCCESS" in maven, "Falta la verificación Java correcta.")
    entornos = {l: json.loads((RESULTADOS / l / "entorno_benchmark.json").read_text(encoding="utf-8"))
                for l in ("python", "java")}
    registros = {"pytest": pytest.strip(), "maven": "\n".join(
        linea for linea in maven.splitlines()
        if "Tests run: 19," in linea or "BUILD SUCCESS" in linea or "Finished at:" in linea)}
    VistaInforme()._grafica_rendimiento(benchmark, temporal)
    return datos, benchmark, entornos, registros


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
            "identidad": ParagraphStyle("identidad", fontName="Informe", fontSize=10.2, leading=12.2,
                                        splitLongWords=False),
            "leyenda": ParagraphStyle("leyenda", fontName="InformeItalic", fontSize=9, leading=11.5,
                                      alignment=TA_LEFT, spaceAfter=9),
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
        tabla = Table(contenido, colWidths=anchos, repeatRows=int(cabeceras is not None), hAlign="LEFT")
        reglas = [("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#444444")),
                  ("VALIGN", (0, 0), (-1, -1), "TOP"),
                  ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                  ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if cabeceras:
            reglas.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")))
        tabla.setStyle(TableStyle(reglas))
        self.contenido.extend((tabla, Spacer(1, 9)))

    def imagen(self, ruta: Path, ancho: float, alto: float) -> Image:
        imagen = Image(str(ruta))
        factor = min(ancho / imagen.imageWidth, alto / imagen.imageHeight)
        imagen.drawWidth, imagen.drawHeight = imagen.imageWidth * factor, imagen.imageHeight * factor
        imagen.hAlign = "CENTER"
        return imagen

    def figura(self, ruta: Path, leyenda: str, ancho: float = ANCHO, alto: float = 230) -> None:
        self.contenido.append(KeepTogether([
            self.imagen(ruta, ancho, alto), Spacer(1, 5),
            Paragraph(leyenda, self.estilos["leyenda"]),
        ]))

    def codigo(self, texto: str) -> None:
        self.contenido.append(Preformatted(texto, self.estilos["codigo"]))

    def guardar(self) -> None:
        logo = BASE / "docs/recursos/logo_unl.png"

        def marco(canvas, documento):
            canvas.saveState()
            canvas.drawImage(str(logo), 54, A4[1] - 69, width=146, height=54.25,
                             preserveAspectRatio=True, mask="auto")
            canvas.setFillColor(colors.black)
            canvas.setFont("Informe", 10.5)
            canvas.drawRightString(A4[0] - 54, A4[1] - 41, "FEIRNNR - Carrera de Computación")
            canvas.setLineWidth(.4)
            canvas.line(54, A4[1] - 82, A4[0] - 54, A4[1] - 82)
            canvas.setFont("Informe", 9)
            canvas.drawString(54, 28, "APE 06 · Simulación")
            canvas.drawRightString(A4[0] - 54, 28, str(documento.page))
            canvas.restoreState()

        doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=54, rightMargin=54,
                                topMargin=105, bottomMargin=48,
                                title="APE 06 — Validación estadística de números pseudoaleatorios",
                                author="Anderson Mateo Coello Jaramillo",
                                subject="Reporte técnico de actividades práctico-experimentales; Simulación, U2",
                                creator="Generador local del informe APE 06 (ReportLab)")
        doc.build(self.contenido, onFirstPage=marco, onLaterPages=marco)
        exigir(doc.page == self.paginas_esperadas,
               f"Revisa la maquetación: se planificaron {self.paginas_esperadas} páginas y se generaron {doc.page}.")


def generar(temporal: Path) -> None:
    datos, benchmark, entornos, registros = cargar_datos(temporal)
    registrar_fuentes()
    informe = Informe()
    p = informe.p
    tabla = informe.tabla
    pruebas = {nombre: {r["nombre"]: r for r in datos[nombre]["pruebas"]} for nombre in ORDEN}
    pi = {(b["generador"], b["n"]): b for b in benchmark}
    fecha = datetime.now(ZoneInfo("America/Guayaquil")).strftime("%d/%m/%Y")

    # 1. Identificación: conserva la estructura de APE 01/02 y usa los datos de la guía 006.
    p("Reporte Técnico de Actividades<br/>Práctico-Experimentales Nro. 006", "titulo")
    p("1. Datos de Identificación del Estudiante y la Práctica", "h1")
    identificacion = [
        ("Nombre del estudiante", "Anderson Mateo Coello Jaramillo"),
        ("Asignatura", "Simulación"), ("Ciclo", "5"),
        ("Unidad", "U2: Generación de números pseudoaleatorios y generación de variables aleatorias"),
        ("Resultado de aprendizaje de la unidad", "R2. Interpreta los resultados de una Simulación, bajo los principios "
         "de solidaridad, transparencia, responsabilidad y honestidad."),
        ("Práctica Nro.", "006"),
        ("Título de la Práctica", "Validación estadística de números pseudoaleatorios mediante Chi-cuadrado y Kolmogorov-Smirnov"),
        ("Nombre del Docente", "José O. Guamán Q."),
        ("Fecha de la práctica", "05 de noviembre de 2026<br/>06 de noviembre de 2026"),
        ("Horario", "Jueves 10h30 a 11h30<br/>Viernes 07h30 a 09h30"),
        ("Lugar", "Aula"), ("Tiempo planificado en el Sílabo", "3 horas"),
    ]
    tabla(None, [[f"<b>{etiqueta}</b>", valor] for etiqueta, valor in identificacion],
          [187, ANCHO - 187], identidad=True)
    p("2. Objetivo(s) de la Práctica", "h1")
    p("Evaluar la calidad estadística de una secuencia de números pseudoaleatorios mediante Chi-cuadrado y "
      "Kolmogorov-Smirnov para determinar si su comportamiento es compatible con una distribución uniforme en [0,1].")
    for i, objetivo in enumerate((
        "Generar secuencias mediante el método congruencial lineal (LCG).",
        "Aplicar Chi-cuadrado para evaluar la uniformidad de las frecuencias.",
        "Aplicar KS para comparar la distribución empírica con la uniforme teórica.",
        "Interpretar los estadísticos y sus respectivos valores p.",
        "Comparar diferentes configuraciones del generador pseudoaleatorio.",
    ), 1):
        p(f"{i}. {objetivo}")

    # 2. Herramientas y generación.
    informe.pagina()
    p("3. Materiales y reactivos", "h1")
    p("Guía de Actividades Práctico-Experimentales Nro. 006 [1], diapositivas de las semanas 5 y 6 [2, 3], "
      "configuración compartida <b>config/generadores.csv</b> y código de las implementaciones Python y Java [4]. "
      "Se trabajó con secuencias producidas por la recurrencia LCG; no se sustituyeron por otro generador aleatorio.")
    p("4. Equipos y herramientas", "h1")
    py_version = entornos["python"]["version"].split()[0]
    tabla(["Herramienta", "Versión / uso comprobado"], [
        ["Computador y sistema", escape(entornos["python"]["sistema"])],
        ["Python", f"{py_version}; entorno virtual python/.venv"],
        ["Java", f"JDK {escape(entornos['java']['version'])}; compilación y pruebas con Maven"],
        ["Cálculo y tablas", f"NumPy {version('numpy')}, SciPy {version('scipy')} y Pandas {version('pandas')}"],
        ["Gráficas e informe", f"Matplotlib {version('matplotlib')}, Java2D y ReportLab {version('reportlab')}"],
        ["Verificación", f"pytest {version('pytest')} y JUnit 5 (configurado en pom.xml)"],
    ], [128, ANCHO - 128])
    p("Las versiones de Python, Java y sistema proceden de los archivos de entorno del benchmark; las de las "
      "bibliotecas Python corresponden al entorno usado para generar este informe. No se atribuyen al equipo "
      "especificaciones de hardware que no estén documentadas.", "leyenda")
    p("5. Procedimiento / Metodología Ejecutada", "h1")
    p("5.1. Generador congruencial lineal y parámetros", "h2")
    p("Se asigna la semilla X<sub>0</sub> una sola vez. En cada iteración se obtiene el nuevo estado entero y "
      "después se normaliza. El primer número almacenado corresponde a X<sub>1</sub> [1, 2].")
    p("X<sub>n+1</sub> = (aX<sub>n</sub> + c) mod m &nbsp;&nbsp;&nbsp; "
      "U<sub>n+1</sub> = X<sub>n+1</sub> / m", "formula")
    tabla(["Configuración", "Semilla X<sub>0</sub>", "a", "c", "m"], [
        [NOMBRES[n], str(datos[n]["parametros"]["semilla"]), str(datos[n]["parametros"]["a"]),
         str(datos[n]["parametros"]["c"]), str(datos[n]["parametros"]["m"])] for n in ORDEN
    ], [88, 87, 112, 70, ANCHO - 357])
    p("Los parámetros MINSTD y glibc, incluidas sus semillas, se tomaron de los ejemplos de clase [2, 3]. "
      "Los parámetros a, c y m de ZX81 corresponden a la tabla de Semana 5; su semilla 1 es una elección del "
      "experimento. Los nombres identifican las configuraciones de clase, sin afirmar que reproduzcan toda "
      "la API de los generadores históricos.")

    # 3. Métodos estadísticos.
    informe.pagina()
    p("5.2. Hipótesis y nivel de significancia", "h2")
    p("Para las pruebas de uniformidad se plantean H<sub>0</sub>: los valores siguen U(0,1), y "
      "H<sub>1</sub>: su distribución difiere de U(0,1). Se fijó <b>α = 0.05</b>. Si p &lt; α se rechaza "
      "H<sub>0</sub>; si p ≥ α, no se rechaza. No rechazar no equivale a demostrar que H<sub>0</sub> sea verdadera [1, 3].")
    p("5.3. Prueba Chi-cuadrado", "h2")
    p("Se dividió [0,1) en diez intervalos de amplitud 0.1. Para cada uno se contabilizó la frecuencia observada "
      "O<sub>i</sub> y se calculó E<sub>i</sub> = N/10. Con N = 10 000, E<sub>i</sub> = 1000 y los grados "
      "de libertad son gl = 10 − 1 = 9. Se satisface la condición E<sub>i</sub> ≥ 5.")
    p("χ² = Σ<sub>i=1,…,10</sub> (O<sub>i</sub> − E<sub>i</sub>)² / E<sub>i</sub>", "formula")
    p("El valor p corresponde a la cola superior de χ² con nueve grados de libertad. Python utiliza SciPy "
      "y Java la función gamma regularizada Q de Apache Commons Math. El crítico a α = 0.05 es "
      f"{pruebas['minstd']['chi_cuadrado']['critico']:.8f}. Se exportan las frecuencias y los aportes al estadístico.")
    p("5.4. Prueba Kolmogorov-Smirnov bilateral", "h2")
    p("Se ordenó una copia de los datos para conservar la secuencia original. Con U<sub>(i)</sub> ordenados "
      "e i = 1,…,N, se calcularon ambas diferencias respecto a F(u) = u:")
    p("D<super>+</super> = max(i/N − U<sub>(i)</sub>)<br/>"
      "D<super>−</super> = max(U<sub>(i)</sub> − (i−1)/N)<br/>"
      "D = max(D<super>+</super>, D<super>−</super>)", "formula")
    p("En ambos lenguajes se usó la distribución límite bilateral de Kolmogorov: "
      "p ≈ Q<sub>K</sub>(√N · D). Es un <b>valor p asintótico</b>, no exacto para N finito. "
      f"El crítico obtenido es {pruebas['minstd']['ks']['critico']:.8f}; la aproximación de clase "
      "1.36/√N da 0.0136. Se guardaron los 10 000 datos ordenados, las FDE izquierda/derecha y las diferencias.")
    p("5.5. Prueba de rachas como complemento", "h2")
    p("Se clasificaron los valores por encima y por debajo de la mediana, manteniendo el orden original. "
      "Se eliminarían los empates, informando su número. La hipótesis de referencia es el orden aleatorio de "
      "esos signos; difiere de la hipótesis de uniformidad [3].")
    p("μ<sub>R</sub> = 2n<sub>1</sub>n<sub>2</sub>/(n<sub>1</sub>+n<sub>2</sub>) + 1<br/>"
      "σ²<sub>R</sub> = 2n<sub>1</sub>n<sub>2</sub>(2n<sub>1</sub>n<sub>2</sub>−n<sub>1</sub>−n<sub>2</sub>) / "
      "[(n<sub>1</sub>+n<sub>2</sub>)²(n<sub>1</sub>+n<sub>2</sub>−1)]<br/>"
      "Z = (R − μ<sub>R</sub>)/σ<sub>R</sub>", "formula")
    p("Se usa la aproximación normal bilateral cuando n<sub>1</sub>, n<sub>2</sub> &gt; 10, sin corrección de "
      "continuidad. El crítico es |Z| ≈ 1.95996. La prueba se añadió como complemento de Semana 6; no sustituye Chi-cuadrado ni KS.")

    # 4. Implementación y experimento de pi.
    informe.pagina()
    p("5.6. Arquitectura e implementación en Python y Java", "h2")
    tabla(["Componente", "Responsabilidad implementada"], [
        ["Modelo", "LCG, parámetros, resultados, pruebas estadísticas, estimación de π y medición del rendimiento."],
        ["Vista", "Presentación en consola y gráficas: Matplotlib en Python y Java2D en Java."],
        ["Controlador", "Coordina generación, análisis, exportación y experimentos de rendimiento."],
        ["Infraestructura", "Lectura de configuración, persistencia CSV/JSON y comparación entre lenguajes."],
        ["Strategy", "PruebaEstadistica define el contrato de Chi-cuadrado, KS y rachas; el servicio recibe las estrategias."],
    ], [102, ANCHO - 102])
    p("Los modelos no importan vistas ni controladores. Se proporcionan dependencias por constructor. "
      "Java ejecuta sus cálculos y crea sus archivos y gráficas sin invocar Python. La comparación consolidada "
      "se realiza después de ambas ejecuciones. Java usa enteros long y recurre a BigInteger cuando los "
      "parámetros podrían desbordar el producto; Python realiza la recurrencia con enteros de precisión arbitraria.")
    p("5.7. Secuencia de ejecución y comparación", "h2")
    for i, paso in enumerate((
        "Leer los mismos parámetros del archivo config/generadores.csv en ambos programas.",
        "Generar 10 000 valores por configuración y aplicar las tres pruebas con α = 0.05.",
        "Exportar secuencias, frecuencias, datos KS, resúmenes y gráficas por lenguaje.",
        "Comparar los 30 000 estados y valores normalizados, comprobando también la recurrencia y las decisiones.",
        "Ejecutar la estimación de π para los cuatro tamaños y consolidar las doce filas de la tabla solicitada.",
    ), 1):
        p(f"{i}. {paso}")
    p("Los estados enteros y normalizados se comparan con igualdad exacta. Para estadísticos y valores p "
      "se aplican tolerancias absoluta y relativa de 10<super>−10</super>; para críticos, absoluta de "
      "10<super>−8</super>. Se comparan todas las filas de cada secuencia, no solo una muestra inicial.")
    p("5.8. Estimación de π y medición de tiempos", "h2")
    p("La página 6 de la guía solicita π estimado y error, pero no define el algoritmo. El proyecto adopta "
      "Monte Carlo por cuarto de círculo: cada punto es (U<sub>2i−1</sub>, U<sub>2i</sub>) y se cuenta como "
      "interior si x² + y² ≤ 1. Esta es una decisión documentada del proyecto, no una fórmula atribuida a la guía.")
    p("π estimado = 4 · puntos interiores / N<br/>Error absoluto = |π estimado − π|", "formula")
    p("Aquí N significa puntos y se consumen <b>2N valores LCG</b>. Cada medición reinicia la misma semilla. "
      "Se realizan tres calentamientos de hasta 10 000 puntos y cinco repeticiones; se informa su mediana en "
      "segundos. Se mide generación más estimación, excluyendo consola, archivos y gráficas. Los relojes son "
      "perf_counter y System.nanoTime. Estas repeticiones miden rendimiento; no son muestras aleatorias independientes.")

    # 5. Muestras y estadística descriptiva.
    informe.pagina()
    p("6. Resultados Obtenidos", "h1")
    p("6.1. Secuencias y estadística descriptiva", "h2")
    p("Cada lenguaje generó 10 000 valores por configuración. La tabla resume Python; los resultados Java "
      "coinciden dentro de las tolerancias declaradas. La referencia uniforme continua tiene media 0.5 "
      "y varianza 1/12 ≈ 0.08333333.")
    tabla(["Configuración", "N", "Media", "Varianza", "Mínimo", "Máximo"], [
        [NOMBRES[n], "10 000", decimal(datos[n]["resumen"]["media"], 8),
         decimal(datos[n]["resumen"]["varianza"], 8), decimal(datos[n]["resumen"]["minimo"], 8),
         decimal(datos[n]["resumen"]["maximo"], 8)] for n in ORDEN
    ], [86, 49, 88, 88, 88, ANCHO - 399])
    p("Tabla 1. Resumen de las tres muestras. La varianza es poblacional, con divisor N. "
      "Datos: resultados/python/&lt;generador&gt;/analisis.json.", "leyenda")
    p("Las medias se encuentran entre 0.50128938 y 0.50410034, y las varianzas próximas a 1/12. "
      "Estas aproximaciones descriptivas no sustituyen las pruebas de hipótesis. En cada muestra se "
      "observaron 10 000 estados distintos. No se detectó repetición en ese tramo: <b>no se afirma el período total</b>.")
    p("La siguiente tabla muestra los diez primeros valores de MINSTD en ambos programas. "
      "Los estados se presentan completos; los normalizados se redondean únicamente para lectura.")
    muestra_p = leer_csv(RESULTADOS / "python/minstd/secuencia.csv")[:10]
    muestra_j = leer_csv(RESULTADOS / "java/minstd/secuencia.csv")[:10]
    tabla(["i", "X Python", "X Java", "U Python", "U Java"], [
        [a["posicion"], a["estado"], b["estado"], f"{float(a['valor']):.10f}", f"{float(b['valor']):.10f}"]
        for a, b in zip(muestra_p, muestra_j)
    ], [30, 102, 102, 126, ANCHO - 360])
    p("Tabla 2. Comparación visible de los primeros diez datos MINSTD. La comprobación completa incluye "
      "también glibc y ZX81: 30 000 pares de estados y valores normalizados, sin diferencias.", "leyenda")
    p("Los archivos secuencia_minstd.csv, secuencia_glibc.csv y secuencia_zx81.csv de "
      "resultados/comparacion conservan la comparación fila por fila. Las secuencias originales se encuentran "
      "en resultados/python y resultados/java. La vista de consola muestra una previsualización de diez datos.")

    # 6. Resultados de las pruebas.
    informe.pagina()
    p("6.2. Contrastes estadísticos: N = 10 000 y α = 0.05", "h2")
    p("Chi-cuadrado: diez intervalos, E<sub>i</sub> = 1000 y gl = 9.", "h2")
    tabla(["Configuración", "χ²", "p", "Crítico", "Decisión"], [
        [NOMBRES[n], decimal(pruebas[n]["chi_cuadrado"]["estadistico"], 4),
         decimal(pruebas[n]["chi_cuadrado"]["valor_p"]), "16.91897760", "No se rechaza H<sub>0</sub>"]
        for n in ORDEN
    ], [83, 62, 91, 93, ANCHO - 329])
    p("Tabla 3. Prueba de uniformidad por frecuencias. Los tres valores p superan 0.05 y "
      "los tres estadísticos son menores que el crítico.", "leyenda")
    p("Kolmogorov-Smirnov bilateral", "h2")
    tabla(["Configuración", "D<super>+</super>", "D<super>−</super>", "D", "p aprox."], [
        [NOMBRES[n], decimal(pruebas[n]["ks"]["detalles"]["d_mas"], 9),
         decimal(pruebas[n]["ks"]["detalles"]["d_menos"], 9), decimal(pruebas[n]["ks"]["estadistico"], 9),
         decimal(pruebas[n]["ks"]["valor_p"])] for n in ORDEN
    ], [83, 103, 103, 103, ANCHO - 392])
    p("Tabla 4. KS asintótico. Crítico común: D = 0.01358099. No se rechaza H<sub>0</sub> en las tres muestras.", "leyenda")
    p("ZX81 presenta la mayor distancia D observada (0.011633098), aunque permanece por debajo del crítico. "
      "La diapositiva de Semana 6 presenta para glibc p<sub>KS</sub> ≈ 0.686; aquí se obtuvo "
      "0.6888559 con el método asintótico declarado. Esa diferencia numérica no cambia la decisión y no se "
      "modificaron los datos para reproducir una cifra prefijada.")
    p("Rachas respecto a la mediana", "h2")
    tabla(["Configuración", "n<sub>1</sub> / n<sub>2</sub>", "Rachas R", "Z", "p"], [
        [NOMBRES[n], "5000 / 5000", str(int(pruebas[n]["rachas"]["detalles"]["rachas"])),
         decimal(pruebas[n]["rachas"]["estadistico"]), decimal(pruebas[n]["rachas"]["valor_p"])] for n in ORDEN
    ], [83, 111, 83, 105, ANCHO - 382])
    p("Tabla 5. No hubo empates con la mediana. μ<sub>R</sub> = 5001, σ²<sub>R</sub> = 2499.749975 "
      "y crítico |Z| = 1.95996398. No se rechaza el orden aleatorio de signos en estas muestras.", "leyenda")
    p("Las pruebas no detectan evidencia suficiente contra sus hipótesis de referencia a α = 0.05. "
      "Un valor p mayor no constituye una puntuación de calidad del generador. Uniformidad marginal, "
      "orden de signos e independencia completa son propiedades diferentes; estos resultados no garantizan "
      "idoneidad para cualquier simulación.")

    # 7. Tabla de frecuencias consolidada.
    informe.pagina()
    p("6.3. Frecuencias observadas y contribuciones a χ²", "h2")
    p("Cada intervalo incluye su extremo inferior y excluye el superior. Como U &lt; 1, los diez intervalos "
      "cubren todos los valores generados. La frecuencia esperada es 1000 en cada intervalo y configuración.")
    tabla(["Intervalo", "MINSTD O<sub>i</sub>", "glibc O<sub>i</sub>", "ZX81 O<sub>i</sub>", "E<sub>i</sub>"], [
        [f"[{i/10:.1f}, {(i+1)/10:.1f})",
         *[str(pruebas[n]["chi_cuadrado"]["intervalos"][i]["observada"]) for n in ORDEN], "1000"]
        for i in range(10)
    ] + [["<b>Total</b>", "10 000", "10 000", "10 000", "10 000"]], [103, 108, 98, 98, ANCHO - 407])
    p("Tabla 6. Frecuencias de los CSV exportados, verificadas entre ambos lenguajes. Cada columna "
      "de conteos suma exactamente 10 000.", "leyenda")
    tabla(["Intervalo", "Aporte MINSTD", "Aporte glibc", "Aporte ZX81"], [
        [f"[{i/10:.1f}, {(i+1)/10:.1f})",
         *[decimal(pruebas[n]["chi_cuadrado"]["intervalos"][i]["aporte"], 3) for n in ORDEN]]
        for i in range(10)
    ] + [["<b>Suma χ²</b>", "3.278", "2.436", "7.860"]], [103, 128, 128, ANCHO - 359])
    p("Tabla 7. Cada aporte es (O<sub>i</sub>−1000)²/1000. Las sumas reproducen los estadísticos de la tabla 3.", "leyenda")
    p("En MINSTD el mayor aporte corresponde a [0.1,0.2), con 1038 datos y aporte 1.444. "
      "En glibc corresponde a [0.1,0.2), con 973 y aporte 0.729. En ZX81 corresponde a [0.3,0.4), "
      "con 947 y aporte 2.809. Ninguna de estas desviaciones, agregada con las demás, produce rechazo al nivel fijado.")

    # 8–10. Gráficas reales, una configuración por página.
    comentarios = {
        "minstd": "El histograma presenta conteos próximos a 1000. La FDE se mantiene cerca de la diagonal y "
                  "su mayor separación es D = 0.005638671, inferior al crítico. La coincidencia visual con la "
                  "uniforme es consistente con las pruebas; no demuestra independencia.",
        "glibc": "Las frecuencias varían entre 973 y 1022. La mayor distancia entre la FDE y F(u)=u es "
                 "D = 0.007133834. La tabla 4 informa ambas diferencias; la línea roja señala la distancia D. "
                 "Estos resultados corresponden a la configuración LCG de clase y a la semilla 1.",
        "zx81": "Las frecuencias varían entre 947 y 1039 y la distancia máxima es D = 0.011633098. "
                "Aunque ZX81 se identifica como deficiente en la tabla de Semana 5, estas pruebas con N = 10 000 "
                "no lo rechazan. No se fuerza un resultado distinto; el alcance de la conclusión es esta muestra.",
    }
    for indice, nombre in enumerate(ORDEN):
        informe.pagina()
        p(f"6.4.{indice+1}. Gráficas de {NOMBRES[nombre]}", "h2")
        p(comentarios[nombre])
        informe.figura(RESULTADOS / "python" / nombre / "histograma.png",
                       f"Figura {2*indice+1}. {NOMBRES[nombre]}: frecuencias observadas frente a E<sub>i</sub> = N/10. "
                       "Gráfica real exportada por la implementación Python.", alto=215)
        informe.figura(RESULTADOS / "python" / nombre / "acumulada.png",
                       f"Figura {2*indice+2}. {NOMBRES[nombre]}: FDE de los 10 000 datos frente a F(u)=u, "
                       "con la distancia máxima D. Se representa la secuencia completa ordenada.", alto=265)
        p("Java también conserva histograma.png y acumulada.png en su carpeta de resultados. "
          "Los cálculos usados en ambas representaciones se contrastaron antes de elaborar las tablas.", "leyenda")

    # 11. Evidencia de ambos lenguajes en gráficas de pares.
    informe.pagina()
    p("6.5. Inspección visual de pares consecutivos", "h2")
    p("Se muestran los primeros 4000 pares (U<sub>n</sub>, U<sub>n+1</sub>) en Python y Java. "
      "Las escalas y estilos gráficos difieren; los datos de las secuencias coinciden. Esta inspección "
      "complementa las pruebas marginales y no se presenta como una prueba serial formal.")
    for indice, nombre in enumerate(ORDEN):
        imagenes = [informe.imagen(RESULTADOS / lenguaje / nombre / "pares.png", ANCHO/2-8, 145)
                    for lenguaje in ("python", "java")]
        columnas = Table([imagenes], colWidths=[ANCHO/2, ANCHO/2])
        columnas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                     ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        informe.contenido.append(KeepTogether([
            Paragraph(f"{NOMBRES[nombre]} — Python (izquierda) y Java (derecha)", informe.estilos["h2"]),
            columnas,
            Paragraph(f"Figura {7+indice}. Archivos pares.png generados independientemente por ambos programas.",
                      informe.estilos["leyenda"]),
        ]))
    p("Que una nube parezca uniforme no descarta estructuras en otras dimensiones o retardos. "
      "No se ejecutaron poker, una prueba serial formal, Diehard ni TestU01.", "leyenda")

    # 12. Tabla solicitada y análisis del rendimiento.
    informe.pagina()
    p("6.6. Estimación de π, error y tiempos de ejecución", "h2")
    p("La tabla reproduce los cuatro tamaños de la guía para las tres configuraciones. Las estimaciones y "
      "los conteos interiores coinciden entre lenguajes; por eso se muestra una columna de π. Los tiempos "
      "son las medianas de cinco mediciones y corresponden a los archivos benchmark.csv conservados.")
    tabla(["Generador", "N puntos", "π estimado", "Error absoluto", "Python (s)", "Java (s)"], [
        [NOMBRES[n], entero(t), decimal(pi[n, t]["pi_estimado"], 8), decimal(pi[n, t]["error_absoluto"], 8),
         decimal(pi[n, t]["tiempo_python_s"], 6), decimal(pi[n, t]["tiempo_java_s"], 6)]
        for n in ORDEN for t in TAMANOS
    ], [73, 70, 87, 92, 83, ANCHO - 405])
    p("Tabla 8. Error = |π estimado−π|; tiempos en segundos, redondeados para lectura. N puntos "
      "consumen 2N uniformes. Los CSV conservan los valores completos y tiempos.csv las 120 mediciones individuales.", "leyenda")
    informe.figura(temporal / "comparacion_rendimiento.png",
                   "Figura 10. Error absoluto y medianas de tiempo de los mismos datos de la tabla 8. "
                   "Ambos ejes usan escalas logarítmicas.", alto=185)
    ratios = {n: pi[n, 1000000]["tiempo_python_s"] / pi[n, 1000000]["tiempo_java_s"] for n in ORDEN}
    p("Con un millón de puntos, glibc obtuvo el menor error observado (0.00034335), seguido de MINSTD "
      "(0.00163135) y ZX81 (0.01859665). El error no disminuye monótonamente: en glibc aumenta "
      "de N = 10 000 a 100 000, y en MINSTD de 100 000 a 1 000 000. Una única secuencia no establece una clasificación universal.")
    p(f"Para N = 1 000 000, las razones tiempo Python / tiempo Java fueron {ratios['minstd']:.2f} en MINSTD, "
      f"{ratios['glibc']:.2f} en glibc y {ratios['zx81']:.2f} en ZX81. Java fue más rápido en estas mediciones. "
      "La conclusión se limita a estas implementaciones, relojes y entorno; no es una comparación universal de lenguajes.")

    # 13. Verificación documentada.
    informe.pagina()
    p("6.7. Verificación computacional y trazabilidad", "h2")
    p("La verificación existente del proyecto registra las siguientes pruebas. Los extractos inferiores son "
      "texto de los registros reales, no capturas de una interfaz ni resultados de pruebas añadidas para este informe.")
    tabla(["Suite", "Ejecutadas", "Fallos", "Errores", "Omitidas"], [
        ["Python / pytest", "32", "0", "0", "0"], ["Java / Maven y JUnit", "19", "0", "0", "0"],
    ], [183, 83, 73, 73, ANCHO - 412])
    p("Tabla 9. Evidencia: resultados/revision/pytest.log y maven.log. Maven también registra BUILD SUCCESS.", "leyenda")
    informe.codigo(registros["pytest"])
    informe.codigo(registros["maven"])
    p("Las pruebas incluyen vectores LCG conocidos, ciclos pequeños calculables a mano, límites de intervalos, "
      "datos inválidos, referencias de SciPy, rachas, estimación de π y una integración Python/Java con parámetros "
      "de 48 bits. La integración altera deliberadamente un estado de una copia temporal para comprobar que la "
      "comparación detecta la discrepancia. Esto no modifica las secuencias entregadas.")
    p("Antes de generar este PDF se repitió la comparación de las secuencias existentes en una carpeta temporal. "
      "También se exigieron explícitamente N = 10 000 y α = 0.05, las tres configuraciones y los cuatro tamaños "
      "de benchmark. Se comprobaron las frecuencias exportadas, la longitud de las tablas KS y las medianas y "
      "mínimos frente a las cinco mediciones individuales de cada caso.")
    tabla(["Evidencia comprobada", "Resultado"], [
        ["Secuencias Python frente a Java", "30 000 pares de estados y valores normalizados iguales"],
        ["Pruebas estadísticas", "Nueve resultados por lenguaje; decisiones coincidentes"],
        ["Tabla de π", "12 estimaciones y conteos interiores coincidentes"],
        ["Tiempos individuales", "60 por lenguaje; 120 en total; medianas y mínimos coherentes"],
        ["Artefactos gráficos de cada programa", "18 PNG: histograma, acumulada y pares por configuración y lenguaje"],
    ], [199, ANCHO - 199])
    p("Tabla 10. La coincidencia entre implementaciones acredita reproducción del cálculo, no azar verdadero "
      "ni independencia completa. La instalación en un equipo diferente no se presenta como verificada.", "leyenda")

    # 14. Preguntas y conclusiones específicas de esta ejecución.
    informe.pagina()
    p("7. Preguntas de Control", "h1")
    preguntas = (
        ("¿Qué es la hipótesis nula?", "Es la afirmación de referencia que se somete a contraste. Aquí, "
         "H<sub>0</sub> establece que la distribución de los valores es U(0,1). En rachas, la referencia es el orden "
         "aleatorio de los signos respecto a la mediana."),
        ("¿Qué representa el valor p?", "Bajo H<sub>0</sub> y los supuestos de la prueba, es la probabilidad de "
         "obtener un estadístico tan extremo o más que el observado. No es la probabilidad de que H<sub>0</sub> sea verdadera."),
        ("¿Qué significa rechazar H<sub>0</sub>?", "Significa que los datos aportan evidencia contra H<sub>0</sub> al nivel "
         "de significancia elegido. Con α = 0.05 se rechaza cuando p &lt; 0.05. Puede ocurrir un error tipo I "
         "(rechazar una H<sub>0</sub> verdadera); no rechazar una falsa es un error tipo II."),
        ("¿Qué diferencia existe entre Chi-cuadrado y KS?", "Chi-cuadrado agrupa los valores y compara "
         "frecuencias observadas y esperadas; depende de los intervalos. KS compara la FDE de los datos "
         "individuales ordenados con F(u)=u mediante la distancia máxima D."),
        ("¿Por qué una prueba estadística no demuestra que un generador sea verdaderamente aleatorio?", "El LCG "
         "es determinista y reproducible a partir de su semilla. Cada prueba detecta aspectos concretos; superar "
         "una batería limitada no descarta otros patrones. Por ejemplo, ZX81 no fue rechazado aquí, aunque su "
         "error de π con un millón de puntos fue mayor que el de las otras configuraciones."),
    )
    for i, (pregunta, respuesta) in enumerate(preguntas, 1):
        p(f"{i}. {pregunta}", "h2")
        p(respuesta)
    p("8. Conclusiones", "h1")
    conclusiones = (
        "Se implementó la misma recurrencia en Python y Java. Coincidieron exactamente los 30 000 estados "
        "y valores normalizados comparados, y las doce estimaciones de π; la ejecución es reproducible con los parámetros usados.",
        "A α = 0.05, Chi-cuadrado y KS no rechazaron uniformidad en ninguna de las tres muestras. Rachas "
        "tampoco rechazó el orden aleatorio de signos. Estas decisiones se limitan a las pruebas y N = 10 000.",
        "Con un millón de puntos, los errores absolutos de π fueron 0.00163135 (MINSTD), 0.00034335 (glibc) "
        "y 0.01859665 (ZX81). La mayor desviación de ZX81 muestra por qué superar pruebas marginales no garantiza "
        "el mismo desempeño en una aplicación. No se atribuye a una única causa sin análisis adicional.",
        "Java registró menores tiempos en la tabla conservada. La medición excluyó archivos y gráficas; "
        "las diferencias corresponden a este entorno y a estas implementaciones. El método de π, el error "
        "absoluto y el carácter asintótico de KS se declararon explícitamente para delimitar las conclusiones.",
    )
    for i, conclusion in enumerate(conclusiones, 1):
        p(f"{i}. {conclusion}")

    # 15. Bibliografía y anexos de reproducción.
    informe.pagina()
    p("9. Bibliografía y fuentes de la práctica", "h1")
    fuentes = (
        "[1] José O. Guamán Q. <i>Guía de Actividades Práctico-Experimentales Nro. 006: Validación estadística "
        "de números pseudoaleatorios mediante Chi-cuadrado y Kolmogorov-Smirnov.</i> Simulación, U2. "
        "05 y 06 de noviembre de 2026. Archivo: ape_guia simulacion semana 6.pdf; pp. 1–6.",
        "[2] Material de la asignatura. <i>Generadores pseudoaleatorios, Semana 5.</i> Archivo: simulacion "
        "Semana 5.pptx [Repaired].pdf. Se consultaron las pp. 7–10 (recurrencia y período), 13 "
        "(parámetros), 15 (pares consecutivos) y 19 (ejemplo MINSTD). Ubicación: Simulacion/Diapos.",
        "[3] Material de la asignatura. <i>Semana 6: Pruebas estadísticas de uniformidad e independencia.</i> "
        "Archivo PDF del mismo nombre. Se consultaron las pp. 6–11 (uniformidad), 13–14 (rachas), "
        "18 (ejemplo glibc) y 19–25 (interpretación y límites). Ubicación: Simulacion/Diapos.",
        "[4] Proyecto 06APE. Código Python y Java, config/generadores.csv, archivos de resultados, "
        "registros de verificación y docs/BASE_ACADEMICA.md. Fuentes directas de las cifras de este reporte.",
        "[5] Anderson Mateo Coello Jaramillo. <i>Reportes técnicos de las prácticas 001 y 002, Unidad 1.</i> "
        "Archivos APE01-CoelloAnderson-U1-Simulacion.pdf y APE02-CoelloAnderson-U1-Simulacion.pdf; "
        "y reporte APE04-CoelloAnderson-U1-Simulacion.pdf. Referencias de formato, encabezado e identificación. "
        "Sus resultados experimentales no se trasladaron al APE 06.",
    )
    for fuente in fuentes:
        p(fuente)
    p("10. Anexos y reproducción de resultados", "h1")
    p("Desde la carpeta 06APE, la preparación, ejecución completa y verificación se realizan con:")
    informe.codigo("./scripts/preparar.sh\n./scripts/ejecutar_todo.sh\n./scripts/verificar.sh")
    p("Para regenerar este informe institucional a partir de resultados ya existentes y verificados:")
    informe.codigo("python/.venv/bin/python scripts/generar_informe.py")
    tabla(["Archivo / ubicación", "Contenido"], [
        ["config/generadores.csv", "Semillas y parámetros compartidos."],
        ["resultados/{python,java}/&lt;generador&gt;/", "Secuencia completa, frecuencias, datos KS, análisis JSON y gráficas PNG."],
        ["resultados/{python,java}/benchmark.csv y tiempos.csv", "Resultados de π, medianas y mediciones individuales."],
        ["resultados/comparacion/", "Secuencias contrastadas, tabla_guia.csv y verificacion.json."],
        ["resultados/revision/", "Registros de pytest, Maven y comparación."],
    ], [235, ANCHO - 235])
    p(f"Informe elaborado el {fecha} (America/Guayaquil). Las fechas de la tabla de identificación "
      "corresponden al calendario de la práctica indicado por la guía. Regenerar el PDF no vuelve a medir "
      "los tiempos; para obtener otras mediciones se debe ejecutar nuevamente el benchmark.", "leyenda")
    informe.guardar()
    print(f"Informe generado: {SALIDA}")
    print(f"Páginas: {informe.paginas_esperadas}; 30 000 valores comparados; 12 filas de benchmark verificadas.")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="ape06-informe-") as carpeta:
        generar(Path(carpeta))
