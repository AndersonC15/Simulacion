"""Informe academico generado con los resultados verificados, sin cifras prefijadas."""

from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak


PREGUNTAS = (
    ("Que es la hipotesis nula?", "Para las pruebas de uniformidad, H0 plantea que la distribucion es U(0,1). "
     "En rachas se contrasta el orden aleatorio de los signos respecto a la mediana."),
    ("Que representa el valor p?", "Bajo H0 y los supuestos de la prueba, es la probabilidad de obtener un "
     "estadistico tan extremo o mas que el observado. No es la probabilidad de que H0 sea verdadera."),
    ("Que significa rechazar H0?", "Que los datos aportan evidencia contra H0 al nivel alfa establecido. "
     "Un error tipo I es rechazar una H0 verdadera; uno tipo II es no rechazar una H0 falsa."),
    ("Que diferencia existe entre Chi-cuadrado y KS?", "Chi-cuadrado agrupa los valores en diez intervalos y "
     "compara conteos. KS usa los datos individuales ordenados y la distancia entre FDE y F(u)=u."),
    ("Por que una prueba no demuestra aleatoriedad verdadera?", "El LCG es determinista, reproducible y "
     "de estado finito. Cada prueba detecta patrones concretos; superar las pruebas no garantiza "
     "independencia completa ni elimina otros defectos. Poker, serial, Diehard y TestU01 amplian la cobertura "
     "segun las diapositivas; no se ejecutan esas baterias en esta practica."),
)

METODOLOGIA = (
    "La guia 006 solicita LCG, Chi-cuadrado, KS, dos implementaciones equivalentes y conclusiones. "
    "Las diapositivas de Semana 6 aportan rachas como complemento de independencia.",
    "LCG: X(n+1)=(a*X(n)+c) mod m; U(n+1)=X(n+1)/m en [0,1). La semilla se asigna una sola vez. "
    "El primer dato es X1, no X0. Los parametros MINSTD y glibc, incluidas sus semillas, proceden de los "
    "ejemplos de clase; los parametros de ZX81 proceden de Semana 5 y su semilla 1 es una eleccion experimental.",
    "Chi-cuadrado: diez intervalos [i/10,(i+1)/10), Ei=N/10, gl=9, T=sum((Oi-Ei)^2/Ei). "
    "Se exige Ei>=5. Se informa el valor p de cola superior y el valor critico de la distribucion chi-cuadrado.",
    "KS: ordenar una copia. D+=max(i/N-U(i)), D-=max(U(i)-(i-1)/N), D=max(D+,D-), i=1,...,N. "
    "Se usa p=Q_K(sqrt(N)*D), la distribucion limite bilateral de Kolmogorov, en ambos lenguajes. "
    "Es una aproximacion asintotica, no el p exacto de una muestra finita. El critico se obtiene de esa "
    "misma distribucion; para alfa=0.05 es aproximadamente 1.35810/sqrt(N). La diapositiva lo redondea a 1.36/sqrt(N).",
    "Rachas: clasificar sobre/bajo la mediana conservando el orden original. Se omiten los empates "
    "con la mediana y se reporta su numero. Con n1,n2>10 se calcula media=2*n1*n2/(n1+n2)+1; "
    "varianza=2*n1*n2*(2*n1*n2-n1-n2)/((n1+n2)^2*(n1+n2-1)); Z=(R-media)/sqrt(varianza). "
    "p=2*P(Normal(0,1)>=abs(Z)), sin correccion de continuidad. Si no se cumple el tamano minimo "
    "se informa No aplicable, sin inventar un valor p.",
    "Decision: si p<alfa se rechaza H0; si p>=alfa no se rechaza H0. Uniformidad e independencia "
    "son propiedades distintas. Los valores p convencionales usan los supuestos del modelo de referencia "
    "continuo e independiente: son diagnosticos de una secuencia pseudoaleatoria, no pruebas de azar verdadero.",
    "La pagina 6 de la guia incluye pi estimado y Error sin definir el procedimiento. Para completar "
    "esa tabla se adopta explicitamente Monte Carlo por cuarto de circulo: cada punto es (U(2i-1),U(2i)); "
    "se cuenta x*x+y*y<=1; pi_estimado=4*dentro/N y Error=abs(pi_estimado-pi). N significa puntos y "
    "se consumen 2N numeros del mismo LCG. Este metodo y la definicion de error son decisiones de "
    "implementacion, no formulas atribuidas a las diapositivas.",
    "Cada repeticion de Monte Carlo reinicia la misma semilla para comparar el mismo trabajo. Se "
    "realizan tres calentamientos y se mide solo generacion mas estimacion, sin consola, archivos ni graficas. "
    "Se reporta la mediana de las repeticiones y se guardan todos los tiempos. Las repeticiones son mediciones "
    "de rendimiento, no replicas estadisticas independientes. Los tiempos dependen del equipo y la JVM; "
    "no son un benchmark universal de los lenguajes.",
    "Se conservan estados enteros y valores completos en CSV. La comparacion verifica todos los "
    "estados y normalizados, la recurrencia, las frecuencias, los estadisticos, las decisiones y los resultados "
    "de pi. Estadisticos/p: tolerancia absoluta y relativa 1e-10; criticos: absoluta 1e-8. "
    "Un periodo no detectado en la muestra no se declara como periodo total. Un p mostrado como 0 puede "
    "representar subdesbordamiento numerico.",
)

FUENTES = (
    "Guia de Actividades Practico-Experimentales 006: paginas 1-6 (archivo original en 06APE).",
    "Semana 5, Generadores pseudoaleatorios: paginas 7-10 (LCG y periodo), 13 (parametros), "
    "15 (pares consecutivos) y 19 (ejemplo MINSTD, semilla 123457).",
    "Semana 6, Pruebas estadisticas de uniformidad e independencia: paginas 6-11 (hipotesis, "
    "Chi-cuadrado y KS), 13-14 (rachas), 18 (LCG glibc) y 19-25 (interpretacion y limites).",
    "Implementacion numerica KS: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstwobign.html",
    "Funciones gamma para Chi-cuadrado: https://commons.apache.org/proper/commons-math/javadocs/api-3.6.1/org/apache/commons/math3/special/Gamma.html",
    "Condicion n1,n2>10 para aproximacion de rachas: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35d.htm",
    "Decision adicional para pi, ejemplo oficial de Apache Commons RNG: "
    "https://svn.apache.org/repos/infra/websites/production/commons/content/proper/commons-rng/commons-rng-examples/commons-rng-examples-quadrature/apidocs/org/apache/commons/rng/examples/quadrature/ComputePi.html",
)


def formato(valor: float | None) -> str:
    return "N/A" if valor is None else f"{valor:.7g}"


class VistaInforme:
    def guardar(self, analisis: list[dict], benchmark: list[dict], python: Path, java: Path, salida: Path) -> None:
        fecha = datetime.now(ZoneInfo("America/Guayaquil")).strftime("%Y-%m-%d %H:%M %Z")
        filas_pruebas = [[a["parametros"]["nombre"], str(a["n"]), p["nombre"], formato(p["estadistico"]),
                          formato(p["valor_p"]), p["decision"]] for a in analisis for p in a["pruebas"]]
        filas_pi = [[b["generador"], str(b["n"]), f"{b['pi_estimado']:.8f}", f"{b['error_absoluto']:.8f}",
                     f"{b['tiempo_python_s']:.6f}", f"{b['tiempo_java_s']:.6f}"] for b in benchmark]
        conclusiones = self._conclusiones(analisis, benchmark)
        self._grafica_rendimiento(benchmark, salida)
        self._markdown(salida, fecha, analisis, filas_pruebas, filas_pi, conclusiones)
        self._pdf(salida, fecha, analisis, filas_pruebas, filas_pi, conclusiones, python, java)

    def _conclusiones(self, analisis: list[dict], benchmark: list[dict]) -> list[str]:
        conclusiones = [f"Se comprobaron exactamente {sum(a['n'] for a in analisis):,} estados y valores "
                        "normalizados entre Java y Python. Los estadisticos, decisiones y frecuencias coinciden "
                        "dentro de las tolerancias documentadas."]
        for a in analisis:
            resultados = "; ".join(f"{p['nombre']}: p={formato(p['valor_p'])}, {p['decision'].lower()}" for p in a["pruebas"])
            conclusiones.append(f"{a['parametros']['nombre'].upper()} (N={a['n']}): {resultados}. "
                                "La conclusion se limita a estas pruebas y a esta muestra.")
        if any(a["parametros"]["nombre"] == "zx81" for a in analisis):
            conclusiones.append(
                "ZX81 aparece como configuracion de mala calidad en las diapositivas. Si supera estas "
                "pruebas con la muestra usada, se reporta ese resultado: no se fuerza un rechazo. La grafica "
                "de pares y las limitaciones del LCG ayudan a discutir defectos que las pruebas marginales no cubren.")
        for nombre in sorted({b["generador"] for b in benchmark}):
            mayor = max((b for b in benchmark if b["generador"] == nombre), key=lambda b: b["n"])
            conclusiones.append(f"{nombre.upper()}, con {mayor['n']:,} puntos: pi estimado={mayor['pi_estimado']:.8f}, "
                                f"error absoluto={mayor['error_absoluto']:.8f}. Es un resultado observado, "
                                "no una garantia sobre otras muestras o aplicaciones.")
        conclusiones += [
            f"Las {len(benchmark)} estimaciones de pi y sus conteos interiores coinciden entre ambos "
            "lenguajes. El error de Monte Carlo no tiene por que disminuir monotonamente al aumentar N. "
            "Una estimacion cercana a pi no demuestra calidad general del generador.",
            "Los tiempos de la tabla son mediciones reales de esta ejecucion, en segundos. Se compara "
            "el mismo algoritmo con la misma semilla, pero las diferencias corresponden a estas "
            "implementaciones y a este entorno.",
            "No rechazar H0 no equivale a demostrar que H0 sea verdadera. Las baterias adicionales "
            "mencionadas en clase quedan como trabajo posterior; no se afirma haberlas aplicado.",
        ]
        return conclusiones

    def _grafica_rendimiento(self, benchmark: list[dict], salida: Path) -> None:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figura, ejes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
        colores = ("#24768a", "#a34a30", "#7960a5")
        for i, nombre in enumerate(sorted({b["generador"] for b in benchmark})):
            filas = sorted((b for b in benchmark if b["generador"] == nombre), key=lambda b: b["n"])
            color = colores[i % len(colores)]
            tamanos = [b["n"] for b in filas]
            ejes[0].loglog(tamanos, [b["error_absoluto"] for b in filas], "o-", color=color, label=nombre)
            ejes[1].loglog(tamanos, [b["tiempo_python_s"] for b in filas], "o-", color=color, label=f"{nombre} Python")
            ejes[1].loglog(tamanos, [b["tiempo_java_s"] for b in filas], "s--", color=color, label=f"{nombre} Java")
        ejes[0].set(title="Error observado de pi", xlabel="N puntos", ylabel="Error absoluto")
        ejes[1].set(title="Rendimiento medido", xlabel="N puntos", ylabel="Mediana (segundos)")
        for eje in ejes:
            eje.grid(alpha=.2)
            eje.legend(fontsize=8)
        figura.savefig(salida / "comparacion_rendimiento.png", dpi=160)
        plt.close(figura)

    def _markdown(self, salida, fecha, analisis, filas_pruebas, filas_pi, conclusiones):
        texto = ["# Practica 06 - Validacion estadistica de numeros pseudoaleatorios", f"Generado: {fecha}",
                 "## Objetivo", "Evaluar uniformidad con Chi-cuadrado y KS y complementar con rachas; "
                 "comparar implementaciones LCG en Python y Java y completar la tabla de pi/rendimiento.",
                 "## Metodologia", *METODOLOGIA, "## Parametros"]
        for a in analisis:
            p = a["parametros"]
            texto.append(f"- {p['nombre']}: X0={p['semilla']}, a={p['a']}, c={p['c']}, m={p['m']}. Fuente: {p['fuente']}.")
        texto += ["## Pruebas (resultados Python; Java verificado)", "\n".join([
                  "| Generador | N | Prueba | Estadistico | p | Decision |", "|---|---:|---|---:|---:|---|",
                  *("| " + " | ".join(fila) + " |" for fila in filas_pruebas)])]
        texto += ["## Tabla solicitada en la guia", "N = puntos; Error = error absoluto; tiempos = medianas en segundos.",
                  "\n".join(["| Generador | N | Pi estimado | Error | Tiempo Python | Tiempo Java |", "|---|---:|---:|---:|---:|---:|",
                             *("| " + " | ".join(fila) + " |" for fila in filas_pi)])]
        texto += ["## Conclusiones", *(f"- {c}" for c in conclusiones), "## Preguntas de control"]
        texto += [f"**{pregunta}**\n\n{respuesta}" for pregunta, respuesta in PREGUNTAS]
        texto += ["## Fuentes", *(f"- {f}" for f in FUENTES),
                  "## Evidencias", "Las secuencias comparadas completas estan en secuencia_*.csv; "
                  "cada lenguaje conserva frecuencias.csv, ks_ordenados.csv, analisis.json y tres graficas "
                  "por generador. tabla_guia.csv conserva los valores sin redondear y verificacion.json "
                  "registra el resultado de la comparacion.",
                  "![Error de pi y tiempos medidos](comparacion_rendimiento.png)"]
        (salida / "informe.md").write_text("\n\n".join(texto) + "\n", encoding="utf-8")

    def _pdf(self, salida, fecha, analisis, filas_pruebas, filas_pi, conclusiones, python, java):
        estilos = getSampleStyleSheet()
        estilos.add(ParagraphStyle("TituloPractica", parent=estilos["Title"], fontSize=21, leading=26,
                                  textColor=colors.HexColor("#184957"), alignment=TA_CENTER))
        estilos["BodyText"].fontSize = 9
        estilos["BodyText"].leading = 13
        for nombre in ("Heading1", "Heading2", "Heading3"):
            estilos[nombre].keepWithNext = True
        contenido = []

        def parrafo(texto, estilo="BodyText"):
            contenido.append(Paragraph(escape(texto), estilos[estilo]))
            if not estilo.startswith("Heading"):
                contenido.append(Spacer(1, .15*cm))

        def tabla(encabezados, filas, anchos=None):
            datos = [[Paragraph(escape(str(c)), estilos["BodyText"]) for c in fila] for fila in [encabezados, *filas]]
            t = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceef1")),
                                   ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#a9bbc1")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            contenido.extend([t, Spacer(1, .3*cm)])

        parrafo("Practica 06: Validacion estadistica de numeros pseudoaleatorios", "TituloPractica")
        parrafo("Simulacion - Quinto ciclo - Implementaciones en Python y Java")
        parrafo(f"Resultados generados: {fecha}")
        parrafo("Objetivo", "Heading2")
        parrafo("Evaluar la uniformidad de un LCG con Chi-cuadrado y KS, complementar con rachas y "
                "comparar secuencias y rendimiento entre dos implementaciones.")
        parrafo("Metodologia y decisiones de implementacion", "Heading2")
        for texto in METODOLOGIA:
            parrafo(texto)
        parrafo("Parametros y resultados descriptivos", "Heading2")
        for a in analisis:
            p, r = a["parametros"], a["resumen"]
            parrafo(f"{p['nombre'].upper()}: X0={p['semilla']}, a={p['a']}, c={p['c']}, m={p['m']}. "
                    f"Fuente: {p['fuente']}. N={a['n']}; media={r['media']:.8f}; varianza "
                    f"poblacional={r['varianza']:.8f}; distintos={r['distintos']}; periodo observado="
                    f"{r['periodo_observado'] if r['periodo_observado'] is not None else 'no detectado en la muestra'}.")
        parrafo("Pruebas estadisticas", "Heading2")
        tabla(["Generador", "N", "Prueba", "Estadistico", "p", "Decision"], filas_pruebas,
              [2*cm, 1.3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5.2*cm])
        parrafo("Se muestran resultados Python; los resultados Java fueron verificados antes de "
                "generar este informe. Los criticos y detalles completos estan en analisis.json.")
        contenido.append(PageBreak())
        parrafo("Tabla solicitada en la guia", "Heading2")
        tabla(["Generador", "N puntos", "Pi estimado", "Error absoluto", "Python (s)", "Java (s)"], filas_pi,
              [2*cm, 2*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        parrafo("N son puntos y se consumen 2N valores del LCG. Error absoluto respecto a pi; "
                "tiempos medidos en segundos, mediana de cinco repeticiones en la ejecucion predeterminada.")
        contenido.append(Image(str(salida / "comparacion_rendimiento.png"), width=17*cm, height=7*cm))
        for a in analisis:
            nombre = a["parametros"]["nombre"]
            contenido.append(PageBreak())
            parrafo(f"{nombre.upper()}: frecuencias y distribucion acumulada", "Heading1")
            chi = next(p for p in a["pruebas"] if p["nombre"] == "chi_cuadrado")
            tabla(["Intervalo", "Observada", "Esperada", "Aporte"], [
                [f"[{b['inferior']:.1f}, {b['superior']:.1f})", b["observada"], formato(b["esperada"]), formato(b["aporte"])]
                for b in chi["intervalos"]], [4*cm]*4)
            for grafica in ("histograma.png", "acumulada.png"):
                imagen = Image(str(python / nombre / grafica))
                factor = min(16*cm / imagen.imageWidth, 6.5*cm / imagen.imageHeight)
                imagen.drawWidth, imagen.drawHeight = imagen.imageWidth*factor, imagen.imageHeight*factor
                contenido.append(imagen)
            contenido.append(PageBreak())
            parrafo(f"{nombre.upper()}: inspeccion de pares consecutivos", "Heading2")
            for lenguaje, carpeta in (("Python", python), ("Java", java)):
                parrafo(lenguaje)
                imagen = Image(str(carpeta / nombre / "pares.png"))
                factor = min(16*cm / imagen.imageWidth, 9*cm / imagen.imageHeight)
                imagen.drawWidth, imagen.drawHeight = imagen.imageWidth*factor, imagen.imageHeight*factor
                contenido.append(imagen)
            parrafo("Los pares son una inspeccion visual basada en Semana 5, no una prueba serial formal.")
        contenido.append(PageBreak())
        parrafo("Conclusiones", "Heading1")
        for c in conclusiones:
            parrafo(c)
        parrafo("Preguntas de control", "Heading1")
        for pregunta, respuesta in PREGUNTAS:
            parrafo(pregunta, "Heading3")
            parrafo(respuesta)
        parrafo("Fuentes y alcance", "Heading1")
        for fuente in FUENTES:
            parrafo(fuente)

        def pie(canvas, documento):
            canvas.setFont("Helvetica", 8)
            canvas.drawString(1.6*cm, 1*cm, "APE 06 - Simulacion | Resultados reproducibles")
            canvas.drawRightString(19.4*cm, 1*cm, f"Pagina {documento.page}")

        SimpleDocTemplate(str(salida / "informe.pdf"), pagesize=(21*cm, 29.7*cm), leftMargin=1.6*cm,
                          rightMargin=1.6*cm, topMargin=1.6*cm, bottomMargin=1.8*cm,
                          title="APE 06 - Validacion estadistica LCG").build(contenido, onFirstPage=pie, onLaterPages=pie)
