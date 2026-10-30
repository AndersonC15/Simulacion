"""Compone el informe a partir de las evidencias de ejecución de 02APE."""
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
E = ROOT / 'informe_ape02/evidencias'
PDF = ROOT / 'APE02-CoelloAnderson-U1-Simulacion.pdf'
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
def header(c,doc):
    c.saveState()
    c.drawImage(str(E/'logo_unl.png'),54,H-73,width=147,height=54.6,mask='auto',preserveAspectRatio=True)
    c.setFont('TimesUNL',10.5)
    c.drawRightString(W-54,H-42,'FEIRNNR - Carrera de Computación')
    c.setStrokeColor(colors.HexColor('#333333'))
    c.setLineWidth(.5)
    c.line(54,H-82,W-54,H-82)
    c.setFont('TimesUNL',9)
    c.drawString(54,28,'APE 02 · Simulación')
    c.drawRightString(W-54,28,str(doc.page))
    c.restoreState()

BASE=DATA['base']
def number(value):
    from decimal import Decimal
    text=format(Decimal(value),'f')
    integer,_,fraction=text.partition('.')
    fraction=fraction[:5].rstrip('0')
    return integer+('.'+fraction if fraction else '')

# 1. Identificación y objetivos.
add('Reporte Técnico de Actividades<br/>Práctico-Experimentales Nro. 002','title')
heading('1. Datos de Identificación del Estudiante y la Práctica')
identificacion=[
    ('Nombre del estudiante','Anderson Mateo Coello Jaramillo'),('Asignatura','Simulación'),('Ciclo','5'),
    ('Unidad','U1: Introducción a la Simulación'),
    ('Resultado de aprendizaje de la unidad','R1. Aplica análisis estadísticos de los datos de la Simulación para mejorar la calidad de los resultados, bajo los principios de solidaridad, transparencia, responsabilidad y honestidad.'),
    ('Práctica Nro.','002'),('Título de la Práctica','Comparación de modelos determinísticos, estocásticos, discretos y continuos'),
    ('Nombre del Docente','José O. Guamán Q.'),('Fecha','22 de Octubre de 2026<br/>23 de Octubre 2026'),
    ('Horario','Jueves 10h30 a 11h30<br/>Viernes 07h30 a 09h30'),('Lugar','Aula'),('Tiempo planificado en el Sílabo','3 horas')]
table([['<b>'+a+'</b>',b] for a,b in identificacion],[186,WIDTH-186],header=False,padding=3.6)
heading('2. Objetivo(s) de la Práctica')
add('Diferenciar los principales paradigmas de simulación mediante la construcción de modelos computacionales.')
add('1. Implementar un modelo determinístico y uno estocástico.<br/>2. Comparar modelos discretos y continuos.<br/>3. Analizar el efecto de la aleatoriedad sobre los resultados.')

# 2. Herramientas, cuatro formulaciones y organización del proyecto.
page()
heading('3. Materiales y reactivos')
add('Python 3.14.4, NumPy 2.5.4 y Matplotlib 3.11.2, disponibles en el entorno <i>.venv-ape02</i>. Se utilizó pytest 9.1.1 para ejecutar las pruebas existentes. El código representa las poblaciones con <i>Decimal</i>; NumPy aporta el generador de ruido normal.')
heading('4. Equipos y herramientas')
add('Computador con sistema operativo Linux, terminal y editor de código. La guía establece como requisitos mínimos 4 GB de RAM y un procesador de doble núcleo; la conexión a Internet se requiere al instalar herramientas. La ejecución se realizó con las dependencias ya instaladas.')
heading('5. Procedimiento / Metodología Ejecutada')
sub('5.1. Modelos matemáticos implementados')
add('Se estudia la evolución de una población P a partir de P₀, la tasa r y el tiempo t. Las observaciones corresponden a períodos consecutivos, sin asignarles unidades no indicadas, como días o años.')
table([['<b>Modelo</b>','<b>Ecuación y funcionamiento</b>'],
       ['Determinístico exponencial','P(t) = P₀e<super>rt</super>. Cada valor se calcula desde la condición inicial. No utiliza ruido.'],
       ['Discreto','P<sub>k+1</sub> = P<sub>k</sub> + rP<sub>k</sub>. Actualiza la población una vez por período.'],
       ['Estocástico','P<sub>k+1</sub> = max(0, P<sub>k</sub> + rP<sub>k</sub> + ε<sub>k</sub>), con ε<sub>k</sub> ~ N(0, σ<super>2</super>). El recorte a cero sigue el pseudocódigo de la guía.'],
       ['Continuo mediante Euler','La ecuación es dP/dt = rP. Euler la aproxima mediante P(t+h) = P(t) + hrP(t), con h = dt salvo un posible último paso reducido.']],
       [116,WIDTH-116],padding=5)
add('Estas categorías no son excluyentes: el discreto también es determinístico y el estocástico avanza por períodos. La ecuación diferencial es continua, pero Euler la resuelve con pasos discretos. La exponencial se evalúa en una malla para representarla gráficamente.')
sub('5.2. Organización y secuencia de ejecución')
add('<i>Modelo/</i> contiene observaciones, parámetros, ecuaciones y análisis de ruido. <i>Controlador/simulacion.py</i> coordina los experimentos. La consola está en <i>main.py</i>; <i>Vista/graficas.py</i> guarda PNG y CSV. Las cuatro estrategias comparten la operación <i>simular(parametros)</i>.')
add('Se verificaron los datos, se ejecutó la comparación inicial, se generaron los tres escenarios predefinidos y se realizó el análisis de ruido. Las gráficas y los CSV de este informe se generaron nuevamente en <i>informe_ape02/evidencias/salidas/</i>.')

# 3. Estimaciones y evidencia actual de verificación.
page()
sub('5.3. Datos de entrada y parámetros de la comparación inicial')
add('Se utilizó exactamente el arreglo de la guía:<br/><b>[1000, 1100, 1250, 1400, 1600, 1850, 2100]</b>, asociado a los tiempos 0, 1, 2, 3, 4, 5 y 6. P₀ = 1000 y el horizonte es 6 períodos.')
rows=[['<b>Parámetro</b>','<b>Valor presentado</b>','<b>Origen o función</b>']]
params=BASE['parametros']
for key,label,meaning in [('p0','P₀','Primera observación.'),('tasa','r','Promedio de las seis variaciones relativas.'),
                           ('sigma','σ','Desviación poblacional de los residuos.'),('dt','dt','Paso de la malla exponencial y de Euler.'),
                           ('horizonte','Horizonte','Último período de las observaciones.'),('semilla','Semilla','Generador local NumPy: 42.'),
                           ('precision','Precisión','50 dígitos para las aproximaciones.')]:
    rows.append([label,number(params[key]),meaning])
table(rows,[80,110,WIDTH-190],padding=4)
add('La consola trunca a un máximo de cinco decimales, sin redondear; el informe conserva esa presentación. Los cálculos y CSV retienen los valores internos. En particular, r ≈ 0.1317676524 y σ ≈ 22.3680456170.','small')
add('Para cada par de observaciones se calcula g<sub>i</sub> = (D<sub>i+1</sub> − D<sub>i</sub>)/D<sub>i</sub>; r es el promedio de esos seis valores. Luego se forman los residuos e<sub>i</sub> = D<sub>i+1</sub> − (1+r)D<sub>i</sub>, y σ es su desviación estándar centrada con divisor 6. Son estimaciones descriptivas; no prueban que los residuos sigan una distribución normal.')
sub('5.4. Verificación y validación computacional')
add('Las <b>353 pruebas existentes aprobaron sin fallos, errores ni omisiones</b>. También se verificaron los cuatro modelos punto por punto con referencias racionales y exponenciales de mayor precisión; se contrastaron las estimaciones y los cuatro CSV generados, cada uno con 144 filas incluyendo el encabezado. La compilación y <i>pip check</i> terminaron con código 0.')
figure(E/'pruebas_captura.png','Figura 1. Captura real de pytest: 353 pruebas aprobadas y código de salida 0. El registro estructurado se conserva en pruebas.xml.',visible_height=240)
add('<b>Alcance:</b> la guía describe visualización con NetLogo mediante pyNetLogo. Esa integración no existe en <i>02APE</i>; se verificaron cálculo Python y exportación Matplotlib con Agg, sin ventanas. No se acredita una ejecución de NetLogo.','small')

# 4. Tabla con observaciones y los cuatro resultados en tiempos comunes.
page()
heading('6. Resultados Obtenidos')
sub('6.1. Comparación con los datos de la guía')
add('Todos los modelos parten de 1000. La exponencial y Euler generan 61 puntos con dt = 0.1; el discreto y el estocástico, 7 puntos. La tabla muestra sus valores en los siete tiempos enteros comunes.')
rows=[['<b>t</b>','<b>Observado</b>','<b>Exponencial</b>','<b>Discreto</b>','<b>Estocástico</b>','<b>Euler</b>']]
for row in BASE['tabla']:
    rows.append([row['tiempo'],row['observado'],*[number(v) for v in row['poblaciones'].values()]])
table(rows,[27,64,*([((WIDTH-91)/4)]*4)],style='data',padding=4.5)
figure(E/'salidas/comparacion.png','Figura 2. Gráfica comparativa generada por main.py. Las cruces negras representan las observaciones; las curvas corresponden a los modelos calculados.')
add('En t = 6, la observación es 2100. Los valores obtenidos son <b>2204.7319</b> en la exponencial, <b>2101.56904</b> en el discreto, <b>2048.82311</b> en la trayectoria estocástica con semilla 42 y <b>2193.37709</b> en Euler. Que el discreto termine más cerca del último dato no constituye por sí solo una validación predictiva.')
add('El mismo r es instantáneo en la exponencial y relativo por período en el discreto. Por ello, e<super>r</super> y 1+r producen trayectorias diferentes. Euler aproxima la solución continua con el paso configurado.')

# 5. Capturas de ejecución y comparación reproducible de ruido.
page()
sub('6.2. Evidencia de la ejecución y efecto del ruido')
figure(E/'comparacion_captura.png','Figura 3. Captura real de la comparación: datos, parámetros, extremos de las cuatro series, archivos guardados y código de salida 0.',visible_height=500)
add('El análisis existente compara <b>30 semillas compartidas, de 42 a 71</b>, por cada nivel de σ, manteniendo P₀, r y el horizonte de la configuración inicial. Se resume la dispersión de P(6).')
rows=[['<b>σ</b>','<b>Media final</b>','<b>Desviación poblacional final</b>']]
for row in DATA['ruido']:
    rows.append([number(row['sigma']),number(row['media']),number(row['desviacion'])])
table(rows,[105,140,WIDTH-245],style='data',padding=5)
figure(E/'ruido_captura.png','Figura 4. Captura real de --analizar-ruido. El programa completó los tres niveles y terminó con código 0.',visible_height=190)
add('Con σ = 0, las 30 realizaciones coinciden con el modelo discreto. Al duplicar σ de 22.36804 a 44.73609, la desviación final pasa de 90.56283 a 181.12566. En estas realizaciones no se activa el recorte a cero. Las diferencias de medias describen estas 30 semillas; no demuestran una tendencia general de crecimiento o decrecimiento causada por el ruido.')

# 6. Gráficas de crecimiento y decrecimiento exigidas por la guía.
page()
sub('6.3. Gráficas de crecimiento y decrecimiento')
add('Se ejecutaron los escenarios definidos en el proyecto. Se mantiene P₀ = 1000, horizonte = 6 y dt = 0.1; se fija σ = 0 para aislar el efecto de r.')
figure(E/'salidas/crecimiento.png','Figura 5. Crecimiento con r = 0.1 y σ = 0. Las cuatro trayectorias aumentan; estocástico y discreto coinciden.',width=450)
figure(E/'salidas/decrecimiento.png','Figura 6. Decrecimiento con r = −0.1 y σ = 0. Las cuatro trayectorias disminuyen; el paso de Euler satisface 1+dt·r ≥ 0.',width=450)
add('Las observaciones de referencia permanecen visibles en ambas gráficas. No son nuevas mediciones de los escenarios modificados. El cambio entre crecimiento y decrecimiento corresponde a la tasa elegida, manteniendo el ruido en cero.')

# 7. Comparación numérica de r e interpretación de constancia.
page()
sub('6.4. Influencia de r e interpretación matemática')
rows=[['<b>Modelo</b>','<b>r = 0.1</b>','<b>r = −0.1</b>','<b>r = 0</b>']]
scenarios=DATA['escenarios']
for i,label in enumerate(['Exponencial','Discreto','Estocástico (σ = 0)','Euler (dt = 0.1)']):
    rows.append([label,*[number(scenarios[s]['series'][i]['final']) for s in ('crecimiento','decrecimiento','constante')]])
table(rows,[148,*([(WIDTH-148)/3]*3)],style='data',padding=5)
add('La tabla compara P(6), con σ = 0 en los tres escenarios. El caso estocástico se reduce exactamente al discreto al anular el ruido.')
figure(E/'salidas/constante.png','Figura 7. Escenario constante, r = 0 y σ = 0: todas las series mantienen P(t) = 1000. Las observaciones de referencia no se modifican.')
add('Para r &gt; 0 la exponencial crece; para r &lt; 0 decrece, y para r = 0 permanece constante. La recurrencia discreta sin ruido tiene solución P<sub>k</sub> = P₀(1+r)<super>k</super>. Euler usa factores 1+hr por paso; con dt = 0.1 y seis períodos realiza 60 actualizaciones.')
add('En esta comparación, Euler se aproxima a la exponencial y el discreto cambia una vez por período. Reducir dt disminuye el error de discretización de Euler en este problema, a costa de calcular más puntos. El modelo exponencial supone r constante; estas simulaciones no incluyen capacidad de carga ni restricciones de recursos.')

# 8 y 9. Las diez preguntas de APE02, respondidas sobre la implementación real.
page()
heading('7. Preguntas de Control')
sub('1. ¿Qué representa el arreglo de entrada?')
add('Representa siete observaciones de población en períodos consecutivos de 0 a 6: [1000, 1100, 1250, 1400, 1600, 1850, 2100]. El primer elemento determina P₀ y la cantidad de intervalos determina el horizonte. El controlador estima r con las variaciones relativas y σ con los residuos; las observaciones también se muestran como referencia en las gráficas.')
sub('2. ¿Cuál es la diferencia entre un modelo determinístico y uno estocástico?')
add('El determinístico obtiene el resultado a partir de sus entradas y reglas, sin sorteos. El estocástico incorpora variables aleatorias: aquí se añade ruido normal en cada período. La semilla fija reproduce la misma realización dentro del generador utilizado; cambiarla puede cambiar la trayectoria. El modelo discreto y Euler también son determinísticos en esta implementación.')
sub('3. ¿Qué efecto produce modificar la tasa r?')
add('r controla la variación proporcional de población. Con ruido cero, r = 0.1 produjo crecimiento, r = −0.1 produjo decrecimiento y r = 0 conservó la población. La tabla de escenarios muestra esos efectos en P(6). La tasa instantánea de la exponencial y la tasa relativa de la recurrencia tienen interpretaciones distintas, aunque se use el mismo número para compararlas.')
sub('4. ¿Qué representa el parámetro σ?')
add('Es la desviación estándar del ruido aditivo por período, ε ~ N(0, σ<super>2</super>). Su unidad corresponde a la población del modelo, porque el ruido se suma directamente a ella. No es la desviación de toda la serie observada: el programa lo estima a partir de los residuos respecto a la recurrencia. Si σ = 0, el modelo estocástico coincide con el discreto.')
sub('5. ¿Qué ocurre cuando aumenta el nivel de ruido?')
add('Aumenta la magnitud típica de las perturbaciones y puede aumentar la dispersión entre realizaciones. Con las 30 semillas compartidas del experimento, duplicar σ duplicó la desviación final, aproximadamente de 90.56283 a 181.12566. No implica que cada trayectoria crezca más. Si se activara el recorte de valores negativos a cero, este podría alterar la media y esa proporcionalidad.')

page()
heading('7. Preguntas de Control (continuación)')
sub('6. ¿Cuál es la diferencia entre los modelos discreto y continuo?')
add('El discreto actualiza P<sub>k</sub> una vez por período mediante una recurrencia. El continuo describe una variación instantánea con dP/dt = rP. El proyecto aproxima esta ecuación con Euler, usando pasos dt; no convierte por ello a la ecuación original en un modelo de períodos unitarios. Con dt = 0.1 obtiene 61 puntos frente a los 7 de la recurrencia.')
sub('7. ¿Qué función cumple dt?')
add('Controla el paso temporal de Euler y la malla donde se evalúa la exponencial. Un dt menor aumenta el número de puntos y mejora la aproximación de Euler para este problema. La malla incluye el horizonte y reduce el último paso si es necesario. Para evitar poblaciones negativas en Euler, cada paso h debe cumplir 1+hr ≥ 0. dt no altera la recurrencia discreta de paso unitario.')
sub('8. ¿Por qué es importante visualizar los resultados mediante gráficas?')
add('Permite observar aumentos, descensos, diferencias entre métodos y perturbaciones aleatorias durante todo el horizonte, además de contrastar las series con las observaciones. En esta práctica las gráficas incluyen título, tiempo, población, leyenda y cuadrícula. La visualización complementa las tablas y la verificación numérica; por sí sola no demuestra que el modelo prediga correctamente.')
sub('9. ¿Qué modelo presenta comportamiento aleatorio?')
add('El estocástico, porque utiliza un generador local de NumPy para obtener ε en cada período cuando σ &gt; 0. El resto de los modelos no realiza sorteos. Con σ = 0 desaparece la contribución aleatoria y la serie estocástica coincide con la discreta, como se comprobó en los tres escenarios controlados.')
sub('10. ¿Cómo cambia la simulación cuando se introduce un nuevo arreglo de datos?')
add('La opción 9 valida el arreglo y permite elegir modo automático o manual. El automático actualiza P₀, el horizonte y las estimaciones de r y σ; necesita al menos dos datos y divisores distintos de cero. El manual conserva r, σ, dt, semilla y precisión, y actualiza P₀ y horizonte. En ambos casos se invalida el experimento anterior para que la siguiente ejecución use la nueva configuración.')
heading('8. Bibliografía y fuentes de la práctica')
add('[1] José O. Guamán Q. <i>Guía de Actividades Práctico-Experimentales Nro. 002: Comparación de modelos determinísticos, estocásticos, discretos y continuos</i>. Asignatura Simulación, U1. Documento local: «ape_guia simulacion semana 2-firmado-signed.pdf».','small')
add('[2] Proyecto <i>02APE</i>: main.py; Modelo/; Controlador/simulacion.py; Vista/graficas.py; tests/. Código, CSV, PNG y registros de ejecución verificados para este informe.','small')
add('[3] <i>Reporte Técnico de Actividades Práctico-Experimentales Nro. 004</i>, «APE04-CoelloAnderson-U1-Simulacion.pdf». Referencia de presentación, identificación y fechas; sus resultados no se trasladaron a APE02.','small')

doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=98,bottomMargin=44,
                      title='APE02 - Comparación de modelos determinísticos, estocásticos, discretos y continuos',
                      author='Anderson Mateo Coello Jaramillo',subject='Informe de Simulación: modelos poblacionales y efecto de la aleatoriedad')
doc.build(story,onFirstPage=header,onLaterPages=header)
print(PDF)

