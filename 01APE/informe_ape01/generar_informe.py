"""Compone el informe a partir de las evidencias de ejecución de 01APE."""
from pathlib import Path
import json
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parent.parent
E = ROOT / 'informe_ape01/evidencias'
PDF = ROOT / 'APE01-CoelloAnderson-U1-Simulacion.pdf'
DATA = json.loads((E / 'resultados_verificados.json').read_text())
FONTDIR = Path('/usr/share/fonts/truetype/msttcorefonts')
for name, file in [('TimesUNL','Times_New_Roman.ttf'),('TimesUNL-Bold','Times_New_Roman_Bold.ttf'),
                   ('TimesUNL-Italic','Times_New_Roman_Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR / file)))
pdfmetrics.registerFontFamily('TimesUNL', normal='TimesUNL', bold='TimesUNL-Bold', italic='TimesUNL-Italic')
W, H = A4
WIDTH = W - 108
styles = {
    'body': ParagraphStyle('body',fontName='TimesUNL',fontSize=11,leading=14.1,alignment=TA_JUSTIFY,spaceAfter=7),
    'small': ParagraphStyle('small',fontName='TimesUNL',fontSize=9.4,leading=11.6,spaceAfter=5),
    'cell': ParagraphStyle('cell',fontName='TimesUNL',fontSize=10.4,leading=12.5),
    'data': ParagraphStyle('data',fontName='TimesUNL',fontSize=9,leading=11.1,alignment=TA_CENTER),
    'caption': ParagraphStyle('caption',fontName='TimesUNL-Italic',fontSize=9.4,leading=11.6,spaceBefore=4,spaceAfter=8),
    'h1': ParagraphStyle('h1',fontName='TimesUNL-Bold',fontSize=13,leading=16,spaceBefore=6,spaceAfter=9,keepWithNext=True),
    'h2': ParagraphStyle('h2',fontName='TimesUNL-Bold',fontSize=11.5,leading=14.5,spaceBefore=5,spaceAfter=7,keepWithNext=True),
    'title': ParagraphStyle('title',fontName='TimesUNL-Bold',fontSize=18,leading=21,alignment=TA_CENTER,spaceAfter=15),
    'formula': ParagraphStyle('formula',fontName='TimesUNL',fontSize=12,leading=16,alignment=TA_CENTER,spaceBefore=3,spaceAfter=9),
}
story = []
def P(text, style='body'):
    return Paragraph(text.replace('P₀', 'P<sub>0</sub>'), styles[style])
def add(text, style='body'):
    story.append(P(text,style))
def heading(text): add(text,'h1')
def sub(text): add(text,'h2')
def page(): story.append(PageBreak())
def table(rows, widths, header=True, style='cell', padding=4):
    data = [[P(str(cell), style) for cell in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='CENTER')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.45,colors.HexColor('#424242')),
              ('LEFTPADDING',(0,0),(-1,-1),padding),('RIGHTPADDING',(0,0),(-1,-1),padding),
              ('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding)]
    if header: commands += [('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee'))]
    t.setStyle(TableStyle(commands))
    story.append(t)
    story.append(Spacer(1,8))
def figure(path, caption, width=WIDTH, visible_height=None):
    with PILImage.open(path) as im:
        iw,ih=im.size
        source = str(path)
        if visible_height is not None:
            # Solo retira el margen vacío inferior; conserva la captura original.
            ih = visible_height
            source = BytesIO()
            im.crop((0,0,iw,ih)).save(source,format='PNG')
            source.seek(0)
    story.append(KeepTogether([Image(source,width=width,height=width*ih/iw),P(caption,'caption')]))
def result_table(key):
    rows=[['<b>Hora</b>','<b>Humedad<br/>(%)</b>','<b>Nubosidad<br/>(%)</b>','<b>Temp.<br/>(°C)</b>',
           '<b>H</b>','<b>N</b>','<b>Tf</b>','<b>Índice</b>','<b>Estado</b>']]
    for r in DATA[key]:
        rows.append([r['hora'],r['humedad'],r['nubosidad'],r['temperatura'],
                     f"{float(r['H']):.2f}",f"{float(r['N']):.2f}",f"{float(r['Tf']):.2f}",
                     f"{float(r['indice']):.3f}",r['estado']])
    table(rows,[40,58,62,50,45,45,45,55,WIDTH-400],style='data',padding=4)

def header(c,doc):
    c.saveState()
    c.drawImage(str(E/'logo_unl.png'),54,H-73,width=147,height=54.6,mask='auto',preserveAspectRatio=True)
    c.setFont('TimesUNL',10.5)
    c.drawRightString(W-54,H-42,'FEIRNNR - Carrera de Computación')
    c.setStrokeColor(colors.HexColor('#333333'))
    c.setLineWidth(.5)
    c.line(54,H-82,W-54,H-82)
    c.setFont('TimesUNL',9)
    c.drawString(54,28,'APE 01 · Simulación')
    c.drawRightString(W-54,28,str(doc.page))
    c.restoreState()

# 1. Datos y objetivos: información de APE01; fechas conservadas del informe de referencia.
add('Reporte Técnico de Actividades<br/>Práctico-Experimentales Nro. 001','title')
heading('1. Datos de Identificación del Estudiante y la Práctica')
identificacion=[
    ('Nombre del estudiante','Anderson Mateo Coello Jaramillo'),
    ('Asignatura','Simulación'),('Ciclo','5'),('Unidad','U1: Introducción a la Simulación'),
    ('Resultado de aprendizaje de la unidad','R1. Aplica análisis estadísticos de los datos de la Simulación para mejorar la calidad de los resultados, bajo los principios de solidaridad, transparencia, responsabilidad y honestidad.'),
    ('Práctica Nro.','001'),('Título de la Práctica','Construcción y simulación computacional de un modelo matemático'),
    ('Nombre del Docente','José O. Guamán Q.'),('Fecha','22 de Octubre de 2026<br/>23 de Octubre 2026'),
    ('Horario','Jueves 10h30 a 11h30<br/>Viernes 07h30 a 09h30'),('Lugar','Aula'),
    ('Tiempo planificado en el Sílabo','3 horas')]
table([['<b>'+a+'</b>',b] for a,b in identificacion],[186,WIDTH-186],header=False,padding=3.6)
heading('2. Objetivo(s) de la Práctica')
add('Comprender el proceso de construcción de un modelo matemático y analizar su comportamiento mediante Python.')
add('1. Identificar variables, parámetros y relaciones matemáticas de un sistema.<br/>2. Implementar un modelo matemático en Python.<br/>3. Analizar gráficamente la influencia de los parámetros.')

# 2. Formulación fiel a la guía y a las reglas del código.
page()
heading('3. Materiales y reactivos')
add('NumPy y Matplotlib, indicados en la guía. En el entorno ejecutado se dispone de NumPy 2.5.4 y Matplotlib 3.11.2; el cálculo del índice usa <i>Decimal</i> y las gráficas se generan con Matplotlib.')
heading('4. Equipos y herramientas')
add('Computador con sistema Linux, Python 3.14.4, entorno virtual del proyecto y editor de código. La guía también menciona Java; el alcance verificado corresponde al código Python disponible en <i>01APE</i>.')
heading('5. Procedimiento / Metodología Ejecutada')
sub('5.1. Definición de variables y relaciones matemáticas')
add('Se evalúa un índice de lluvia a partir de humedad, nubosidad y temperatura. Se utilizaron exclusivamente los nueve registros de la guía, entre las 06:00 y las 22:00. Aunque el enunciado menciona 24 horas, no se añadieron mediciones para los horarios ausentes.')
table([['<b>Variable</b>','<b>Definición</b>'],
       ['H','Humedad normalizada: humedad (%) / 100.'],['N','Nubosidad normalizada: nubosidad (%) / 100.'],
       ['Tf','Factor adimensional obtenido de la temperatura.'],['I','Índice adimensional para clasificar el estado de lluvia.']],
       [72,WIDTH-72],padding=3)
add('Modelo original: I = 0.50H + 0.30N + 0.20Tf','formula')
add('Los coeficientes 0.50, 0.30 y 0.20 son parámetros; las mediciones de H, N y Tf cambian con la hora. Los pesos son no negativos y suman 1.')
sub('5.2. Factor de temperatura y reglas de clasificación')
table([['<b>°C</b>','≤ 10','12','14','16','18','20','22','24','26','≥ 28'],
       ['<b>Tf</b>','1.00','0.90','0.80','0.70','0.60','0.50','0.40','0.30','0.20','0.10']],
       [WIDTH/11]*11,style='data',padding=3)
add('Para valores intermedios, el proyecto interpola linealmente: Tf = 1 − (T − 10) × 0.05, entre 10 y 28 °C. Así, Tf(15) = 0.75 y Tf(17) = 0.65. En los extremos conserva los factores de la tabla.')
table([['<b>Intervalo del índice</b>','<b>Estado</b>'],['I &lt; 0.40','Sin lluvia'],
       ['0.40 ≤ I &lt; 0.60','Baja posibilidad'],['0.60 ≤ I &lt; 0.75','Lluvia probable'],['I ≥ 0.75','Lluvia']],
       [WIDTH/2]*2,padding=3)

# 3. Implementación y verificación actual, sin reutilizar resultados históricos.
page()
sub('5.3. Implementación y ajuste del modelo')
add('La aplicación organiza sus responsabilidades mediante Modelo, Vista y Controlador (MVC):')
table([['<b>Componente</b>','<b>Función implementada</b>'],
       ['Modelo/','Carga los nueve registros, valida mediciones y pesos, normaliza, calcula Tf e I y clasifica los resultados.'],
       ['Vista/','Presenta el menú y las tablas, recibe el caso manual y genera las dos gráficas.'],
       ['Controlador/ y main.py','Conectan los componentes y coordinan las opciones 1, 2, 3, 4 y 0.']],
       [113,WIDTH-113],padding=4)
add('Se ejecutaron las opciones 1 y 2 para obtener ambas tablas, la opción 3 para guardar las gráficas y la opción 4 con el ejemplo de la guía. La opción 0 finalizó cada sesión con código de salida 0.')
add('Modelo ajustado: I<sub>aj</sub> = 0.40H + 0.40N + 0.20Tf','formula')
add('El ajuste, ya definido en el proyecto, traslada 0.10 del peso de humedad al de nubosidad. Se conservaron las entradas y los umbrales para comparar el efecto de los parámetros. El cálculo y la clasificación utilizan <i>Decimal</i>, sin redondear el índice antes de clasificarlo.')
sub('5.4. Verificación de la implementación')
add('Se comprobaron los 18 índices y sus estados con cálculos racionales independientes. Coincidieron todos los registros. La compilación de los módulos y <i>pip check</i> terminaron con código 0; no se detectaron conflictos de dependencias.')
add('La suite existente ejecutó <b>30 pruebas, sin fallos, errores ni omisiones</b>. Cubre el modelo, entradas, coordinación MVC y gráficas; incluye 946 casos en los umbrales. Los fallos de interfaz que la suite simula no equivalen a pruebas de ventanas reales. Las gráficas de esta ejecución se generaron con Agg, sin ventanas.')
figure(E/'pruebas_captura.png','Figura 1. Captura real de la ejecución de las 30 pruebas existentes: resultado OK y código de salida 0.',visible_height=190)
add('<b>Alcance:</b> la guía solicita Java y Python. En <i>01APE</i> solo existe la implementación Python; no se acredita la entrega ni la ejecución de una versión Java.','small')

# 4. Resultados originales: tabla generada de la salida numérica comprobada.
page()
heading('6. Resultados Obtenidos')
sub('6.1. Tabla del modelo original')
add('Con los pesos 0.50, 0.30 y 0.20 se obtuvo la siguiente tabla. H, N y Tf se muestran con dos decimales, e I con tres, sin cambiar sus valores.')
result_table('original')
figure(E/'original_captura.png','Figura 2. Captura real del programa: opción 1, tabla original y finalización correcta. La entrada se redirigió desde un archivo para reproducir la sesión.')
add('El modelo clasifica <b>lluvia probable</b> a las 06:00, 08:00 y 14:00, y <b>lluvia</b> a las 16:00, 18:00, 20:00 y 22:00. A las 10:00 y 12:00 hay baja posibilidad. El mínimo es 0.470 a las 12:00 y el máximo, 0.885 a las 18:00.')

# 5. Resultados ajustados.
page()
sub('6.2. Tabla del modelo ajustado')
add('Se repitió el cálculo con 0.40H + 0.40N + 0.20Tf y las mismas nueve mediciones, sin modificar las reglas de clasificación.')
result_table('ajustado')
figure(E/'ajustado_captura.png','Figura 3. Captura real del programa: opción 2, tabla ajustada y código de salida 0.')
add('A las <b>06:00</b>, el índice baja de <b>0.605 a 0.580</b> y el estado cambia de lluvia probable a baja posibilidad. Las demás clasificaciones se conservan. El ajustado registra lluvia probable a las 08:00 y 14:00, y lluvia a las 16:00, 18:00, 20:00 y 22:00. Su mínimo es 0.440 a las 12:00 y su máximo, 0.888 a las 18:00.')

# 6. PNG originales producidos por la aplicación, sin redibujar curvas.
page()
sub('6.3. Gráficas generadas por el proyecto')
figure(ROOT/'graficas_generadas/variables_modelo.png','Figura 4. Archivo variables_modelo.png regenerado mediante la opción 3. Muestra H, N y Tf en los nueve horarios de la guía.')
figure(ROOT/'graficas_generadas/comparacion_modelos.png','Figura 5. Archivo comparacion_modelos.png regenerado mediante la opción 3. Compara ambos índices e incluye los umbrales 0.40, 0.60 y 0.75.')
add('En ambos modelos el índice aumenta de 06:00 a 08:00, disminuye hasta 12:00, aumenta hasta 18:00 y desciende hasta 22:00. Estas variaciones corresponden a los registros disponibles. Las líneas conectan mediciones; no aportan observaciones adicionales entre horarios.')
add('La humedad y la nubosidad alcanzan sus mayores valores a las 18:00 (0.92 y 0.95); junto con Tf = 0.70 producen los máximos de ambos índices. El mínimo a las 12:00 combina H = 0.60, N = 0.30 y Tf = 0.40.')

# 7. Ejemplo y efecto de parámetros, exigidos por el procedimiento y resultados.
page()
sub('6.4. Ejemplo de la guía ejecutado como caso manual')
add('Entradas: humedad = 90 %, nubosidad = 80 % y temperatura = 18 °C. La normalización produce H = 0.90 y N = 0.80; a 18 °C corresponde Tf = 0.60.')
add('I = 0.50(0.90) + 0.30(0.80) + 0.20(0.60)<br/>I = 0.45 + 0.24 + 0.12 = 0.81','formula')
figure(E/'manual_captura.png','Figura 6. Captura real de la opción 4 con el ejemplo de la guía: I = 0.81 (81 %), estado Lluvia y código de salida 0.')
sub('6.5. Interpretación matemática e influencia de los parámetros')
add('La diferencia entre las configuraciones es:','body')
add('I<sub>aj</sub> − I = 0.10(N − H)','formula')
add('Si N &lt; H, el índice ajustado disminuye; si N &gt; H, aumenta; si N = H, permanece igual. A las 06:00, 0.10(0.40 − 0.65) = −0.025 explica el cambio de estado. A las 16:00, H = N = 0.85 y ambos índices son 0.800. A las 18:00, la diferencia es 0.003, por lo que el índice pasa de 0.885 a 0.888.')
add('Se verificó la implementación y se representaron aumentos y disminuciones del índice. La guía menciona la influencia de <i>r</i>, pero ese parámetro pertenece al modelo exponencial y no interviene en la fórmula de lluvia; aquí se analizaron los pesos. Sin registros de lluvia observada no se puede afirmar que el ajuste mejore la predicción ni interpretar 81 % como una probabilidad calibrada.')

# 8. Todas las preguntas textuales de APE01 y fuentes realmente disponibles.
page()
heading('7. Preguntas de Control')
sub('1. ¿Qué es un modelo matemático?')
add('Es una representación simplificada de un sistema mediante variables, parámetros y relaciones matemáticas. Permite calcular y analizar su comportamiento bajo determinados supuestos. En esta práctica, la relación I = 0.50H + 0.30N + 0.20Tf transforma mediciones atmosféricas en un índice de lluvia.')
sub('2. ¿Cuál es la diferencia entre variable y parámetro?')
add('Una variable puede cambiar entre observaciones; un parámetro define una configuración del modelo. En este proyecto, H, N, Tf e I varían con la hora, mientras los pesos 0.50, 0.30 y 0.20 permanecen fijos en el modelo original. El experimento ajustado modifica los pesos de H y N a 0.40.')
add('Las preguntas 3, 4 y 5 de la guía se refieren al modelo exponencial. Se responden de forma conceptual; el proyecto ejecutado no implementa ese modelo.','small')
sub('3. ¿Qué representa P₀?')
add('En el modelo exponencial P(t) = P₀e<super>rt</super>, P₀ representa la cantidad o población inicial: P(0) = P₀. No es un dato de entrada del índice de lluvia.')
sub('4. ¿Qué ocurre cuando r &lt; 0?')
add('En P(t) = P₀e<super>rt</super>, si P₀ &gt; 0 y r &lt; 0, la cantidad decrece exponencialmente al aumentar el tiempo y se aproxima a cero. Esto se debe a que e<super>rt</super> disminuye para t ≥ 0. El parámetro r no modifica las tablas meteorológicas de esta práctica.')
sub('5. ¿Qué limitaciones tiene el modelo exponencial?')
add('Supone una tasa relativa r constante y un cambio proporcional a la cantidad existente. No representa por sí solo recursos limitados, saturación, cambios de la tasa, interacciones complejas ni variaciones aleatorias. Con r &gt; 0 predice crecimiento sin límite, por lo que su aplicación a sistemas reales exige justificar el intervalo y los supuestos.')
heading('8. Bibliografía y fuentes de la práctica')
add('[1] José O. Guamán Q. <i>Guía de Actividades Práctico-Experimentales Nro. 001: Construcción y simulación computacional de un modelo matemático</i>. Asignatura Simulación, U1. Documento local: «ape_guia simulacion semana 1-firmado-signed.pdf».','small')
add('[2] Proyecto <i>01APE</i>: main.py; Modelo/datos.py, modelo.py y precision.py; Vista/consola.py y graficas.py; Controlador/controlador.py; tests/. Código y resultados comprobados en la ejecución documentada.','small')
add('[3] <i>Reporte Técnico de Actividades Práctico-Experimentales Nro. 004</i>, «APE04-CoelloAnderson-U1-Simulacion.pdf». Utilizado como referencia de presentación, datos de identificación y fechas; sus resultados de simulación no se trasladaron a esta práctica.','small')

doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=98,bottomMargin=44,
                      title='APE01 - Construcción y simulación computacional de un modelo matemático',
                      author='Anderson Mateo Coello Jaramillo',subject='Informe de Simulación: índice de lluvia, modelo original y ajustado')
doc.build(story,onFirstPage=header,onLaterPages=header)
print(PDF)
