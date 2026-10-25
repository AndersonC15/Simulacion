# Coordinación de simulaciones

`simulacion.py` define `ControladorSimulacion`. Valida datos, comienza con la
estimación del arreglo o acepta parámetros manuales, selecciona las
estrategias y agrupa las series con sus parámetros y observaciones en un
`Experimento`.

`ejecutar(nombre)` ejecuta una estrategia; sin nombre compara todas.
`experimento_actual()` devuelve el experimento conservado, o lo calcula si no
hay uno. Cambiar datos, parámetros o escenario invalida el anterior. Las
vistas reciben ese objeto: volver a graficar o enviarlo a NetLogo no debe
simular otra trayectoria estocástica silenciosamente.

Los escenarios crecimiento/decrecimiento/constante usan r=0.1/−0.1/0 y sigma=0
para comparar el efecto de la tasa sin ruido. Son decisiones de implementación,
no escenarios atribuidos a la guía. El constructor permite inyectar el conjunto
de estrategias para probar o extender la coordinación. Las ecuaciones y el
generador pertenecen al modelo; el menú y la presentación pertenecen a las vistas.

Consulta [README principal](../README.md) para uso, formato de datos y arquitectura.
