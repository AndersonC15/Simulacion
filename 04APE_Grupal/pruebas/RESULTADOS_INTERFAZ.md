# Pruebas de interfaz

Swing + NetLogo 7.0.4 en pantalla virtual X11. Java 21.0.13.

| ID | Caso | Resultado |
|---|---|---|
| G01 | Ventana abre y anima automaticamente | OK |
| G02 | Sin pestanas de editor/Informacion | OK |
| G03 | Pausa conserva el paso | OK |
| G04 | Reiniciar muestra t=0 | OK |
| G05 | Un paso llega a t=1 | OK |
| G06 | Continuar avanza desde el paso pausado | OK |
| G07 | Ver completo llega al ultimo registro | OK |
| G08 | Un paso al final no excede 100 | OK |
| G09 | Continuar al final reinicia y reproduce | OK |
| G10 | Reiniciar varias veces no acumula curvas | OK |
| G11 | Velocidad minima permitida | OK |
| G12 | Velocidad maxima permitida | OK |
| G13 | Interfaz rechaza beta=2.9999 | OK |
| G14 | Interfaz rechaza gamma=3 | OK |
| G15 | Interfaz rechaza campo vacio | OK |
| G16 | Interfaz rechaza I0 mayor que N | OK |
| G17 | Interfaz rechaza NaN | OK |
| G18 | Interfaz genera escenario sin recuperacion | OK |
| G19 | Interfaz genera horizonte cero y conserva un registro | OK |
| G20 | Comparacion usa otro CSV Java con distinta semilla | OK |
| G21 | Quitar comparacion borra solo escenario B | OK |
| G22 | CSV invalido preserva vista anterior | OK |
| G23 | Parametros auxiliares corruptos no impiden visualizar CSV valido | OK |
| G24 | Archivo con contenido CSV y extension txt no rompe metadatos | OK |
| G25 | Cancelar selector de CSV conserva datos y ventana | OK |
| G26 | Redimensionar ventana mantiene componentes | OK |
| G27 | Guardar vista crea PNG valido | OK |
| G28 | Rafaga de botones durante reproduccion no rompe el visor | OK |

Casos=28. Fallos=0.
