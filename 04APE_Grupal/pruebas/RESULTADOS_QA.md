# Pruebas ejecutadas

Java: 21.0.13. Casos: 195. Fallos: 0.

Cada fila es un caso ejecutado; los rechazos esperados cuentan como aprobados. Las semillas adicionales se agrupan en una prueba de propiedades.

| ID | Caso | Resultado |
|---|---|---|
| Q001 | Validacion: N cero | OK |
| Q002 | Validacion: N negativo | OK |
| Q003 | Validacion: N mayor al limite | OK |
| Q004 | Validacion: N Integer.MAX_VALUE | OK |
| Q005 | Validacion: I0 negativo | OK |
| Q006 | Validacion: I0 mayor a N | OK |
| Q007 | Validacion: beta negativa | OK |
| Q008 | Validacion: beta mayor a uno | OK |
| Q009 | Validacion: beta NaN | OK |
| Q010 | Validacion: beta infinito | OK |
| Q011 | Validacion: beta menos infinito | OK |
| Q012 | Validacion: gamma negativa | OK |
| Q013 | Validacion: gamma mayor a uno | OK |
| Q014 | Validacion: gamma NaN | OK |
| Q015 | Validacion: gamma infinito | OK |
| Q016 | Validacion: pasos negativos | OK |
| Q017 | Validacion: pasos 2001 | OK |
| Q018 | Validacion: pasos Integer.MAX_VALUE | OK |
| Q019 | Validacion: contactos negativos | OK |
| Q020 | Validacion: contactos 21 | OK |
| Q021 | Validacion: contactos Integer.MAX_VALUE | OK |
| Q022 | Validacion: Carga computacional excesiva | OK |
| Q023 | Parametros exactos de la guia | OK |
| Q024 | beta casi igual a gamma: precision sin redondear | OK |
| Q025 | gamma cero: R0 infinito explicito | OK |
| Q026 | beta y gamma cero: R0 indefinido | OK |
| Q027 | R0 incluye contactos configurados | OK |
| Q028 | Probabilidades minimas representables | OK |
| Q029 | N=1 e I0=0 | OK |
| Q030 | N=1 e I0=1 | OK |
| Q031 | CLI rechaza [--lambda, 2.9999] | OK |
| Q032 | CLI rechaza [--mu, 3] | OK |
| Q033 | CLI rechaza [--desconocido] | OK |
| Q034 | CLI rechaza [--beta] | OK |
| Q035 | CLI rechaza [--semilla] | OK |
| Q036 | CLI rechaza [--csv, ] | OK |
| Q037 | CLI rechaza [--semilla, 1.5] | OK |
| Q038 | CLI rechaza [--semilla, 9223372036854775808] | OK |
| Q039 | CLI rechaza [--poblacion, 2147483648] | OK |
| Q040 | CLI rechaza [--poblacion, 10.0] | OK |
| Q041 | CLI rechaza [--beta, NaN] | OK |
| Q042 | CLI rechaza [--gamma, Infinity] | OK |
| Q043 | CLI rechaza [--beta, 0,30] | OK |
| Q044 | CLI rechaza [--beta, 0x1.0p-1] | OK |
| Q045 | CLI rechaza [--beta, 1e999] | OK |
| Q046 | CLI rechaza [--gamma, texto] | OK |
| Q047 | CLI rechaza [--pasos,  ] | OK |
| Q048 | CLI rechaza [--beta, .3, --beta, .4] | OK |
| Q049 | CLI rechaza [--sin-netlogo, --sin-netlogo] | OK |
| Q050 | CLI rechaza [--png, grafica.png] | OK |
| Q051 | CLI rechaza [--csv, a?b.csv] | OK |
| Q052 | CLI rechaza [--infectados, -1] | OK |
| Q053 | CLI rechaza [--gamma, --pasos] | OK |
| Q054 | CLI conserva Long.MIN_VALUE | OK |
| Q055 | CLI conserva Long.MAX_VALUE | OK |
| Q056 | CLI notacion cientifica valida | OK |
| Q057 | CLI alias anterior sin grafica | OK |
| Q058 | Rutas automaticas distintas entre ejecuciones | OK |
| Q059 | Busqueda NetLogo explicita invalida controlada | OK |
| Q060 | Regresion semilla 42: final 4/0/96 y pico 49 en t20 | OK |
| Q061 | Regresion semilla 7: final 9/0/91 | OK |
| Q062 | Misma semilla repite todas las filas | OK |
| Q063 | Semillas diferentes producen trayectorias diferentes | OK |
| Q064 | 1000 semillas: conservacion y transiciones en cada paso | OK |
| Q065 | 500 escenarios aleatorios validos: no poblacion negativa | OK |
| Q066 | Cero infectados: no aparecen contagios | OK |
| Q067 | Todos infectados y gamma=1: todos recuperan | OK |
| Q068 | beta=gamma=0: poblacion estatica | OK |
| Q069 | beta=0 y gamma=1: se recuperan cinco | OK |
| Q070 | gamma=0: nadie recupera en 100 pasos | OK |
| Q071 | Contactos=0: no contagios nuevos | OK |
| Q072 | Foto del paso: recien contagiado no recupera inmediatamente | OK |
| Q073 | Horizonte cero: solo estado inicial y paso rechazado | OK |
| Q074 | No se permite avanzar despues del horizonte | OK |
| Q075 | Modelo rechaza parametros null | OK |
| Q076 | Getter no permite quitar individuos | OK |
| Q077 | Cambiar copia de individuo no altera modelo | OK |
| Q078 | Individuo rechaza estado null | OK |
| Q079 | Setter rechaza null | OK |
| Q080 | Individuo rechaza ID negativo | OK |
| Q081 | ResultadoPaso rechaza [-1, 95, 5, 0] | OK |
| Q082 | ResultadoPaso rechaza [0, -1, 5, 96] | OK |
| Q083 | ResultadoPaso rechaza [0, 95, -1, 6] | OK |
| Q084 | ResultadoPaso rechaza [0, 95, 6, -1] | OK |
| Q085 | ResultadoPaso rechaza [0, 2147483647, 2147483647, 0] | OK |
| Q086 | ResultadoPaso rechaza [0, 0, 0, 0] | OK |
| Q087 | N maximo con horizonte corto | OK |
| Q088 | 2000 pasos con N pequeno | OK |
| Q089 | Imagen rechaza tamano negativo | OK |
| Q090 | Imagen rechaza tamano gigantesco | OK |
| Q091 | Imagen sin datos no se cae | OK |
| Q092 | CSV Java rechaza: Archivo vacio | OK |
| Q093 | CSV Java rechaza: Solo encabezado | OK |
| Q094 | CSV Java rechaza: Sin encabezado | OK |
| Q095 | CSV Java rechaza: Separador punto y coma | OK |
| Q096 | CSV Java rechaza: Encabezado desordenado | OK |
| Q097 | CSV Java rechaza: Columna extra | OK |
| Q098 | CSV Java rechaza: Columna faltante | OK |
| Q099 | CSV Java rechaza: Texto en conteo | OK |
| Q100 | CSV Java rechaza: Conteo negativo | OK |
| Q101 | CSV Java rechaza: Conteo fraccionario | OK |
| Q102 | CSV Java rechaza: NaN en conteo | OK |
| Q103 | CSV Java rechaza: Infinity en conteo | OK |
| Q104 | CSV Java rechaza: Tiempo inicial uno | OK |
| Q105 | CSV Java rechaza: Tiempo con salto | OK |
| Q106 | CSV Java rechaza: Tiempo repetido | OK |
| Q107 | CSV Java rechaza: Tiempo retrocede | OK |
| Q108 | CSV Java rechaza: N cero | OK |
| Q109 | CSV Java rechaza: N mayor al limite | OK |
| Q110 | CSV Java rechaza: Poblacion cambia | OK |
| Q111 | CSV Java rechaza: Susceptibles aumentan | OK |
| Q112 | CSV Java rechaza: Recuperados disminuyen | OK |
| Q113 | CSV Java rechaza: Recuperaciones imposibles | OK |
| Q114 | CSV Java rechaza: Contagios sin infectados | OK |
| Q115 | CSV Java rechaza: R inicial distinto de cero | OK |
| Q116 | CSV Java rechaza: Fila en blanco intermedia | OK |
| Q117 | CSV Java rechaza: Celda vacia | OK |
| Q118 | CSV Java rechaza: Formula de hoja de calculo | OK |
| Q119 | CSV Java rechaza: Texto con instrucciones | OK |
| Q120 | CSV Java rechaza: Entero desbordado | OK |
| Q121 | CSV Java rechaza: Linea enorme | OK |
| Q122 | CSV Java rechaza: 2002 registros | OK |
| Q123 | CSV Java: cabecera BOM aceptada | OK |
| Q124 | CSV Java: saltos CRLF aceptados | OK |
| Q125 | CSV Java: espacios alrededor de enteros | OK |
| Q126 | CSV Java: archivo inexistente | OK |
| Q127 | CSV Java: directorio en vez de archivo | OK |
| Q128 | CSV Java: archivo mayor a 1 MiB rechazado | OK |
| Q129 | CSV Java: ruta con Unicode, espacios y comillas | OK |
| Q130 | Exportacion: CSV PNG parametros por cada ejecucion | OK |
| Q131 | No sobrescribe CSV existente | OK |
| Q132 | No sobrescribe PNG existente aunque no haya CSV | OK |
| Q133 | No sobrescribe parametros existentes | OK |
| Q134 | Extension de salida incorrecta rechazada | OK |
| Q135 | Nombre sin base rechazado | OK |
| Q136 | Padre es un archivo: error controlado | OK |
| Q137 | Fallo del exportador no deja CSV ni PNG parciales | OK |
| Q138 | Mismo controlador dos veces no duplica historial | OK |
| Q139 | CSV exportador rechaza lista vacia | OK |
| Q140 | CSV exportador rechaza transicion imposible | OK |
| Q141 | Texto para NetLogo escapa comillas y barras | OK |
| Q142 | UTF-8 corrupto se rechaza sin bloquear el lector | OK |
| Q143 | Dos ejecuciones simultaneas con igual destino: una sola gana | OK |
| Q144 | Reserva de otra ejecucion no se borra ni sobrescribe | OK |
| Q145 | Archivo final sin salto de linea se importa | OK |
| Q146 | NetLogo carga base en t=0 | OK |
| Q147 | NetLogo importa exactamente todas las filas Java | OK |
| Q148 | NetLogo avanzar dibuja el paso siguiente | OK |
| Q149 | NetLogo ver completo llega a 100 | OK |
| Q150 | NetLogo 500 avances al final no exceden horizonte | OK |
| Q151 | NetLogo reiniciar despues del final | OK |
| Q152 | NetLogo animar avanza desde inicio | OK |
| Q153 | NetLogo ver completo repetido es estable | OK |
| Q154 | NetLogo rechaza y conserva datos: Archivo vacio | OK |
| Q155 | NetLogo rechaza y conserva datos: Solo encabezado | OK |
| Q156 | NetLogo rechaza y conserva datos: Sin encabezado | OK |
| Q157 | NetLogo rechaza y conserva datos: Separador punto y coma | OK |
| Q158 | NetLogo rechaza y conserva datos: Encabezado desordenado | OK |
| Q159 | NetLogo rechaza y conserva datos: Columna extra | OK |
| Q160 | NetLogo rechaza y conserva datos: Columna faltante | OK |
| Q161 | NetLogo rechaza y conserva datos: Texto en conteo | OK |
| Q162 | NetLogo rechaza y conserva datos: Conteo negativo | OK |
| Q163 | NetLogo rechaza y conserva datos: Conteo fraccionario | OK |
| Q164 | NetLogo rechaza y conserva datos: NaN en conteo | OK |
| Q165 | NetLogo rechaza y conserva datos: Infinity en conteo | OK |
| Q166 | NetLogo rechaza y conserva datos: Tiempo inicial uno | OK |
| Q167 | NetLogo rechaza y conserva datos: Tiempo con salto | OK |
| Q168 | NetLogo rechaza y conserva datos: Tiempo repetido | OK |
| Q169 | NetLogo rechaza y conserva datos: Tiempo retrocede | OK |
| Q170 | NetLogo rechaza y conserva datos: N cero | OK |
| Q171 | NetLogo rechaza y conserva datos: N mayor al limite | OK |
| Q172 | NetLogo rechaza y conserva datos: Poblacion cambia | OK |
| Q173 | NetLogo rechaza y conserva datos: Susceptibles aumentan | OK |
| Q174 | NetLogo rechaza y conserva datos: Recuperados disminuyen | OK |
| Q175 | NetLogo rechaza y conserva datos: Recuperaciones imposibles | OK |
| Q176 | NetLogo rechaza y conserva datos: Contagios sin infectados | OK |
| Q177 | NetLogo rechaza y conserva datos: R inicial distinto de cero | OK |
| Q178 | NetLogo rechaza y conserva datos: Fila en blanco intermedia | OK |
| Q179 | NetLogo rechaza y conserva datos: Celda vacia | OK |
| Q180 | NetLogo rechaza y conserva datos: Formula de hoja de calculo | OK |
| Q181 | NetLogo rechaza y conserva datos: Texto con instrucciones | OK |
| Q182 | NetLogo rechaza y conserva datos: Entero desbordado | OK |
| Q183 | NetLogo rechaza y conserva datos: Linea enorme | OK |
| Q184 | NetLogo rechaza y conserva datos: 2002 registros | OK |
| Q185 | NetLogo acepta BOM | OK |
| Q186 | NetLogo acepta CRLF | OK |
| Q187 | NetLogo CSV faltante conserva escenario | OK |
| Q188 | NetLogo carga N y horizonte diferentes a la guia | OK |
| Q189 | NetLogo referencia con horizonte distinto no sale del arreglo | OK |
| Q190 | NetLogo quitar referencia limpia comparaciones | OK |
| Q191 | NetLogo sin datos: controles no lanzan excepcion | OK |
| Q192 | NetLogo archivo solo t0 no provoca indice negativo | OK |
| Q193 | NetLogo rutas Unicode con comillas se tratan como datos | OK |
| Q194 | NetLogo exportacion de graficas contiene todos los puntos | OK |
| Q195 | NetLogo 100 ciclos reiniciar/completo sin acumulacion | OK |
