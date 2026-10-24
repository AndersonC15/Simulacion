# Guia tecnica - MVC, POO y SOLID

Java calcula. NetLogo representa los CSV. No hay simulacion SIR independiente en NetLogo.

## Java

| Paquete | Responsabilidad |
|---|---|
| sir.model | ParametrosSIR, Estado, Individuo, ResultadoPaso y SimulacionSIR: datos y reglas |
| sir.view | VistaConsola y GraficaSIR: tabla, resumen, ventana y PNG |
| sir.controller | ControladorSIR: coordina simulacion, presentacion y exportacion |
| sir.io | ExportadorResultados y ExportadorCsv: contrato y escritura CSV |
| sir.Main | Recibe opciones y conecta los objetos |

POO: individuos y resultados son objetos, los estados son un enum y los datos se encapsulan. Clean Code: nombres concretos, metodos con responsabilidades separadas y parametros validados.

SOLID aplicado de forma sencilla: modelo, vista y exportador tienen responsabilidades distintas; el controlador recibe una interfaz pequena de exportacion. Otro exportador puede implementar ese contrato sin cambiar los contagios. No se agregan frameworks ni jerarquias artificiales.

Se conserva el nucleo del algoritmo original: un contacto por infectado y paso, elegido de toda la poblacion. Se permite repetir contactos o elegirse a si mismo; solo un susceptible puede contagiarse. Se utiliza una copia de estados al comienzo del paso. Un recien infectado actua desde el siguiente paso. No hay reinfeccion, nacimientos ni muertes.

Se registran t=0 y los 100 pasos: 101 puntos. beta=0.30 y gamma=0.10 se usan como probabilidades por contacto/paso. El tiempo se expresa en pasos, no se asumen dias. La guia permite este enfoque estocastico; no se resuelven directamente las ecuaciones diferenciales.

## NetLogo

- datos.nls: lee y valida CSV; conserva las series importadas.
- vista.nls: curvas y valores de los monitores.
- controlador.nls: acciones de carga, reproduccion y exportacion de imagen.
- modelo_sir_netlogo.nlogox: declaraciones y widgets.

La separacion MVC se adapta a procedimientos de NetLogo. La POO con clases esta en Java. NetLogo no llama a random, no crea individuos, no calcula beta/gamma ni cambia los datos importados. El indice de reproduccion solo determina que filas se ven.

El CSV de referencia es opcional y tambien procede de Java. Ambos archivos se validan antes de reemplazar los datos cargados. Si un archivo es incorrecto, se mantiene la serie anterior.
